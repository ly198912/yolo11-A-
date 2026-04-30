#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : game.py
@Desc    : DNF runtime actions with basic stuck recovery
"""
from __future__ import annotations

import time
from typing import Dict, List, Optional, Sequence, Tuple

import pydirectinput
from loguru import logger


BoxDict = Dict[str, object]


class Game:
    NO_TARGET_FALLBACK_DIRECTION = "RIGHT"
    _action_cache: Optional[str] = None
    _player: Optional[BoxDict] = None
    _pre_player: Optional[BoxDict] = None
    _index = 0
    _player_missing_count = 0
    _position_history: List[Tuple[float, float]] = []
    _stuck_count = 0
    _last_recover_time = 0.0
    _recover_step = 0
    _last_player_center: Optional[Tuple[float, float]] = None
    _room_entry_position: Optional[Tuple[float, float]] = None
    _room_entry_time = 0.0
    _flow_direction: Optional[str] = None
    _missing_player_recover_threshold = 10
    _route_search_direction: Optional[str] = None
    _route_search_phase = 0
    _route_search_start: Optional[Tuple[float, float]] = None

    def __init__(
        self,
        obj: Sequence[dict],
        width: int,
        height: int,
        direction,
        selected_door_center: Optional[Tuple[float, float]] = None,
    ):
        self._obj = obj or []
        self._width = width
        self._height = height
        self._player_xywh: Optional[List[float]] = None
        self._attack_x = 100
        self._attack_y = 100
        self._move_x = 20
        self._move_y = 20
        self._direction = direction
        self._selected_door_center = selected_door_center

    def _current_door_direction(self) -> Optional[str]:
        if isinstance(self._direction, (list, tuple)):
            if not self._direction:
                return None
            if Game._index >= len(self._direction):
                return str(self._direction[-1]).upper()
            return str(self._direction[Game._index]).upper()
        if isinstance(self._direction, str) and self._direction.strip():
            return self._direction.strip().upper()
        return None

    def _get_cls(self, cls_name: str) -> Optional[BoxDict]:
        for item in self._obj:
            if cls_name in item:
                return item[cls_name]
        return None

    def _get_clss(self, cls_name: str) -> List[BoxDict]:
        result = []
        for item in self._obj:
            if cls_name in item:
                result.append(item[cls_name])
        return result

    def _release_direction_keys(self) -> None:
        for key in ("up", "down", "left", "right"):
            pydirectinput.keyUp(key)

    def _release_cached_action(self) -> None:
        if not Game._action_cache:
            self._release_direction_keys()
            return
        for action in Game._action_cache.strip().split("_"):
            pydirectinput.keyUp(action.lower())
        self._release_direction_keys()
        Game._action_cache = None

    def _distance(self, a: Tuple[float, float], b: Tuple[float, float]) -> float:
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

    def _infer_flow_direction_from_spawn(self, player_center: Tuple[float, float]) -> Optional[str]:
        x, y = player_center
        edge_scores = {
            "LEFT": x,
            "RIGHT": self._width - x,
            "UP": y,
            "DOWN": self._height - y,
        }
        nearest_edge = min(edge_scores, key=edge_scores.get)
        opposite = {
            "LEFT": "RIGHT",
            "RIGHT": "LEFT",
            "UP": "DOWN",
            "DOWN": "UP",
        }
        if edge_scores[nearest_edge] > min(self._width, self._height) * 0.28:
            return None
        return opposite[nearest_edge]

    def _maybe_update_room_entry(self) -> None:
        if not self._player_xywh:
            return
        player_center = (self._player_xywh[0], self._player_xywh[1])
        previous = Game._last_player_center
        Game._last_player_center = player_center
        if previous is None:
            Game._room_entry_position = player_center
            Game._room_entry_time = time.time()
            Game._flow_direction = self._infer_flow_direction_from_spawn(player_center)
            return

        jump_distance = self._distance(player_center, previous)
        if jump_distance >= 150:
            Game._room_entry_position = player_center
            Game._room_entry_time = time.time()
            Game._flow_direction = self._infer_flow_direction_from_spawn(player_center)
            logger.info(
                "room transition inferred, entry={}, flow_direction={}",
                Game._room_entry_position,
                Game._flow_direction,
            )

    def _filter_backtrack_doors(self, doors: Sequence[BoxDict], direction_hint: Optional[str]) -> List[BoxDict]:
        if not doors:
            return []

        if not Game._room_entry_position:
            return list(doors)

        now = time.time()
        protect_entry = now - Game._room_entry_time <= 3.0
        if not protect_entry:
            return list(doors)

        entry = Game._room_entry_position
        entry_side = self._reverse_direction(Game._flow_direction)
        filtered: List[BoxDict] = []
        for door in doors:
            x, y, w, h = door["xywh"]
            center = (x + w / 2.0, y + h / 2.0)
            near_entry = self._distance(center, entry) <= 240
            dx = center[0] - entry[0]
            dy = center[1] - entry[1]
            if abs(dx) >= abs(dy):
                door_side = "RIGHT" if dx > 0 else "LEFT"
            else:
                door_side = "DOWN" if dy > 0 else "UP"

            if not near_entry:
                filtered.append(door)
                continue

            if entry_side and door_side == entry_side:
                logger.info("ignore backtrack door at entry side {}: {}", entry_side, center)
                continue

            reverse_hint = self._reverse_direction(direction_hint)
            if reverse_hint and door_side == reverse_hint:
                logger.info("ignore reverse door for hint {}: {}", direction_hint, center)
                continue

            filtered.append(door)

        return filtered

    def _is_entry_protected(self) -> bool:
        return bool(Game._room_entry_position) and (time.time() - Game._room_entry_time <= 3.0)

    def _should_block_backtrack_direction(self, direction: Optional[str]) -> bool:
        if not direction or not self._is_entry_protected():
            return False
        entry_side = self._reverse_direction(Game._flow_direction)
        if not entry_side:
            return False
        return direction.upper() == entry_side

    def _key_press(self, key: str) -> None:
        pydirectinput.keyDown(key)
        time.sleep(0.08)
        pydirectinput.keyUp(key)
        time.sleep(0.05)

    def _tap_direction(self, direction: str, duration: float = 0.12) -> None:
        for action in direction.strip().split("_"):
            pydirectinput.keyDown(action.lower())
        time.sleep(duration)
        for action in direction.strip().split("_"):
            pydirectinput.keyUp(action.lower())
        time.sleep(0.04)

    def _reverse_direction(self, direction: Optional[str]) -> Optional[str]:
        mapping = {
            "LEFT": "RIGHT",
            "RIGHT": "LEFT",
            "UP": "DOWN",
            "DOWN": "UP",
            "LEFT_UP": "RIGHT_DOWN",
            "LEFT_DOWN": "RIGHT_UP",
            "RIGHT_UP": "LEFT_DOWN",
            "RIGHT_DOWN": "LEFT_UP",
        }
        return mapping.get(direction or "")

    def _get_nearest(self, cls_objs: Sequence[BoxDict], direct: Optional[str] = None) -> Optional[BoxDict]:
        nearest = None
        min_distance = float("inf")

        if not self._player_xywh:
            return None

        for item in cls_objs:
            xywh = list(item["xywh"])
            obj_x = xywh[0] + xywh[2] / 2
            obj_y = xywh[1] + xywh[3] / 2
            player_x = self._player_xywh[0]
            player_y = self._player_xywh[1]
            dx = obj_x - player_x
            dy = obj_y - player_y

            if direct:
                name = direct.lower()
                if "right" in name and dx <= 0:
                    continue
                if "left" in name and dx >= 0:
                    continue
                if "up" in name and dy >= 0:
                    continue
                if "down" in name and dy <= 0:
                    continue

            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                nearest = {
                    "xywh": [obj_x, obj_y, xywh[2], xywh[3]],
                    "conf": item.get("conf", 0),
                }

        return nearest

    def _get_door_by_center(
        self,
        doors: Sequence[BoxDict],
        center: Optional[Tuple[float, float]],
        max_distance: float = 80.0,
    ) -> Optional[BoxDict]:
        if center is None:
            return None

        nearest = None
        min_distance = float("inf")
        for item in doors:
            xywh = list(item["xywh"])
            obj_x = xywh[0] + xywh[2] / 2
            obj_y = xywh[1] + xywh[3] / 2
            distance = self._distance((obj_x, obj_y), center)
            if distance < min_distance:
                min_distance = distance
                nearest = {
                    "xywh": [obj_x, obj_y, xywh[2], xywh[3]],
                    "conf": item.get("conf", 0),
                }

        if min_distance <= max_distance:
            return nearest
        return None

    def _get_direction(self, obj_box: Sequence[float]) -> Optional[str]:
        if not self._player_xywh:
            return None
        dx = obj_box[0] - self._player_xywh[0]
        dy = obj_box[1] - self._player_xywh[1]

        if abs(dx) < 1 and abs(dy) < 1:
            return None
        if abs(dy) < 20 and abs(dx) >= 1:
            return "RIGHT" if dx > 0 else "LEFT"

        if dy < 0:
            if self._player_xywh[1] - obj_box[1] < abs(dx):
                return "RIGHT_UP" if dx > 0 else "LEFT_UP"
            return "UP"
        if dy > 0:
            if dy < abs(dx):
                return "RIGHT_DOWN" if dx > 0 else "LEFT_DOWN"
            return "DOWN"
        if dx > 0:
            return "RIGHT"
        if dx < 0:
            return "LEFT"
        return None

    def _move(
        self,
        direction: str,
        is_slow: bool = False,
        _action_cache: Optional[str] = None,
        press_time: float = 0.1,
        release_time: float = 0.1,
    ) -> str:
        logger.info("current direction: {}, cached direction: {}", direction, _action_cache)
        if _action_cache and direction != _action_cache:
            for action in _action_cache.strip().split("_"):
                pydirectinput.keyUp(action.lower())

        for action in direction.strip().split("_"):
            pydirectinput.keyDown(action.lower())

        if not is_slow:
            time.sleep(press_time)
            for action in direction.strip().split("_"):
                pydirectinput.keyUp(action.lower())
            time.sleep(release_time)
            for action in direction.strip().split("_"):
                pydirectinput.keyDown(action.lower())

        return direction

    def _update_motion_state(self, expect_motion: bool, player_visible: bool) -> bool:
        if not self._player_xywh:
            return False
        if not expect_motion or not player_visible:
            Game._position_history.clear()
            Game._stuck_count = 0
            return False

        current = (self._player_xywh[0], self._player_xywh[1])
        Game._position_history.append(current)
        if len(Game._position_history) > 8:
            Game._position_history.pop(0)

        if len(Game._position_history) < 6:
            return False

        xs = [point[0] for point in Game._position_history]
        ys = [point[1] for point in Game._position_history]
        spread_x = max(xs) - min(xs)
        spread_y = max(ys) - min(ys)
        if spread_x < 18 and spread_y < 18:
            Game._stuck_count += 1
        else:
            Game._stuck_count = 0

        return Game._stuck_count >= 2

    def _recover_from_stuck(self, reason: str) -> None:
        now = time.time()
        if now - Game._last_recover_time < 1.2:
            return

        try:
            Game._last_recover_time = now
            Game._stuck_count = 0
            Game._position_history.clear()
            logger.warning("stuck recovery triggered: {}", reason)
            route_hint = self._current_door_direction()
            current_hint = Game._action_cache or route_hint or Game._flow_direction or "RIGHT"
            self._release_cached_action()
            reverse_hint = self._reverse_direction(current_hint) or "LEFT"
            pattern = Game._recover_step % 4
            Game._recover_step += 1

            if route_hint in {"LEFT", "RIGHT", "UP", "DOWN"}:
                sideways = ("UP", "DOWN") if route_hint in {"LEFT", "RIGHT"} else ("RIGHT", "LEFT")
                if pattern == 0:
                    self._tap_direction(sideways[0], 0.12)
                    self._tap_direction(route_hint, 0.14)
                elif pattern == 1:
                    self._tap_direction(sideways[1], 0.12)
                    self._tap_direction(route_hint, 0.14)
                elif pattern == 2:
                    self._tap_direction(route_hint, 0.22)
                    self._tap_direction(sideways[0], 0.1)
                else:
                    self._tap_direction(sideways[1], 0.1)
                    self._tap_direction(route_hint, 0.18)
            elif pattern == 0:
                self._tap_direction(reverse_hint, 0.18)
                self._tap_direction("DOWN", 0.12)
            elif pattern == 1:
                self._tap_direction(reverse_hint, 0.18)
                self._tap_direction("UP", 0.12)
            elif pattern == 2:
                for step in ("RIGHT", "DOWN", "LEFT", "UP"):
                    self._tap_direction(step, 0.1)
            else:
                self._tap_direction(reverse_hint, 0.22)
                self._tap_direction(current_hint if isinstance(current_hint, str) else "RIGHT", 0.1)

            Game._action_cache = None
        except Exception as exc:
            logger.exception("stuck recovery failed: {}", exc)
            self._release_cached_action()
            Game._action_cache = None

    def _recover_missing_player(self) -> None:
        if Game._player_missing_count < Game._missing_player_recover_threshold:
            return
        logger.warning("player lost for {} frames, try recovery", Game._player_missing_count)
        self._recover_from_stuck("player_missing")
        Game._player_missing_count = 0

    def _kill_monster(self, obj_box: Sequence[float]) -> None:
        if not self._player_xywh:
            return

        if abs(obj_box[0] - self._player_xywh[0]) < self._attack_x and abs(obj_box[1] - self._player_xywh[1]) < self._attack_y:
            direction = self._get_direction(obj_box)
            face = None
            if direction:
                for item in direction.split("_"):
                    if "RIGHT" in item:
                        face = "RIGHT"
                    elif "LEFT" in item:
                        face = "LEFT"
                    break

            if face:
                self._key_press(face.lower())
            self._key_press("f")
            self._release_cached_action()
            return

        direction = self._get_direction(obj_box)
        if direction:
            Game._action_cache = self._move(direction, is_slow=True, _action_cache=Game._action_cache)

    def _pick_up(self, obj_box: Sequence[float]) -> None:
        if not self._player_xywh:
            return

        target_x = obj_box[0]
        target_y = obj_box[1]
        dx = target_x - self._player_xywh[0]
        dy = target_y - self._player_xywh[1]

        if abs(dx) <= 12 and abs(dy) <= 12:
            self._release_cached_action()
            self._key_press("x")
            return

        direction = self._get_direction(obj_box)
        if direction:
            Game._action_cache = self._move(direction, is_slow=True, _action_cache=Game._action_cache)

    def _move_to_door(self, obj_box: Sequence[float]) -> None:
        direction = self._get_direction(obj_box)
        if direction:
            Game._action_cache = self._move(direction, _action_cache=Game._action_cache)

    def _reset_route_search(self) -> None:
        Game._route_search_direction = None
        Game._route_search_phase = 0
        Game._route_search_start = None

    def _fallback_up_search_move(self) -> None:
        if not self._player_xywh:
            Game._action_cache = self._move("UP", is_slow=True, _action_cache=Game._action_cache)
            return

        current = (self._player_xywh[0], self._player_xywh[1])
        if Game._route_search_direction != "UP":
            Game._route_search_direction = "UP"
            Game._route_search_phase = 0
            Game._route_search_start = current

        if Game._route_search_start is None:
            Game._route_search_start = current

        start_x, start_y = Game._route_search_start
        current_x, current_y = current
        phase = Game._route_search_phase
        amplitude = 20.0

        if phase == 0:
            command = "DOWN"
            if current_y - start_y >= amplitude:
                Game._route_search_phase = 1
                Game._route_search_start = current
                command = "RIGHT"
        elif phase == 1:
            command = "RIGHT"
            if current_x - start_x >= amplitude:
                Game._route_search_phase = 2
                Game._route_search_start = current
                command = "UP"
        elif phase == 2:
            command = "UP"
            if start_y - current_y >= amplitude:
                Game._route_search_phase = 3
                Game._route_search_start = current
                command = "RIGHT"
        else:
            command = "RIGHT"
            if current_x - start_x >= amplitude:
                Game._route_search_phase = 0
                Game._route_search_start = current
                command = "DOWN"

        logger.info(
            "up fallback sweep: phase={}, start={}, current={}, command={}",
            Game._route_search_phase,
            Game._route_search_start,
            current,
            command,
        )
        Game._action_cache = self._move(command, is_slow=True, _action_cache=Game._action_cache)

    def _fallback_route_move(self, direction: str) -> None:
        normalized = direction.upper()
        if normalized == "DOWN":
            self._reset_route_search()
            if not self._player_xywh:
                Game._action_cache = self._move("DOWN", is_slow=True, _action_cache=Game._action_cache)
                return
            player_x = self._player_xywh[0]
            if player_x > self._width * 0.62:
                normalized = "LEFT_DOWN"
            elif player_x < self._width * 0.38:
                normalized = "RIGHT_DOWN"
        elif normalized == "UP":
            self._fallback_up_search_move()
            return
        elif normalized in {"LEFT", "RIGHT"}:
            self._reset_route_search()
            if self._player_xywh:
                player_y = self._player_xywh[1]
                if player_y > self._height * 0.68:
                    normalized = f"{normalized}_UP"
                elif player_y < self._height * 0.36:
                    normalized = f"{normalized}_DOWN"
        else:
            self._reset_route_search()

        Game._action_cache = self._move(normalized, is_slow=True, _action_cache=Game._action_cache)

    def _check_position(self) -> str:
        if not self._player_xywh:
            return "RIGHT_DOWN"
        player_x = self._player_xywh[0]
        player_y = self._player_xywh[1]

        if player_x < self._width / 2:
            return "LEFT_UP" if player_y < self._height / 2 else "LEFT_DOWN"
        return "RIGHT_UP" if player_y < self._height / 2 else "RIGHT_DOWN"

    def _would_push_outside(self, direction: Optional[str]) -> bool:
        if not direction or not self._player_xywh:
            return False
        direction = direction.upper()
        player_x = self._player_xywh[0]
        player_y = self._player_xywh[1]
        if direction == "LEFT":
            return player_x < self._width * 0.12
        if direction == "RIGHT":
            return player_x > self._width * 0.88
        if direction == "UP":
            return player_y < self._height * 0.18
        if direction == "DOWN":
            return player_y > self._height * 0.86
        return False

    def run(self) -> None:
        raw_player = self._get_cls("player")
        if raw_player is None:
            Game._player_missing_count += 1
            Game._player = Game._pre_player
        else:
            Game._player_missing_count = 0
            Game._player = raw_player
            Game._pre_player = raw_player

        if raw_player is None and Game._player_missing_count >= Game._missing_player_recover_threshold:
            self._recover_missing_player()
            return

        if Game._player is None:
            return

        try:
            self._player_xywh = list(Game._player["xywh"])
            self._player_xywh[0] = self._player_xywh[0] + self._player_xywh[2] / 2
            self._player_xywh[1] = self._player_xywh[1] + self._player_xywh[3] / 2
            logger.info("player center: {}", self._player_xywh[:2])
            self._maybe_update_room_entry()

            if self._update_motion_state(
                expect_motion=Game._action_cache is not None,
                player_visible=raw_player is not None,
            ):
                self._recover_from_stuck("movement_stalled")
                return

            boss = self._get_clss("boss")
            if boss:
                nearest_boss = self._get_nearest(boss)
                if nearest_boss:
                    self._kill_monster(nearest_boss["xywh"])
                    return

            monsters = self._get_clss("monster")
            if monsters:
                nearest_monster = self._get_nearest(monsters)
                if nearest_monster:
                    self._kill_monster(nearest_monster["xywh"])
                    return

            goods = self._get_clss("goods")
            if goods:
                nearest_goods = self._get_nearest(goods)
                if nearest_goods:
                    self._pick_up(nearest_goods["xywh"])
                    return

            money = self._get_clss("money")
            if money:
                nearest_money = self._get_nearest(money)
                if nearest_money:
                    self._pick_up(nearest_money["xywh"])
                    return

            doors = self._get_clss("door")
            if doors:
                direction_hint = self._current_door_direction()
                if isinstance(self._direction, (list, tuple)) and Game._index > 0:
                    position = self._check_position()
                    for item in position.split("_"):
                        if direction_hint == item:
                            Game._index += 1
                            direction_hint = self._current_door_direction()

                usable_doors = self._filter_backtrack_doors(doors, direction_hint)
                nearest_door = self._get_door_by_center(usable_doors, self._selected_door_center)
                if nearest_door is not None:
                    logger.info("use route-selected door: {}", self._selected_door_center)
                if nearest_door is None:
                    nearest_door = self._get_nearest(usable_doors, direct=direction_hint) if direction_hint else None
                if nearest_door is None and direction_hint:
                    if self._would_push_outside(direction_hint) and usable_doors:
                        logger.warning("route hint {} points outside screen edge, use nearest visible door", direction_hint)
                        nearest_door = self._get_nearest(usable_doors)
                    else:
                        logger.info("doors found but none match route hint {}, keep following hint", direction_hint)
                        raise LookupError("no door matches route hint")
                if nearest_door is None and direction_hint:
                    logger.info("doors found but none match route hint {}, keep following hint", direction_hint)
                    raise LookupError("no door matches route hint")
                if nearest_door is None and usable_doors:
                    nearest_door = self._get_nearest(usable_doors)
                if nearest_door:
                    self._move_to_door(nearest_door["xywh"])
                    return
        except LookupError:
            pass
        except Exception as exc:
            logger.exception("game loop error: {}", exc)
            self._release_cached_action()
            return

        fallback_direction = self._current_door_direction() or self.NO_TARGET_FALLBACK_DIRECTION
        if fallback_direction:
            if self._should_block_backtrack_direction(fallback_direction):
                logger.warning("fallback direction {} points to entry side, hold position", fallback_direction)
                self._release_cached_action()
                return
            logger.warning("no target found, fallback move: {}", fallback_direction)
            self._fallback_route_move(fallback_direction)
            return

        logger.warning("no target found and no route hint, hold position")
        self._release_cached_action()
