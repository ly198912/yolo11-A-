#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : game.py
@Desc    : DNF runtime actions with basic stuck recovery
"""
from __future__ import annotations

import random
import time
from typing import Dict, List, Optional, Sequence, Tuple

import pydirectinput
from loguru import logger


BoxDict = Dict[str, object]


class Game:
    _motion_active = False
    _player: Optional[BoxDict] = None
    _pre_player: Optional[BoxDict] = None
    _last_player_center: Optional[Tuple[float, float]] = None
    _room_entry_position: Optional[Tuple[float, float]] = None
    _room_entry_time = 0.0
    _entry_door_protect_seconds = 3.0
    _entry_door_radius = 220.0
    _player_missing_count = 0
    _player_missing_started_at: Optional[float] = None
    _missing_player_recovery_attempted = False
    _missing_player_recovery_attempts = 0
    _missing_player_next_recovery_at = 0.0
    _missing_player_recovery_retry_seconds = 1.0
    _missing_player_recovery_max_attempts = 3
    _position_history: List[Tuple[float, float]] = []
    _missing_player_recover_seconds = 10.0 / 15.0
    _missing_player_edge_continue_seconds = 3.0
    _transition_edge_margin = 180.0
    _right_edge_missing_started_at: Optional[float] = None
    _right_edge_recovery_attempted = False
    _right_edge_vertical_seconds = 0.35
    _cached_money_target: Optional[BoxDict] = None
    _cached_money_seen_at = 0.0
    _money_cache_seconds = 0.75
    _stuck_started_at: Optional[float] = None
    _stuck_anchor: Optional[Tuple[float, float]] = None
    _stuck_seconds = 0.6
    _stuck_pixel_threshold = 18.0
    _recovery_active = False
    _recovery_origin_x: Optional[float] = None
    _recovery_started_at: Optional[float] = None
    _recovery_right_distance = 50.0
    _recovery_max_seconds = 2.0
    _recovery_down_seconds = (0.3, 0.5)

    def __init__(
        self,
        obj: Sequence[dict],
        width: int,
        height: int,
        direction=None,
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
        self.release_all_movement_keys()

    @classmethod
    def release_all_movement_keys(cls) -> None:
        for key in ("up", "down", "left", "right"):
            try:
                try:
                    pydirectinput.keyUp(key, _pause=False)
                except TypeError:
                    pydirectinput.keyUp(key)
            except Exception as exc:
                logger.warning("failed to release movement key {}: {}", key, exc)
        cls._motion_active = False

    def _release_movement(self) -> None:
        self._release_direction_keys()
        Game._motion_active = False

    def _distance(self, a: Tuple[float, float], b: Tuple[float, float]) -> float:
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

    def _key_press(self, key: str) -> None:
        self._key_down(key)
        time.sleep(0.08)
        self._key_up(key)
        time.sleep(0.05)

    def _key_down(self, key: str) -> None:
        try:
            pydirectinput.keyDown(key, _pause=False)
        except TypeError:
            pydirectinput.keyDown(key)

    def _key_up(self, key: str) -> None:
        try:
            pydirectinput.keyUp(key, _pause=False)
        except TypeError:
            pydirectinput.keyUp(key)

    def _hold_direction(self, direction: str, seconds: float = 0.8) -> None:
        key = direction.lower()
        self._key_down(key)
        Game._motion_active = True
        try:
            time.sleep(seconds)
        finally:
            self._key_up(key)
            Game._motion_active = False

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

    def _door_center_box(self, door: BoxDict) -> BoxDict:
        xywh = list(door["xywh"])
        return {
            "xywh": [xywh[0] + xywh[2] / 2, xywh[1] + xywh[3] / 2, xywh[2], xywh[3]],
            "conf": door.get("conf", 0),
        }

    def _get_edge_door_for_route(
        self,
        doors: Sequence[BoxDict],
        direction: Optional[str],
    ) -> Optional[BoxDict]:
        if not doors or not direction:
            return None

        direction = direction.upper()
        if direction == "RIGHT":
            return self._door_center_box(max(doors, key=lambda item: list(item["xywh"])[0] + list(item["xywh"])[2] / 2))
        if direction == "LEFT":
            return self._door_center_box(min(doors, key=lambda item: list(item["xywh"])[0] + list(item["xywh"])[2] / 2))
        if direction == "DOWN":
            return self._door_center_box(max(doors, key=lambda item: list(item["xywh"])[1] + list(item["xywh"])[3] / 2))
        if direction == "UP":
            return self._door_center_box(min(doors, key=lambda item: list(item["xywh"])[1] + list(item["xywh"])[3] / 2))
        return None

    def _maybe_update_room_entry(self) -> None:
        if not self._player_xywh:
            return

        player_center = (self._player_xywh[0], self._player_xywh[1])
        previous_center = Game._last_player_center
        Game._last_player_center = player_center
        if previous_center is None:
            return

        if self._distance(player_center, previous_center) < 150:
            return

        Game._room_entry_position = player_center
        Game._room_entry_time = time.time()
        self._clear_money_target()
        logger.info("room transition detected, protect entry door near: {}", player_center)

    def _filter_backtrack_doors(self, doors: Sequence[BoxDict]) -> List[BoxDict]:
        entry_position = Game._room_entry_position
        if entry_position is None:
            return list(doors)

        if time.time() - Game._room_entry_time > Game._entry_door_protect_seconds:
            Game._room_entry_position = None
            return list(doors)

        visible_doors = []
        for door in doors:
            xywh = list(door["xywh"])
            center = (xywh[0] + xywh[2] / 2, xywh[1] + xywh[3] / 2)
            if self._distance(center, entry_position) <= Game._entry_door_radius:
                logger.info("ignore protected backtrack door: {}", center)
                continue
            visible_doors.append(door)
        return visible_doors

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
        press_time: float = 0.1,
        release_time: float = 0.1,
    ) -> None:
        logger.info("current direction: {}", direction)
        self._release_direction_keys()

        for action in direction.strip().split("_"):
            self._key_down(action.lower())
        Game._motion_active = True

        if not is_slow:
            time.sleep(press_time)
            for action in direction.strip().split("_"):
                self._key_up(action.lower())
            time.sleep(release_time)
            for action in direction.strip().split("_"):
                self._key_down(action.lower())

    def _reset_stuck_tracking(self) -> None:
        Game._position_history.clear()
        Game._stuck_started_at = None
        Game._stuck_anchor = None

    def _update_motion_state(self, expect_motion: bool, player_visible: bool) -> bool:
        if not self._player_xywh:
            return False
        if not expect_motion:
            self._reset_stuck_tracking()
            return False

        # Short detector gaps still use the last reliable player position. Without
        # this, intermittent obj=[] frames reset the 0.6s stall timer forever.
        current = (self._player_xywh[0], self._player_xywh[1])
        Game._position_history.append(current)
        if len(Game._position_history) > 8:
            Game._position_history.pop(0)

        now = time.time()
        anchor = Game._stuck_anchor
        if anchor is None or self._distance(current, anchor) >= Game._stuck_pixel_threshold:
            Game._stuck_anchor = current
            Game._stuck_started_at = now
            return False

        stuck_started_at = Game._stuck_started_at
        return stuck_started_at is not None and now - stuck_started_at >= Game._stuck_seconds

    def _start_stuck_recovery(self) -> None:
        if not self._player_xywh:
            return

        down_seconds = random.uniform(*Game._recovery_down_seconds)
        origin_x = self._player_xywh[0]
        logger.warning(
            "movement stalled for {:.1f}s, start recovery: DOWN {:.3f}s then RIGHT until {:.0f}px",
            Game._stuck_seconds,
            down_seconds,
            Game._recovery_right_distance,
        )
        self._release_movement()
        self._key_down("down")
        try:
            time.sleep(down_seconds)
        finally:
            self._key_up("down")

        Game._recovery_active = True
        Game._recovery_origin_x = origin_x
        Game._recovery_started_at = time.time()
        self._reset_stuck_tracking()
        self._move("RIGHT", is_slow=True)

    def _continue_stuck_recovery(self) -> bool:
        if not Game._recovery_active or not self._player_xywh:
            return False

        origin_x = Game._recovery_origin_x
        if origin_x is None:
            Game._recovery_active = False
            return False

        recovery_started_at = Game._recovery_started_at
        if recovery_started_at is not None and time.time() - recovery_started_at >= Game._recovery_max_seconds:
            logger.warning("stuck recovery timed out after {:.1f}s, hold position", Game._recovery_max_seconds)
            self._cancel_stuck_recovery()
            return False

        moved_right = self._player_xywh[0] - origin_x
        if moved_right >= Game._recovery_right_distance:
            logger.info("stuck recovery complete: moved RIGHT {:.1f}px", moved_right)
            Game._recovery_active = False
            Game._recovery_origin_x = None
            Game._recovery_started_at = None
            self._release_movement()
            self._reset_stuck_tracking()
            return False

        logger.info(
            "stuck recovery continue RIGHT: moved={:.1f}/{:.0f}px",
            max(0.0, moved_right),
            Game._recovery_right_distance,
        )
        self._move("RIGHT", is_slow=True)
        return True

    def _cancel_stuck_recovery(self) -> None:
        Game._recovery_active = False
        Game._recovery_origin_x = None
        Game._recovery_started_at = None
        self._reset_stuck_tracking()
        self._release_movement()

    def _restore_cached_player_center(self) -> bool:
        if Game._player is None:
            return False
        self._player_xywh = list(Game._player["xywh"])
        self._player_xywh[0] = self._player_xywh[0] + self._player_xywh[2] / 2
        self._player_xywh[1] = self._player_xywh[1] + self._player_xywh[3] / 2
        return True

    def _player_missing_seconds(self, now: Optional[float] = None) -> float:
        started_at = Game._player_missing_started_at
        if started_at is None:
            return 0.0
        return max(0.0, (time.time() if now is None else now) - started_at)

    def _reset_missing_player_recovery_tracking(self) -> None:
        Game._missing_player_recovery_attempted = False
        Game._missing_player_recovery_attempts = 0
        Game._missing_player_next_recovery_at = 0.0

    def _can_start_missing_player_recovery(self) -> bool:
        return (
            Game._missing_player_recovery_attempts < Game._missing_player_recovery_max_attempts
            and time.time() >= Game._missing_player_next_recovery_at
        )

    def _start_missing_player_recovery(self) -> None:
        Game._missing_player_recovery_attempted = True
        Game._missing_player_recovery_attempts += 1
        self._start_stuck_recovery()
        Game._missing_player_next_recovery_at = (
            time.time()
            + Game._recovery_max_seconds
            + Game._missing_player_recovery_retry_seconds
        )

    def _is_cached_player_near_route_edge(self, direction: Optional[str]) -> bool:
        if not direction or not self._restore_cached_player_center():
            return False

        player_x, player_y = self._player_xywh[:2]
        margin = Game._transition_edge_margin
        direction = direction.upper()
        if direction == "RIGHT":
            return player_x >= self._width - margin
        if direction == "LEFT":
            return player_x <= margin
        if direction == "DOWN":
            return player_y >= self._height - margin
        if direction == "UP":
            return player_y <= margin
        return False

    def _reset_right_edge_missing_tracking(self) -> None:
        Game._right_edge_missing_started_at = None
        Game._right_edge_recovery_attempted = False

    def _track_right_edge_missing(self, direction: Optional[str]) -> None:
        if direction != "RIGHT" or not self._is_cached_player_near_route_edge(direction):
            self._reset_right_edge_missing_tracking()
            return
        if Game._right_edge_missing_started_at is None:
            Game._right_edge_missing_started_at = time.time()

    def _start_right_edge_door_recovery(self, target_door: Optional[BoxDict] = None) -> None:
        logger.warning(
            "player stalled near RIGHT edge for {:.1f}s, align with doorway on Y axis",
            Game._stuck_seconds,
        )
        self._release_movement()
        self._key_down("right")
        try:
            if target_door is not None and self._player_xywh:
                door_y = list(target_door["xywh"])[1]
                dy = door_y - self._player_xywh[1]
                if abs(dy) >= self._move_y:
                    vertical_key = "down" if dy > 0 else "up"
                    press_seconds = min(0.65, max(0.12, abs(dy) / 260.0))
                    logger.info(
                        "align RIGHT edge door on Y axis: player_y={:.1f}, door_y={:.1f}, key={}, seconds={:.2f}",
                        self._player_xywh[1],
                        door_y,
                        vertical_key,
                        press_seconds,
                    )
                    self._key_down(vertical_key)
                    try:
                        time.sleep(press_seconds)
                    finally:
                        self._key_up(vertical_key)
                    return

            for vertical_key in ("up", "down"):
                self._key_down(vertical_key)
                try:
                    time.sleep(Game._right_edge_vertical_seconds)
                finally:
                    self._key_up(vertical_key)
        finally:
            Game._motion_active = True
            self._reset_stuck_tracking()

    def _try_missing_player_right_edge_recovery(self, direction: Optional[str]) -> bool:
        if direction != "RIGHT" or not self._is_cached_player_near_route_edge(direction):
            return False
        started_at = Game._right_edge_missing_started_at
        if started_at is None or time.time() - started_at < Game._stuck_seconds:
            return False
        if Game._right_edge_recovery_attempted:
            return False

        Game._right_edge_recovery_attempted = True
        target_door = self._get_edge_door_for_route(self._get_clss("door"), direction)
        self._start_right_edge_door_recovery(target_door)
        return True

    def _clear_money_target(self) -> None:
        Game._cached_money_target = None
        Game._cached_money_seen_at = 0.0

    def _get_money_target(self) -> Optional[BoxDict]:
        nearest_money = self._get_nearest(self._get_clss("money"))
        if nearest_money is not None:
            Game._cached_money_target = nearest_money
            Game._cached_money_seen_at = time.time()
            return nearest_money

        cached_money = Game._cached_money_target
        if cached_money is None:
            return None
        if time.time() - Game._cached_money_seen_at > Game._money_cache_seconds:
            self._clear_money_target()
            return None

        logger.info("reuse cached money target during detector gap")
        return cached_money

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
            self._release_movement()
            return

        direction = self._get_direction(obj_box)
        if direction:
            self._move(direction, is_slow=True)

    def _pick_up(self, obj_box: Sequence[float], clear_money_target: bool = False) -> None:
        if not self._player_xywh:
            return

        if abs(obj_box[0] - self._player_xywh[0]) < self._move_x and abs(obj_box[1] - self._player_xywh[1]) < self._move_y:
            self._key_press("x")
            if clear_money_target:
                self._clear_money_target()
            self._release_movement()
            return

        direction = self._get_direction(obj_box)
        if direction:
            self._move(direction, is_slow=True)

    def _move_to_door(self, obj_box: Sequence[float], direction_hint: str) -> None:
        vision_direction = self._get_direction(obj_box)
        if not vision_direction:
            logger.info("YOLO door reached for A* route {}, hold position", direction_hint)
            self._release_movement()
            return

        logger.info("YOLO approach door: A* route={}, vision_move={}", direction_hint, vision_direction)
        self._move(vision_direction)

    def _move_by_astar(self, direction_hint: Optional[str], reason: str) -> bool:
        if not direction_hint:
            return False

        logger.info("{}; continue A* navigation: {}", reason, direction_hint)
        self._move(direction_hint, is_slow=True)
        return True

    def run(self) -> None:
        try:
            raw_player = self._get_cls("player")
        except Exception as exc:
            logger.exception("game loop error: {}", exc)
            self._release_movement()
            return

        if raw_player is None:
            Game._player_missing_count += 1
            if Game._player_missing_started_at is None:
                Game._player_missing_started_at = time.time()
            Game._player = Game._pre_player
        else:
            Game._player_missing_count = 0
            Game._player_missing_started_at = None
            self._reset_missing_player_recovery_tracking()
            self._reset_right_edge_missing_tracking()
            Game._player = raw_player
            Game._pre_player = raw_player

        if raw_player is None:
            self._track_right_edge_missing(self._current_door_direction())

        missing_seconds = self._player_missing_seconds()
        if raw_player is None and missing_seconds >= Game._missing_player_recover_seconds:
            direction_hint = self._current_door_direction()
            if Game._player is None and direction_hint:
                logger.warning(
                    "player missing without cached center for {:.2f}s, continue A* navigation: {}",
                    missing_seconds,
                    direction_hint,
                )
                self._move_by_astar(direction_hint, "player missing without cached center")
                return
            if self._try_missing_player_right_edge_recovery(direction_hint):
                return
            edge_continue_limit = (
                Game._missing_player_recover_seconds
                + Game._missing_player_edge_continue_seconds
            )
            if (
                missing_seconds <= edge_continue_limit
                and self._is_cached_player_near_route_edge(direction_hint)
            ):
                logger.warning(
                    "player lost for {} frames ({:.2f}s) near {} edge, continue A* room transition",
                    Game._player_missing_count,
                    missing_seconds,
                    direction_hint,
                )
                self._move_by_astar(direction_hint, "player missing near route edge")
                return
            if Game._recovery_active and self._restore_cached_player_center():
                Game._missing_player_recovery_attempted = True
                if self._continue_stuck_recovery():
                    return
            if self._can_start_missing_player_recovery() and self._restore_cached_player_center():
                logger.warning(
                    "player lost for {} frames ({:.2f}s), try controlled recovery {}/{}",
                    Game._player_missing_count,
                    missing_seconds,
                    Game._missing_player_recovery_attempts + 1,
                    Game._missing_player_recovery_max_attempts,
                )
                self._start_missing_player_recovery()
                return
            logger.warning(
                "player lost for {} frames ({:.2f}s), hold position after {}/{} recovery attempts",
                Game._player_missing_count,
                missing_seconds,
                Game._missing_player_recovery_attempts,
                Game._missing_player_recovery_max_attempts,
            )
            self._cancel_stuck_recovery()
            return

        if Game._player is None:
            return

        try:
            self._restore_cached_player_center()
            logger.info("player center: {}", self._player_xywh[:2])
            self._maybe_update_room_entry()

            if self._current_door_direction() is None and not any(
                self._get_clss(name) for name in ("boss", "monster", "money", "goods", "door")
            ):
                logger.info("YOLO found no actionable target and A* has no route, hold position")
                self._cancel_stuck_recovery()
                return

            if self._continue_stuck_recovery():
                return

            if self._update_motion_state(
                expect_motion=Game._motion_active,
                player_visible=raw_player is not None,
            ):
                if (
                    self._current_door_direction() == "RIGHT"
                    and self._is_cached_player_near_route_edge("RIGHT")
                ):
                    target_door = self._get_edge_door_for_route(self._get_clss("door"), "RIGHT")
                    self._start_right_edge_door_recovery(target_door)
                    return
                self._start_stuck_recovery()
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

            nearest_money = self._get_money_target()
            if nearest_money:
                self._pick_up(nearest_money["xywh"], clear_money_target=True)
                return

            goods = self._get_clss("goods")
            if goods:
                nearest_goods = self._get_nearest(goods)
                if nearest_goods:
                    self._pick_up(nearest_goods["xywh"])
                    return

            doors = self._get_clss("door")
            if doors:
                direction_hint = self._current_door_direction()
                if not direction_hint:
                    logger.info("YOLO found doors but A* has no route, hold position")
                    self._release_movement()
                    return

                visible_doors = self._filter_backtrack_doors(doors)
                if not visible_doors:
                    if self._is_cached_player_near_route_edge(direction_hint):
                        nearest_door = self._get_edge_door_for_route(doors, direction_hint)
                        if nearest_door is not None:
                            logger.info(
                                "use protected edge door for route {}: {}",
                                direction_hint,
                                nearest_door["xywh"][:2],
                            )
                            self._move_to_door(nearest_door["xywh"], direction_hint)
                            return
                    self._move_by_astar(direction_hint, "YOLO found only protected backtrack door")
                    return

                nearest_door = self._get_door_by_center(visible_doors, self._selected_door_center)
                if nearest_door is not None:
                    logger.info("use route-selected door: {}", self._selected_door_center)
                if nearest_door is None:
                    nearest_door = self._get_nearest(visible_doors, direct=direction_hint)
                if nearest_door is None and self._is_cached_player_near_route_edge(direction_hint):
                    nearest_door = self._get_edge_door_for_route(doors, direction_hint)
                    if nearest_door is not None:
                        logger.info("use edge door for route {}: {}", direction_hint, nearest_door["xywh"][:2])
                if nearest_door:
                    self._move_to_door(nearest_door["xywh"], direction_hint)
                    return
                self._move_by_astar(direction_hint, "YOLO found no door matching A* route")
                return
        except Exception as exc:
            logger.exception("game loop error: {}", exc)
            self._release_movement()
            return

        direction_hint = self._current_door_direction()
        if self._move_by_astar(direction_hint, "YOLO found no door"):
            return

        logger.info("YOLO found no door and A* has no route, hold position")
        self._release_movement()
