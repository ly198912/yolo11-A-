#! /usr/bin/env python
"""
@File    : game.py
@Desc    : DNF runtime actions with basic stuck recovery.
"""

from __future__ import annotations

import os
import random
import time
from collections.abc import Iterable, Sequence

import pydirectinput
from loguru import logger

BoxDict = dict[str, object]


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        logger.warning("invalid float env {}={}, use {}", name, os.getenv(name), default)
        return default


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        logger.warning("invalid int env {}={}, use {}", name, os.getenv(name), default)
        return default


def _env_range(name: str, default: tuple[float, float]) -> tuple[float, float]:
    value = os.getenv(name)
    if not value:
        return default
    try:
        left, right = value.replace(",", "-").split("-", 1)
        low = float(left.strip())
        high = float(right.strip())
        if low < 0 or high < 0 or low > high:
            raise ValueError
        return low, high
    except ValueError:
        logger.warning("invalid range env {}={}, use {}", name, value, default)
        return default


def _env_key(name: str, default: str) -> str:
    value = os.getenv(name, default).strip()
    return value or default


class Game:
    NO_TARGET_FALLBACK_DIRECTION = "RIGHT"
    _action_cache: str | None = None
    _player: BoxDict | None = None
    _pre_player: BoxDict | None = None
    _index = 0
    _player_missing_count = 0
    _position_history: list[tuple[float, float]] = []
    _stuck_count = 0
    _last_recover_time = 0.0
    _recover_step = 0
    _last_player_center: tuple[float, float] | None = None
    _room_entry_position: tuple[float, float] | None = None
    _room_entry_time = 0.0
    _flow_direction: str | None = None
    _entry_door_protect_seconds = _env_float("DNF_ENTRY_DOOR_PROTECT_SECONDS", 30.0)
    _entry_door_protect_radius = _env_float("DNF_ENTRY_DOOR_PROTECT_RADIUS", 280.0)
    _missing_player_recover_threshold = _env_int("DNF_MISSING_PLAYER_RECOVER_THRESHOLD", 10)
    _route_search_direction: str | None = None
    _route_search_phase = 0
    _route_search_start: tuple[float, float] | None = None
    _route_search_x_amplitude = _env_float("DNF_ROUTE_SEARCH_X_AMPLITUDE", 32.0)
    _route_search_y_amplitude = _env_float("DNF_ROUTE_SEARCH_Y_AMPLITUDE", 6.0)
    _route_search_amplitude = _route_search_x_amplitude
    _route_search_edge_band = 0.08
    _horizontal_move_y_deadzone = _env_float("DNF_HORIZONTAL_MOVE_Y_DEADZONE", 48.0)
    _horizontal_door_align_distance = _env_float("DNF_HORIZONTAL_DOOR_ALIGN_DISTANCE", 120.0)
    _diagonal_y_ratio = _env_float("DNF_DIAGONAL_Y_RATIO", 0.35)
    _horizontal_edge_top_ratio = _env_float("DNF_HORIZONTAL_EDGE_TOP_RATIO", 0.22)
    _horizontal_edge_bottom_ratio = _env_float("DNF_HORIZONTAL_EDGE_BOTTOM_RATIO", 0.80)
    _down_stuck_anchor: tuple[float, float] | None = None
    _down_stuck_since = 0.0
    _down_right_search_until = 0.0
    _up_stuck_anchor: tuple[float, float] | None = None
    _up_stuck_since = 0.0
    _up_right_search_until = 0.0
    _vertical_escape_direction: str | None = None
    _vertical_escape_target_y: float | None = None
    _vertical_escape_source_direction: str | None = None
    _right_search_anchor_x: float | None = None
    _right_search_until = 0.0
    _right_search_until_door = False
    _active_route_direction: str | None = None
    _action_cache_time = 0.0
    _down_stuck_seconds = _env_float("DNF_VERTICAL_STUCK_SECONDS", 0.6)
    _down_stuck_move_tolerance = _env_float("DNF_VERTICAL_STUCK_MOVE_TOLERANCE", 16.0)
    _vertical_stuck_y_tolerance = _env_float("DNF_VERTICAL_STUCK_Y_TOLERANCE", 6.0)
    _down_right_search_seconds = _env_float("DNF_VERTICAL_RIGHT_SEARCH_SECONDS", 1.2)
    _vertical_edge_nudge_pixels = _env_float("DNF_VERTICAL_EDGE_NUDGE_PIXELS", 3.0)
    _right_search_pixels = _env_float("DNF_RIGHT_SEARCH_PIXELS", 40.0)
    _move_press_time = _env_float("DNF_MOVE_PRESS_TIME", 0.16)
    _move_release_time = _env_float("DNF_MOVE_RELEASE_TIME", 0.06)
    _move_reassert_seconds = _env_float("DNF_MOVE_REASSERT_SECONDS", 0.12)
    _tap_direction_seconds = _env_float("DNF_DIRECTION_TAP_SECONDS", 0.16)
    _monster_attack_range_x = _env_float("DNF_MONSTER_ATTACK_RANGE_X", 70.0)
    _monster_attack_range_y = _env_float("DNF_MONSTER_ATTACK_RANGE_Y", 55.0)
    _attack_key = _env_key("DNF_ATTACK_KEY", "x")
    _attack_cooldown_seconds = _env_float("DNF_ATTACK_COOLDOWN", 0.45)
    _last_attack_time = 0.0
    _pickup_x_deadzone = _env_float("DNF_PICKUP_X_DEADZONE", 18.0)
    _pickup_y_sweep_x_range = _env_float("DNF_PICKUP_Y_SWEEP_X_RANGE", 120.0)
    _pickup_y_deadzone = _env_float("DNF_PICKUP_Y_DEADZONE", 14.0)
    _special_attack_key = _env_key("DNF_SPECIAL_ATTACK_KEY", "q")
    _special_attack_cooldown_range = _env_range("DNF_SPECIAL_ATTACK_COOLDOWN", (8.0, 9.0))
    _next_special_attack_time = 0.0
    _extra_attack_key = _env_key("DNF_EXTRA_ATTACK_KEY", "a")
    _extra_attack_cooldown_range = _env_range("DNF_EXTRA_ATTACK_COOLDOWN", (17.0, 18.0))
    _next_extra_attack_time = 0.0

    def __init__(
        self,
        obj: Sequence[dict],
        width: int,
        height: int,
        direction,
        selected_door_center: tuple[float, float] | None = None,
        target_kind: str | None = None,
    ):
        self._obj = obj or []
        self._width = width
        self._height = height
        self._player_xywh: list[float] | None = None
        self._attack_x = Game._monster_attack_range_x
        self._attack_y = Game._monster_attack_range_y
        self._move_x = 20
        self._move_y = 20
        self._direction = direction
        self._selected_door_center = selected_door_center
        self._target_kind = target_kind

    def _current_door_direction(self) -> str | None:
        if isinstance(self._direction, (list, tuple)):
            if not self._direction:
                return None
            if Game._index >= len(self._direction):
                return str(self._direction[-1]).upper()
            return str(self._direction[Game._index]).upper()
        if isinstance(self._direction, str) and self._direction.strip():
            return self._direction.strip().upper()
        return None

    def _get_cls(self, cls_name: str) -> BoxDict | None:
        for item in self._obj:
            if cls_name in item:
                return item[cls_name]
        return None

    def _get_clss(self, cls_name: str) -> list[BoxDict]:
        result = []
        for item in self._obj:
            if cls_name in item:
                result.append(item[cls_name])
        return result

    def _release_direction_keys(self) -> None:
        for key in ("up", "down", "left", "right"):
            pydirectinput.keyUp(key)

    @classmethod
    def reset_motion_cache(cls) -> None:
        cls._action_cache = None
        cls._action_cache_time = 0.0
        cls._position_history.clear()
        cls._stuck_count = 0
        cls._last_recover_time = 0.0
        cls._last_attack_time = 0.0
        cls._next_special_attack_time = 0.0
        cls._next_extra_attack_time = 0.0
        cls._active_route_direction = None
        cls._right_search_until_door = False

    @classmethod
    def release_action_keys(cls, extra_keys: Iterable[str] = ()) -> None:
        keys = {
            "up",
            "down",
            "left",
            "right",
            cls._attack_key,
            cls._special_attack_key,
            cls._extra_attack_key,
        }
        if cls._action_cache:
            keys.update(action.lower() for action in cls._action_cache.strip().split("_") if action)
        keys.update(key.strip().lower() for key in extra_keys if key and key.strip())
        for key in keys:
            pydirectinput.keyUp(key)
        cls._action_cache = None
        cls._action_cache_time = 0.0

    def _release_cached_action(self) -> None:
        if not Game._action_cache:
            self._release_direction_keys()
            return
        for action in Game._action_cache.strip().split("_"):
            pydirectinput.keyUp(action.lower())
        self._release_direction_keys()
        Game._action_cache = None
        Game._action_cache_time = 0.0

    def _distance(self, a: tuple[float, float], b: tuple[float, float]) -> float:
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

    def _infer_flow_direction_from_spawn(self, player_center: tuple[float, float]) -> str | None:
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
            self._reset_route_search()
            self._reset_down_stuck_search()
            self._reset_up_stuck_search()
            self._reset_vertical_escape()
            self._reset_right_search_lock()
            logger.info(
                "room transition inferred, entry={}, flow_direction={}",
                Game._room_entry_position,
                Game._flow_direction,
            )

    def _filter_backtrack_doors(self, doors: Sequence[BoxDict], direction_hint: str | None) -> list[BoxDict]:
        if not doors:
            return []

        if not Game._room_entry_position:
            return list(doors)

        now = time.time()
        protect_entry = now - Game._room_entry_time <= Game._entry_door_protect_seconds
        if not protect_entry:
            return list(doors)

        entry = Game._room_entry_position
        entry_side = self._reverse_direction(Game._flow_direction)
        direction_hint = direction_hint.upper() if direction_hint else None
        filtered: list[BoxDict] = []
        for door in doors:
            x, y, w, h = door["xywh"]
            center = (x + w / 2.0, y + h / 2.0)
            near_entry = self._distance(center, entry) <= Game._entry_door_protect_radius
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
        return bool(Game._room_entry_position) and (
            time.time() - Game._room_entry_time <= Game._entry_door_protect_seconds
        )

    def _should_block_backtrack_direction(self, direction: str | None) -> bool:
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

    def _attack_ready(self) -> bool:
        return time.time() - Game._last_attack_time >= Game._attack_cooldown_seconds

    def _special_attack_ready(self, now: float | None = None) -> bool:
        now = time.time() if now is None else now

        return now >= Game._next_special_attack_time

    def _try_attack(self, face: str | None = None) -> bool:
        self._release_cached_action()
        now = time.time()
        special_ready = self._special_attack_ready(now)
        attack_ready = now - Game._last_attack_time >= Game._attack_cooldown_seconds
        extra_ready = now >= Game._next_extra_attack_time
        if not extra_ready and not special_ready and not attack_ready:
            logger.info(
                "skip attack keys {}, {}, cooldown active",
                Game._special_attack_key,
                Game._attack_key,
            )
            return False

        if face:
            self._key_press(face)

        if extra_ready:
            self._key_press(Game._extra_attack_key)
            cooldown = random.uniform(*Game._extra_attack_cooldown_range)
            Game._next_extra_attack_time = now + cooldown
            Game._last_attack_time = now
            logger.info(
                "press extra attack key {}, cooldown {:.2f}s",
                Game._extra_attack_key,
                cooldown,
            )
            return True

        if special_ready:
            self._key_press(Game._special_attack_key)
            cooldown = random.uniform(*Game._special_attack_cooldown_range)
            Game._next_special_attack_time = now + cooldown
            Game._last_attack_time = now
            logger.info(
                "press special attack key {}, cooldown {:.2f}s",
                Game._special_attack_key,
                cooldown,
            )
            return True

        self._key_press(Game._attack_key)
        Game._last_attack_time = now
        return True

    def _tap_direction(self, direction: str, duration: float | None = None) -> None:
        duration = Game._tap_direction_seconds if duration is None else duration
        for action in direction.strip().split("_"):
            pydirectinput.keyDown(action.lower())
        time.sleep(duration)
        for action in direction.strip().split("_"):
            pydirectinput.keyUp(action.lower())
        time.sleep(0.04)

    def _reverse_direction(self, direction: str | None) -> str | None:
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

    def _primary_door_direction(self, direction: str | None) -> str | None:
        if not direction:
            return None
        direction = direction.upper()
        if "RIGHT" in direction:
            return "RIGHT"
        if "LEFT" in direction:
            return "LEFT"
        if "DOWN" in direction:
            return "DOWN"
        if "UP" in direction:
            return "UP"
        return direction

    def _get_nearest(self, cls_objs: Sequence[BoxDict], direct: str | None = None) -> BoxDict | None:
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

            distance = (dx**2 + dy**2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                nearest = {
                    "xywh": [obj_x, obj_y, xywh[2], xywh[3]],
                    "conf": item.get("conf", 0),
                }

        return nearest

    def _get_route_forward_door(self, doors: Sequence[BoxDict], direction: str | None) -> BoxDict | None:
        if not doors or not direction or not self._player_xywh:
            return None

        direction = self._primary_door_direction(direction) or direction.upper()
        candidates = []
        player_x = self._player_xywh[0]
        player_y = self._player_xywh[1]
        for item in doors:
            xywh = list(item["xywh"])
            obj_x = xywh[0] + xywh[2] / 2
            obj_y = xywh[1] + xywh[3] / 2
            dx = obj_x - player_x
            dy = obj_y - player_y

            if direction == "RIGHT":
                if dx <= 0:
                    continue
                score = (-obj_x, abs(dy), abs(dx))
            elif direction == "LEFT":
                if dx >= 0:
                    continue
                score = (obj_x, abs(dy), abs(dx))
            elif direction == "DOWN":
                if dy <= 0:
                    continue
                score = (-obj_y, abs(dx), abs(dy))
            elif direction == "UP":
                if dy >= 0:
                    continue
                score = (obj_y, abs(dx), abs(dy))
            else:
                return self._get_nearest(doors, direct=direction)

            candidates.append(
                (
                    score,
                    {
                        "xywh": [obj_x, obj_y, xywh[2], xywh[3]],
                        "conf": item.get("conf", 0),
                    },
                )
            )

        if not candidates:
            return None
        candidates.sort(key=lambda item: item[0])
        return candidates[0][1]

    def _get_door_by_center(
        self,
        doors: Sequence[BoxDict],
        center: tuple[float, float] | None,
        max_distance: float = 80.0,
    ) -> BoxDict | None:
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

    def _get_direction(self, obj_box: Sequence[float]) -> str | None:
        if not self._player_xywh:
            return None
        dx = obj_box[0] - self._player_xywh[0]
        dy = obj_box[1] - self._player_xywh[1]

        if abs(dx) < 1 and abs(dy) < 1:
            return None
        horizontal_deadzone = max(1.0, Game._horizontal_move_y_deadzone)
        diagonal_y_ratio = max(0.1, Game._diagonal_y_ratio)

        if abs(dy) <= horizontal_deadzone and abs(dx) >= 1:
            return "RIGHT" if dx > 0 else "LEFT"

        if dy < 0:
            if self._player_xywh[1] - obj_box[1] < abs(dx) * diagonal_y_ratio:
                return "RIGHT_UP" if dx > 0 else "LEFT_UP"
            return "UP"
        if dy > 0:
            if dy < abs(dx) * diagonal_y_ratio:
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
        _action_cache: str | None = None,
        press_time: float | None = None,
        release_time: float | None = None,
    ) -> str:
        press_time = Game._move_press_time if press_time is None else press_time
        release_time = Game._move_release_time if release_time is None else release_time
        logger.debug("current direction: {}, cached direction: {}", direction, _action_cache)
        now = time.time()
        if is_slow and _action_cache == direction:
            if now - Game._action_cache_time >= Game._move_reassert_seconds:
                for action in direction.strip().split("_"):
                    pydirectinput.keyDown(action.lower())
                Game._action_cache_time = now
            return direction

        if _action_cache and direction != _action_cache:
            for action in _action_cache.strip().split("_"):
                pydirectinput.keyUp(action.lower())

        for action in direction.strip().split("_"):
            pydirectinput.keyDown(action.lower())
        Game._action_cache_time = now

        if not is_slow:
            time.sleep(press_time)
            for action in direction.strip().split("_"):
                pydirectinput.keyUp(action.lower())
            time.sleep(release_time)
            for action in direction.strip().split("_"):
                pydirectinput.keyDown(action.lower())
            Game._action_cache_time = time.time()

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

        if (
            abs(obj_box[0] - self._player_xywh[0]) < self._attack_x
            and abs(obj_box[1] - self._player_xywh[1]) < self._attack_y
        ):
            direction = self._get_direction(obj_box)
            face = None
            if direction:
                for item in direction.split("_"):
                    if "RIGHT" in item:
                        face = "RIGHT"
                    elif "LEFT" in item:
                        face = "LEFT"
                    break

            self._try_attack(face.lower() if face else None)
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
        abs_dx = abs(dx)
        abs_dy = abs(dy)
        x_deadzone = max(12.0, Game._pickup_x_deadzone)
        y_sweep_x_range = max(x_deadzone, Game._pickup_y_sweep_x_range)
        y_deadzone = max(8.0, Game._pickup_y_deadzone)

        if abs_dx <= x_deadzone and abs_dy <= y_deadzone:
            self._release_cached_action()
            self._key_press("x")
            return

        if abs_dy <= y_deadzone:
            direction = "RIGHT" if dx > 0 else "LEFT"
        elif abs_dx <= x_deadzone:
            direction = "DOWN" if dy > 0 else "UP"
        elif abs_dx <= y_sweep_x_range:
            direction = "DOWN" if dy > 0 else "UP"
        else:
            direction = self._get_direction(obj_box)

        if direction:
            Game._action_cache = self._move(direction, is_slow=True, _action_cache=Game._action_cache)

    def _move_to_door(self, obj_box: Sequence[float]) -> None:
        direction = self._get_route_direction_to_target(obj_box) or self._get_direction(obj_box)
        if direction:
            Game._action_cache = self._move(direction, is_slow=True, _action_cache=Game._action_cache)

    def _try_probe_attack(self) -> bool:
        now = time.time()
        if now - Game._last_attack_time < Game._attack_cooldown_seconds:
            return False

        self._release_cached_action()
        face = None
        if Game._flow_direction in {"LEFT", "RIGHT"}:
            face = Game._flow_direction.lower()
        elif self._player_xywh:
            face = "right" if self._player_xywh[0] <= self._width / 2 else "left"

        if face:
            self._key_press(face)
        self._key_press(Game._attack_key)
        Game._last_attack_time = now
        return True

    def _wait_for_missing_query_target(self) -> None:
        self._reset_route_search()
        self._reset_down_stuck_search()
        self._reset_up_stuck_search()
        self._reset_vertical_escape()
        self._reset_right_search_lock()
        if self._try_probe_attack():
            logger.warning("query marker missing, hold room and probe attack for possible off-screen monster")
        else:
            logger.warning("query marker missing, hold room and wait for monster detection")

    def _reset_route_search(self) -> None:
        Game._route_search_direction = None
        Game._route_search_phase = 0
        Game._route_search_start = None

    def _route_search_progress_reached(
        self,
        start: tuple[float, float],
        current: tuple[float, float],
        command: str,
    ) -> bool:
        start_x, start_y = start
        current_x, current_y = current
        x_amplitude = Game._route_search_x_amplitude
        y_amplitude = Game._route_search_y_amplitude
        if "RIGHT" in command and current_x - start_x >= x_amplitude:
            return True
        if "LEFT" in command and start_x - current_x >= x_amplitude:
            return True
        if "DOWN" in command and current_y - start_y >= y_amplitude:
            return True
        if "UP" in command and start_y - current_y >= y_amplitude:
            return True
        return False

    def _route_search_commands(self, direction: str) -> tuple[str, ...]:
        mapping = {
            "RIGHT": ("RIGHT",),
            "LEFT": ("LEFT",),
            "DOWN": ("DOWN",),
            "UP": ("UP",),
        }
        return mapping.get(direction, (direction,))

    def _get_route_direction_to_target(
        self, obj_box: Sequence[float], route_direction: str | None = None
    ) -> str | None:
        route_direction = self._current_door_direction() if route_direction is None else route_direction
        route_direction = self._primary_door_direction(route_direction)
        if route_direction not in {"LEFT", "RIGHT"} or not self._player_xywh:
            return None

        dx = obj_box[0] - self._player_xywh[0]
        if route_direction == "RIGHT" and dx <= 0:
            return None
        if route_direction == "LEFT" and dx >= 0:
            return None
        if abs(dx) > Game._horizontal_door_align_distance:
            return self._avoid_screen_edge_for_search(route_direction, route_direction)
        return None

    def _limit_horizontal_search_vertical_command(self, route_direction: str, command: str) -> str:
        if route_direction not in {"LEFT", "RIGHT"} or "_" not in command:
            return command
        if not self._player_xywh or Game._route_search_start is None:
            return command

        start_y = Game._route_search_start[1]
        current_y = self._player_xywh[1]
        if "DOWN" in command and current_y - start_y >= Game._route_search_y_amplitude:
            return route_direction
        if "UP" in command and start_y - current_y >= Game._route_search_y_amplitude:
            return route_direction
        return command

    def _avoid_screen_edge_for_search(self, route_direction: str, command: str) -> str:
        if not self._player_xywh:
            return command

        player_x = self._player_xywh[0]
        player_y = self._player_xywh[1]
        route_direction = route_direction.upper()

        if route_direction in {"LEFT", "RIGHT"}:
            if player_y > self._height * Game._horizontal_edge_bottom_ratio:
                return f"{route_direction}_UP"
            if player_y < self._height * Game._horizontal_edge_top_ratio:
                return f"{route_direction}_DOWN"
            return command

        if route_direction == "DOWN":
            return "DOWN"

        if route_direction == "UP":
            right_edge = self._width * (0.66 + Game._route_search_edge_band)
            right_clear = self._width * (0.66 - Game._route_search_edge_band)
            left_edge = self._width * (0.34 - Game._route_search_edge_band)
            left_clear = self._width * (0.34 + Game._route_search_edge_band)

            if "LEFT" in command and player_x > right_clear:
                return "LEFT_UP"
            if "RIGHT" in command and player_x < left_clear:
                return "RIGHT_UP"
            if player_x > right_edge:
                return "LEFT_UP"
            if player_x < left_edge:
                return "RIGHT_UP"
            return command

        return command

    def _fallback_door_search_move(self, direction: str) -> None:
        route_direction = direction.upper()
        if route_direction not in {"LEFT", "RIGHT", "UP", "DOWN"}:
            self._reset_route_search()
            Game._action_cache = self._move(route_direction, is_slow=True, _action_cache=Game._action_cache)
            return

        if not self._player_xywh:
            self._reset_route_search()
            Game._action_cache = self._move(route_direction, is_slow=True, _action_cache=Game._action_cache)
            return

        current = (self._player_xywh[0], self._player_xywh[1])
        if Game._route_search_direction != route_direction:
            Game._route_search_direction = route_direction
            Game._route_search_phase = 0
            Game._route_search_start = current

        if Game._route_search_start is None:
            Game._route_search_start = current

        commands = self._route_search_commands(route_direction)
        phase = Game._route_search_phase % len(commands)
        command = commands[phase]
        if self._route_search_progress_reached(Game._route_search_start, current, command):
            Game._route_search_phase = (Game._route_search_phase + 1) % len(commands)
            Game._route_search_start = current
            command = commands[Game._route_search_phase]

        phase_command = command
        command = self._avoid_screen_edge_for_search(route_direction, command)
        if command == phase_command:
            command = self._limit_horizontal_search_vertical_command(route_direction, command)
        logger.debug(
            "door search fallback: route={}, phase={}, start={}, current={}, command={}",
            route_direction,
            Game._route_search_phase,
            Game._route_search_start,
            current,
            command,
        )
        Game._action_cache = self._move(command, is_slow=True, _action_cache=Game._action_cache)

    def _reset_down_stuck_search(self) -> None:
        Game._down_stuck_anchor = None
        Game._down_stuck_since = 0.0
        Game._down_right_search_until = 0.0

    def _reset_up_stuck_search(self) -> None:
        Game._up_stuck_anchor = None
        Game._up_stuck_since = 0.0
        Game._up_right_search_until = 0.0

    def _reset_vertical_escape(self) -> None:
        Game._vertical_escape_direction = None
        Game._vertical_escape_target_y = None
        Game._vertical_escape_source_direction = None

    def _reset_right_search_lock(self) -> None:
        Game._right_search_anchor_x = None
        Game._right_search_until = 0.0
        Game._right_search_until_door = False

    def _sync_route_direction_state(self) -> None:
        route_direction = self._current_door_direction()
        if route_direction == Game._active_route_direction:
            return

        previous_direction = Game._active_route_direction
        Game._active_route_direction = route_direction
        cached_action = (Game._action_cache or "").upper()
        cached_parts = set(cached_action.split("_")) if cached_action else set()
        stale_cached_action = bool(cached_action and (route_direction is None or route_direction not in cached_parts))
        stale_vertical_escape = bool(
            Game._vertical_escape_source_direction and Game._vertical_escape_source_direction != route_direction
        )

        if stale_cached_action or stale_vertical_escape:
            self._reset_route_search()
            self._reset_down_stuck_search()
            self._reset_up_stuck_search()
            self._reset_vertical_escape()
            self._reset_right_search_lock()

        if stale_cached_action:
            self._release_cached_action()

        if previous_direction != route_direction and (stale_cached_action or stale_vertical_escape):
            logger.info(
                "route direction changed: {} -> {}, reset stale movement state",
                previous_direction,
                route_direction,
            )

    def _begin_right_search_lock(self, until_door: bool = False) -> None:
        if not self._player_xywh:
            return
        Game._right_search_anchor_x = self._player_xywh[0]
        Game._right_search_until = float("inf") if until_door else time.time() + Game._down_right_search_seconds
        Game._right_search_until_door = until_door

    def _has_usable_route_door(self) -> bool:
        doors = self._get_clss("door")
        if not doors:
            return False

        direction_hint = self._current_door_direction()
        if not direction_hint:
            return True

        usable_doors = self._filter_backtrack_doors(doors, direction_hint)
        if self._selected_door_center and self._get_door_by_center(usable_doors, self._selected_door_center):
            return True
        if self._get_route_forward_door(usable_doors, direction_hint):
            return True
        if self._would_push_outside(direction_hint) and usable_doors:
            return True
        return False

    def _get_right_search_door(self) -> BoxDict | None:
        doors = self._get_clss("door")
        if not doors:
            return None
        usable_doors = self._filter_backtrack_doors(doors, "RIGHT")
        return self._get_route_forward_door(usable_doors, "RIGHT")

    def _move_to_right_search_door(self, door: BoxDict) -> None:
        direction = self._get_route_direction_to_target(door["xywh"], route_direction="RIGHT") or self._get_direction(
            door["xywh"]
        )
        if direction:
            Game._action_cache = self._move(direction, is_slow=True, _action_cache=Game._action_cache)

    def _continue_right_search_lock(self) -> bool:
        if not self._player_xywh or Game._right_search_anchor_x is None:
            self._reset_right_search_lock()
            return False
        if Game._right_search_until_door:
            right_door = self._get_right_search_door()
            if right_door is not None:
                logger.debug("right-search lock found right door, keep moving to it")
                self._move_to_right_search_door(right_door)
                return True
            Game._action_cache = self._move("RIGHT", is_slow=True, _action_cache=Game._action_cache)
            return True
        if self._has_usable_route_door():
            self._reset_right_search_lock()
            return False

        moved_right = self._player_xywh[0] - Game._right_search_anchor_x
        Game._action_cache = self._move("RIGHT", is_slow=True, _action_cache=Game._action_cache)
        if not Game._right_search_until_door and (
            moved_right >= Game._right_search_pixels or time.time() > Game._right_search_until
        ):
            self._reset_right_search_lock()
        return True

    def _should_search_right_after_vertical_stuck(self, direction: str) -> bool:
        if not self._player_xywh:
            if direction == "UP":
                self._reset_up_stuck_search()
            else:
                self._reset_down_stuck_search()
            return False

        now = time.time()
        current = (self._player_xywh[0], self._player_xywh[1])
        if direction == "UP":
            anchor = Game._up_stuck_anchor
            stuck_since = Game._up_stuck_since
            right_search_until = Game._up_right_search_until
        else:
            anchor = Game._down_stuck_anchor
            stuck_since = Game._down_stuck_since
            right_search_until = Game._down_right_search_until

        if now < right_search_until:
            return True

        if anchor is None:
            if direction == "UP":
                Game._up_stuck_anchor = current
                Game._up_stuck_since = now
            else:
                Game._down_stuck_anchor = current
                Game._down_stuck_since = now
            return False

        if self._distance(current, anchor) > Game._down_stuck_move_tolerance:
            if direction == "UP":
                Game._up_stuck_anchor = current
                Game._up_stuck_since = now
            else:
                Game._down_stuck_anchor = current
                Game._down_stuck_since = now
            return False

        if now - stuck_since >= Game._down_stuck_seconds:
            if direction == "UP":
                Game._up_right_search_until = now + Game._down_right_search_seconds
                Game._up_stuck_anchor = current
                Game._up_stuck_since = now
            else:
                Game._down_right_search_until = now + Game._down_right_search_seconds
                Game._down_stuck_anchor = current
                Game._down_stuck_since = now
            logger.warning(
                "{} stuck for {:.1f}s, move away from edge before searching door to RIGHT",
                direction,
                Game._down_stuck_seconds,
            )
            return True

        return False

    def _should_search_right_after_down_stuck(self) -> bool:
        return self._should_search_right_after_vertical_stuck("DOWN")

    def _should_search_right_after_up_stuck(self) -> bool:
        return self._should_search_right_after_vertical_stuck("UP")

    def _cached_vertical_stuck_direction(self, force: bool = False) -> str | None:
        if not self._player_xywh:
            self._reset_up_stuck_search()
            self._reset_down_stuck_search()
            return None

        cached_action = (Game._action_cache or "").upper()
        has_up = "UP" in cached_action
        has_down = "DOWN" in cached_action
        if has_up == has_down:
            self._reset_up_stuck_search()
            self._reset_down_stuck_search()
            return None

        direction = "UP" if has_up else "DOWN"
        now = time.time()
        current = (self._player_xywh[0], self._player_xywh[1])
        if direction == "UP":
            anchor = Game._up_stuck_anchor
            stuck_since = Game._up_stuck_since
        else:
            anchor = Game._down_stuck_anchor
            stuck_since = Game._down_stuck_since

        if anchor is None:
            if direction == "UP":
                Game._up_stuck_anchor = current
                Game._up_stuck_since = now
                self._reset_down_stuck_search()
            else:
                Game._down_stuck_anchor = current
                Game._down_stuck_since = now
                self._reset_up_stuck_search()
            anchor = current
            stuck_since = now
            if not force:
                return None

        if abs(current[1] - anchor[1]) > Game._vertical_stuck_y_tolerance:
            if direction == "UP":
                Game._up_stuck_anchor = current
                Game._up_stuck_since = now
            else:
                Game._down_stuck_anchor = current
                Game._down_stuck_since = now
            if not force:
                return None

        if force or now - stuck_since >= Game._down_stuck_seconds:
            if direction == "UP":
                Game._up_stuck_anchor = current
                Game._up_stuck_since = now
            else:
                Game._down_stuck_anchor = current
                Game._down_stuck_since = now
            logger.warning(
                "{} movement stuck for {:.1f}s while holding {}, tap out once then lock RIGHT",
                direction,
                Game._down_stuck_seconds,
                cached_action,
            )
            return direction

        return None

    def _vertical_edge_escape_direction(self, direction: str) -> str | None:
        if direction == "UP":
            return "DOWN"
        if direction == "DOWN":
            return "UP"
        return None

    def _escape_vertical_stuck_then_search_right(self, direction: str) -> bool:
        if not self._player_xywh:
            return False

        escape_direction = self._vertical_edge_escape_direction(direction)
        if escape_direction is None:
            return False

        self._reset_route_search()
        self._release_cached_action()
        self._tap_direction(escape_direction, duration=0.08)
        if direction == "DOWN":
            self._reset_down_stuck_search()
        elif direction == "UP":
            self._reset_up_stuck_search()
        self._reset_vertical_escape()
        self._begin_right_search_lock(until_door=True)
        Game._action_cache = self._move("RIGHT", is_slow=True, _action_cache=Game._action_cache)
        logger.warning("{} stuck, nudged {} once then locked RIGHT search", direction, escape_direction)
        return True

    def _continue_vertical_escape(self) -> bool:
        """Migrate stale vertical escape state to the new right-search behavior."""
        source_direction = Game._vertical_escape_source_direction
        if source_direction == "DOWN":
            self._reset_down_stuck_search()
            self._begin_right_search_lock(until_door=True)
        elif source_direction == "UP":
            self._reset_up_stuck_search()
            self._begin_right_search_lock(until_door=True)
        self._reset_vertical_escape()
        return False

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
        normalized = self._primary_door_direction(direction) or direction.upper()
        if self._continue_right_search_lock():
            return
        if normalized == "DOWN":
            if not self._player_xywh:
                Game._action_cache = self._move("DOWN", is_slow=True, _action_cache=Game._action_cache)
                return
            if self._should_search_right_after_down_stuck():
                self._escape_vertical_stuck_then_search_right("DOWN")
                return
            self._fallback_door_search_move("DOWN")
            return

        if normalized == "UP":
            self._reset_down_stuck_search()
            if not self._player_xywh:
                Game._action_cache = self._move("UP", is_slow=True, _action_cache=Game._action_cache)
                return
            if self._should_search_right_after_up_stuck():
                self._escape_vertical_stuck_then_search_right("UP")
                return
            self._fallback_door_search_move("UP")
            return

        if normalized in {"LEFT", "RIGHT"}:
            self._reset_down_stuck_search()
            self._reset_up_stuck_search()
            self._fallback_door_search_move(normalized)
            return

        self._reset_route_search()
        self._reset_down_stuck_search()
        self._reset_up_stuck_search()
        Game._action_cache = self._move(normalized, is_slow=True, _action_cache=Game._action_cache)

    def _check_position(self) -> str:
        if not self._player_xywh:
            return "RIGHT_DOWN"
        player_x = self._player_xywh[0]
        player_y = self._player_xywh[1]

        if player_x < self._width / 2:
            return "LEFT_UP" if player_y < self._height / 2 else "LEFT_DOWN"
        return "RIGHT_UP" if player_y < self._height / 2 else "RIGHT_DOWN"

    def _would_push_outside(self, direction: str | None) -> bool:
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
            logger.debug("player center: {}", self._player_xywh[:2])
            self._sync_route_direction_state()
            self._maybe_update_room_entry()

            if self._continue_vertical_escape():
                return
            if self._continue_right_search_lock():
                return

            cached_vertical_stuck = self._cached_vertical_stuck_direction()
            if cached_vertical_stuck:
                if self._escape_vertical_stuck_then_search_right(cached_vertical_stuck):
                    return

            if self._update_motion_state(
                expect_motion=Game._action_cache is not None,
                player_visible=raw_player is not None,
            ):
                cached_vertical_stuck = self._cached_vertical_stuck_direction(force=True)
                if cached_vertical_stuck:
                    if self._escape_vertical_stuck_then_search_right(cached_vertical_stuck):
                        return

                cached_action = (Game._action_cache or "").upper()
                if self._current_door_direction() == "DOWN" and "DOWN" in cached_action:
                    logger.warning("DOWN movement stalled, keep fallback search active")
                else:
                    if self._current_door_direction() == "DOWN":
                        if self._escape_vertical_stuck_then_search_right("DOWN"):
                            return
                    elif self._current_door_direction() == "UP":
                        if self._escape_vertical_stuck_then_search_right("UP"):
                            return
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

            if self._target_kind == "query_missing":
                self._wait_for_missing_query_target()
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
                    nearest_door = (
                        self._get_route_forward_door(usable_doors, direction_hint) if direction_hint else None
                    )
                if nearest_door is None and direction_hint:
                    if self._would_push_outside(direction_hint) and usable_doors:
                        logger.warning(
                            "route hint {} points outside screen edge, use nearest visible door", direction_hint
                        )
                        nearest_door = self._get_nearest(usable_doors)
                    else:
                        logger.debug("doors found but none match route hint {}, keep following hint", direction_hint)
                        raise LookupError("no door matches route hint")
                if nearest_door is None and direction_hint:
                    logger.debug("doors found but none match route hint {}, keep following hint", direction_hint)
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
            if self._vertical_escape_direction and self._continue_vertical_escape():
                return
            if self._continue_right_search_lock():
                return
            if self._should_block_backtrack_direction(fallback_direction):
                if fallback_direction.upper() in {"DOWN", "RIGHT"}:
                    logger.warning(
                        "fallback direction {} is entry side, keep route search instead of using backtrack door",
                        fallback_direction,
                    )
                    self._fallback_route_move(fallback_direction)
                    return
                logger.warning("fallback direction {} points to entry side, hold position", fallback_direction)
                self._release_cached_action()
                return
            logger.debug("no target found, fallback move: {}", fallback_direction)
            self._fallback_route_move(fallback_direction)
            return

        logger.warning("no target found and no route hint, hold position")
        self._release_cached_action()
