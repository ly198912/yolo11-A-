from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dnf.game import Game


def _reset_search_state() -> None:
    Game._action_cache = None
    Game._action_cache_time = 0.0
    Game._route_search_direction = None
    Game._route_search_phase = 0
    Game._route_search_start = None
    Game._down_stuck_anchor = None
    Game._down_stuck_since = 0.0
    Game._down_right_search_until = 0.0
    Game._up_stuck_anchor = None
    Game._up_stuck_since = 0.0
    Game._up_right_search_until = 0.0
    Game._vertical_escape_direction = None
    Game._vertical_escape_target_y = None
    Game._vertical_escape_source_direction = None
    Game._right_search_anchor_x = None
    Game._right_search_until = 0.0
    Game._right_search_until_door = False
    Game._player = None
    Game._pre_player = None
    Game._player_missing_count = 0
    Game._room_entry_position = None
    Game._room_entry_time = 0.0
    Game._flow_direction = None
    Game._last_player_center = None


def _game_with_recorder() -> tuple[Game, list[str]]:
    game = Game([], width=800, height=600, direction="RIGHT")
    game._player_xywh = [400.0, 300.0, 0.0, 0.0]
    moves: list[str] = []

    def record_move(direction: str, **kwargs) -> str:
        moves.append(direction)
        return direction

    game._move = record_move  # type: ignore[method-assign]
    game._tap_direction = lambda direction, duration=None: None  # type: ignore[method-assign]
    return game, moves


def test_right_fallback_moves_straight_while_searching_for_door() -> None:
    _reset_search_state()
    game, moves = _game_with_recorder()

    game._fallback_route_move("RIGHT")
    game._player_xywh = [410.0, 340.0, 0.0, 0.0]
    game._fallback_route_move("RIGHT")

    assert moves == ["RIGHT", "RIGHT"]


def test_down_fallback_keeps_moving_down_without_sideways_drift() -> None:
    _reset_search_state()
    game, moves = _game_with_recorder()

    game._player_xywh = [400.0, 300.0, 0.0, 0.0]
    game._fallback_route_move("DOWN")
    game._fallback_route_move("DOWN")

    assert moves == ["DOWN", "DOWN"]


def test_horizontal_fallback_avoids_bottom_edge() -> None:
    _reset_search_state()
    game, moves = _game_with_recorder()
    game._player_xywh = [400.0, 560.0, 0.0, 0.0]

    game._fallback_route_move("RIGHT")

    assert moves == ["RIGHT_UP"]


def test_down_route_entry_guard_keeps_moving_down_without_sideways_drift() -> None:
    _reset_search_state()
    game = Game(
        [{"player": {"xywh": [380.0, 500.0, 40.0, 80.0], "conf": 0.9}}],
        width=800,
        height=600,
        direction="DOWN",
    )
    moves: list[str] = []

    def record_move(direction: str, **kwargs) -> str:
        moves.append(direction)
        return direction

    game._move = record_move  # type: ignore[method-assign]
    Game._room_entry_position = (400.0, 540.0)
    Game._room_entry_time = time.time()
    Game._flow_direction = "UP"
    Game._last_player_center = (400.0, 540.0)

    game.run()

    assert moves == ["DOWN"]


def test_down_stuck_nudges_up_three_pixels() -> None:
    _reset_search_state()
    game, moves = _game_with_recorder()
    game._player_xywh = [400.0, 500.0, 0.0, 0.0]
    Game._down_stuck_anchor = (400.0, 500.0)
    Game._down_stuck_since = time.time() - Game._down_stuck_seconds - 0.1

    game._fallback_route_move("DOWN")

    assert moves == ["RIGHT"]
    assert Game._vertical_escape_direction is None
    assert Game._right_search_anchor_x == 400.0
    assert Game._right_search_until_door


def test_down_stuck_returns_to_right_after_three_pixel_nudge() -> None:
    _reset_search_state()
    game, moves = _game_with_recorder()
    game._player_xywh = [400.0, 497.0, 0.0, 0.0]
    Game._vertical_escape_direction = "UP"
    Game._vertical_escape_target_y = 497.0
    Game._vertical_escape_source_direction = "DOWN"

    assert not game._continue_vertical_escape()
    game._fallback_route_move("DOWN")

    assert moves == ["RIGHT"]
    assert Game._right_search_anchor_x == 400.0
    assert Game._right_search_until_door


def test_up_stuck_nudges_down_three_pixels() -> None:
    _reset_search_state()
    game, moves = _game_with_recorder()
    game._player_xywh = [400.0, 80.0, 0.0, 0.0]
    Game._up_stuck_anchor = (400.0, 80.0)
    Game._up_stuck_since = time.time() - Game._down_stuck_seconds - 0.1

    game._fallback_route_move("UP")

    assert moves == ["RIGHT"]
    assert Game._vertical_escape_direction is None
    assert Game._right_search_anchor_x == 400.0
    assert Game._right_search_until_door


def test_up_stuck_returns_to_route_after_three_pixel_nudge() -> None:
    _reset_search_state()
    game, moves = _game_with_recorder()
    game._player_xywh = [400.0, 83.0, 0.0, 0.0]
    Game._vertical_escape_direction = "DOWN"
    Game._vertical_escape_target_y = 83.0
    Game._vertical_escape_source_direction = "UP"

    assert not game._continue_vertical_escape()
    game._fallback_route_move("UP")

    assert moves == ["RIGHT"]
    assert Game._right_search_anchor_x == 400.0
    assert Game._right_search_until_door


def test_up_fallback_search_moves_up_when_centered() -> None:
    _reset_search_state()
    game, moves = _game_with_recorder()
    game._player_xywh = [400.0, 300.0, 0.0, 0.0]

    game._fallback_route_move("UP")

    assert moves == ["UP"]


def test_up_fallback_search_nudges_back_from_right_edge() -> None:
    _reset_search_state()
    game, moves = _game_with_recorder()
    game._player_xywh = [620.0, 300.0, 0.0, 0.0]

    game._fallback_route_move("UP")

    assert moves == ["LEFT_UP"]


def test_right_search_lock_keeps_right_until_x_progress() -> None:
    _reset_search_state()
    game, moves = _game_with_recorder()
    game._player_xywh = [400.0, 300.0, 0.0, 0.0]
    game._begin_right_search_lock()

    game._player_xywh = [410.0, 300.0, 0.0, 0.0]
    game._fallback_route_move("UP")
    game._player_xywh = [445.0, 300.0, 0.0, 0.0]
    game._fallback_route_move("UP")

    assert moves == ["RIGHT", "RIGHT"]
    assert Game._right_search_anchor_x is None


def test_vertical_escape_right_search_keeps_right_until_door_is_visible() -> None:
    _reset_search_state()
    game, moves = _game_with_recorder()
    game._player_xywh = [400.0, 83.0, 0.0, 0.0]
    Game._vertical_escape_direction = "DOWN"
    Game._vertical_escape_target_y = 83.0
    Game._vertical_escape_source_direction = "UP"

    assert not game._continue_vertical_escape()
    game._player_xywh = [480.0, 83.0, 0.0, 0.0]
    game._fallback_route_move("RIGHT")
    game._player_xywh = [560.0, 83.0, 0.0, 0.0]
    game._fallback_route_move("RIGHT")

    assert moves == ["RIGHT", "RIGHT"]
    assert Game._right_search_anchor_x == 400.0
    assert Game._right_search_until_door


def test_vertical_escape_right_search_keeps_lock_when_right_door_is_visible() -> None:
    _reset_search_state()
    game = Game(
        [{"door": {"xywh": [620.0, 250.0, 80.0, 130.0], "conf": 0.9}}],
        width=800,
        height=600,
        direction="RIGHT",
    )
    game._player_xywh = [500.0, 83.0, 0.0, 0.0]
    moves: list[str] = []

    def record_move(direction: str, **kwargs) -> str:
        moves.append(direction)
        return direction

    game._move = record_move  # type: ignore[method-assign]
    game._tap_direction = lambda direction, duration=None: None  # type: ignore[method-assign]
    Game._right_search_anchor_x = 400.0
    Game._right_search_until = float("inf")
    Game._right_search_until_door = True

    assert game._continue_right_search_lock()
    assert moves == ["RIGHT"]
    assert Game._right_search_anchor_x == 400.0
    assert Game._right_search_until_door


def test_vertical_escape_right_search_ignores_non_route_door() -> None:
    _reset_search_state()
    game = Game(
        [{"door": {"xywh": [0.0, 326.0, 52.0, 90.0], "conf": 0.9}}],
        width=800,
        height=600,
        direction="DOWN",
    )
    game._player_xywh = [451.0, 475.0, 0.0, 0.0]
    moves: list[str] = []

    def record_move(direction: str, **kwargs) -> str:
        moves.append(direction)
        return direction

    game._move = record_move  # type: ignore[method-assign]
    Game._right_search_anchor_x = 400.0
    Game._right_search_until = float("inf")
    Game._right_search_until_door = True

    assert game._continue_right_search_lock()
    assert moves == ["RIGHT"]
    assert Game._right_search_anchor_x == 400.0
    assert Game._right_search_until_door


def test_stale_vertical_escape_state_never_moves_up_or_down() -> None:
    _reset_search_state()
    game = Game(
        [
            {"door": {"xywh": [18.0, 339.0, 80.0, 100.0], "conf": 0.9}},
            {"player": {"xywh": [189.0, 435.0, 57.0, 89.0], "conf": 0.9}},
        ],
        width=800,
        height=600,
        direction="DOWN",
    )
    moves: list[str] = []

    def record_move(direction: str, **kwargs) -> str:
        moves.append(direction)
        return direction

    game._move = record_move  # type: ignore[method-assign]
    Game._vertical_escape_direction = "UP"
    Game._vertical_escape_target_y = 497.0
    Game._vertical_escape_source_direction = "DOWN"

    game.run()

    assert moves == ["RIGHT"]
    assert Game._vertical_escape_direction is None
    assert Game._right_search_until_door


def test_vertical_escape_right_search_ignores_selected_down_door() -> None:
    _reset_search_state()
    game = Game(
        [
            {"door": {"xywh": [572.0, 557.0, 82.0, 42.0], "conf": 0.9}},
        ],
        width=800,
        height=600,
        direction="DOWN",
        selected_door_center=(613.0, 578.0),
    )
    game._player_xywh = [449.0, 350.0, 0.0, 0.0]
    moves: list[str] = []

    def record_move(direction: str, **kwargs) -> str:
        moves.append(direction)
        return direction

    game._move = record_move  # type: ignore[method-assign]
    Game._right_search_anchor_x = 449.0
    Game._right_search_until = float("inf")
    Game._right_search_until_door = True

    assert game._continue_right_search_lock()

    assert moves == ["RIGHT"]
    assert Game._right_search_anchor_x == 449.0
    assert Game._right_search_until_door


def test_vertical_escape_right_search_moves_to_right_door_when_visible() -> None:
    _reset_search_state()
    game = Game(
        [
            {"door": {"xywh": [650.0, 320.0, 80.0, 120.0], "conf": 0.9}},
        ],
        width=800,
        height=600,
        direction="DOWN",
    )
    game._player_xywh = [500.0, 360.0, 0.0, 0.0]
    moves: list[str] = []

    def record_move(direction: str, **kwargs) -> str:
        moves.append(direction)
        return direction

    game._move = record_move  # type: ignore[method-assign]
    Game._right_search_anchor_x = 400.0
    Game._right_search_until = float("inf")
    Game._right_search_until_door = True

    assert game._continue_right_search_lock()

    assert moves == ["RIGHT"]
    assert Game._right_search_anchor_x == 400.0
    assert Game._right_search_until_door


def test_query_missing_holds_room_and_probe_attacks_instead_of_entering_door() -> None:
    _reset_search_state()
    game = Game(
        [
            {"player": {"xywh": [380.0, 260.0, 40.0, 80.0], "conf": 0.9}},
            {"door": {"xywh": [620.0, 250.0, 80.0, 130.0], "conf": 0.9}},
        ],
        width=800,
        height=600,
        direction=None,
        target_kind="query_missing",
    )
    moves: list[str] = []
    keys: list[str] = []

    def record_move(direction: str, **kwargs) -> str:
        moves.append(direction)
        return direction

    game._move = record_move  # type: ignore[method-assign]
    game._release_cached_action = lambda: None  # type: ignore[method-assign]
    game._key_press = lambda key: keys.append(key)  # type: ignore[method-assign]
    Game._last_attack_time = 0.0

    game.run()

    assert moves == []
    assert keys == ["right", "x"]


def test_vertical_escape_switches_to_right_immediately() -> None:
    _reset_search_state()
    game, moves = _game_with_recorder()
    game._player_xywh = [400.0, 500.0, 0.0, 0.0]
    Game._down_stuck_anchor = (400.0, 500.0)
    Game._down_stuck_since = time.time() - Game._down_stuck_seconds - 0.1

    game._fallback_route_move("DOWN")
    game._player_xywh = [400.0, 498.0, 0.0, 0.0]
    game.run()

    assert moves == ["RIGHT"]
    assert Game._vertical_escape_direction is None
    assert Game._right_search_until_door


def test_cached_right_up_stuck_nudges_down_before_right_search() -> None:
    _reset_search_state()
    game = Game(
        [{"player": {"xywh": [380.0, 40.0, 40.0, 80.0], "conf": 0.9}}],
        width=800,
        height=600,
        direction="RIGHT",
    )
    moves: list[str] = []

    def record_move(direction: str, **kwargs) -> str:
        moves.append(direction)
        return direction

    game._move = record_move  # type: ignore[method-assign]
    Game._action_cache = "RIGHT_UP"
    Game._up_stuck_anchor = (400.0, 80.0)
    Game._up_stuck_since = time.time() - Game._down_stuck_seconds - 0.1

    game.run()

    assert moves == ["RIGHT"]
    assert Game._vertical_escape_direction is None
    assert Game._right_search_until_door


def test_cached_right_down_stuck_nudges_up_before_right_search() -> None:
    _reset_search_state()
    game = Game(
        [{"player": {"xywh": [380.0, 460.0, 40.0, 80.0], "conf": 0.9}}],
        width=800,
        height=600,
        direction="RIGHT",
    )
    moves: list[str] = []

    def record_move(direction: str, **kwargs) -> str:
        moves.append(direction)
        return direction

    game._move = record_move  # type: ignore[method-assign]
    game._tap_direction = lambda direction, duration=None: None  # type: ignore[method-assign]
    Game._action_cache = "RIGHT_DOWN"
    Game._down_stuck_anchor = (400.0, 500.0)
    Game._down_stuck_since = time.time() - Game._down_stuck_seconds - 0.1

    game.run()

    assert moves == ["RIGHT"]
    assert Game._vertical_escape_direction is None
    assert Game._right_search_until_door


def test_generic_stuck_recovery_prefers_cached_vertical_escape() -> None:
    _reset_search_state()
    game = Game(
        [{"player": {"xywh": [380.0, 40.0, 40.0, 80.0], "conf": 0.9}}],
        width=800,
        height=600,
        direction="RIGHT",
    )
    moves: list[str] = []

    def record_move(direction: str, **kwargs) -> str:
        moves.append(direction)
        return direction

    game._move = record_move  # type: ignore[method-assign]
    game._tap_direction = lambda direction, duration=None: None  # type: ignore[method-assign]
    game._update_motion_state = lambda **kwargs: True  # type: ignore[method-assign]
    Game._action_cache = "RIGHT_UP"

    game.run()

    assert moves == ["RIGHT"]
    assert Game._vertical_escape_direction is None
    assert Game._right_search_until_door


def test_visible_entry_door_is_ignored_after_combat_dragged_player_left() -> None:
    _reset_search_state()
    game = Game(
        [
            {"player": {"xywh": [370.0, 320.0, 40.0, 80.0], "conf": 0.9}},
            {"door": {"xywh": [620.0, 250.0, 80.0, 130.0], "conf": 0.9}},
        ],
        width=800,
        height=600,
        direction="RIGHT",
    )
    moves: list[str] = []

    def record_move(direction: str, **kwargs) -> str:
        moves.append(direction)
        return direction

    game._move = record_move  # type: ignore[method-assign]
    Game._room_entry_position = (660.0, 315.0)
    Game._room_entry_time = time.time() - 8.0
    Game._flow_direction = "LEFT"
    Game._last_player_center = (390.0, 360.0)

    game.run()

    assert moves == ["RIGHT"]


def test_entry_side_route_is_not_blocked_when_target_is_explicit() -> None:
    _reset_search_state()
    game = Game(
        [{"player": {"xywh": [363.8671875, 277.734375, 72.0703125, 136.71875], "conf": 0.88}}],
        width=800,
        height=600,
        direction="LEFT",
        target_kind="query",
    )
    moves: list[str] = []

    def record_move(direction: str, **kwargs) -> str:
        moves.append(direction)
        return direction

    game._move = record_move  # type: ignore[method-assign]
    Game._room_entry_position = (400.0, 346.0)
    Game._room_entry_time = time.time()
    Game._flow_direction = "RIGHT"
    Game._last_player_center = (399.0, 346.0)

    game.run()

    assert moves == ["LEFT"]


def test_entry_side_door_is_allowed_when_route_explicitly_points_to_it() -> None:
    _reset_search_state()
    game = Game(
        [
            {"player": {"xywh": [363.8671875, 277.734375, 72.0703125, 136.71875], "conf": 0.88}},
            {"door": {"xywh": [0.0, 300.0, 80.0, 100.0], "conf": 0.9}},
        ],
        width=800,
        height=600,
        direction="LEFT",
        target_kind="query",
    )
    moves: list[str] = []

    def record_move(direction: str, **kwargs) -> str:
        moves.append(direction)
        return direction

    game._move = record_move  # type: ignore[method-assign]
    Game._room_entry_position = (400.0, 346.0)
    Game._room_entry_time = time.time()
    Game._flow_direction = "RIGHT"
    Game._last_player_center = (399.0, 346.0)

    game.run()

    assert moves == ["LEFT"]


def test_forward_door_selection_prefers_farther_right_door() -> None:
    _reset_search_state()
    game = Game(
        [
            {"player": {"xywh": [180.0, 320.0, 40.0, 80.0], "conf": 0.9}},
            {"door": {"xywh": [220.0, 420.0, 70.0, 120.0], "conf": 0.9}},
            {"door": {"xywh": [620.0, 420.0, 70.0, 120.0], "conf": 0.9}},
        ],
        width=800,
        height=600,
        direction="RIGHT",
    )
    moves: list[str] = []

    def record_move(direction: str, **kwargs) -> str:
        moves.append(direction)
        return direction

    game._move = record_move  # type: ignore[method-assign]

    game.run()

    assert moves == ["RIGHT"]


def test_move_to_door_uses_sustained_motion() -> None:
    _reset_search_state()
    game = Game([], width=800, height=600, direction="RIGHT")
    game._player_xywh = [200.0, 200.0, 0.0, 0.0]
    moves: list[tuple[str, bool]] = []

    def record_move(direction: str, is_slow: bool = False, **kwargs) -> str:
        moves.append((direction, is_slow))
        return direction

    game._move = record_move  # type: ignore[method-assign]
    game._move_to_door([300.0, 200.0, 0.0, 0.0])

    assert moves == [("RIGHT", True)]


def test_sustained_same_direction_reasserts_key_after_short_interval(monkeypatch) -> None:
    _reset_search_state()
    game = Game([], width=800, height=600, direction="RIGHT")
    presses: list[str] = []
    releases: list[str] = []

    monkeypatch.setattr("dnf.game.pydirectinput.keyDown", lambda key: presses.append(key))
    monkeypatch.setattr("dnf.game.pydirectinput.keyUp", lambda key: releases.append(key))

    Game._action_cache_time = 1.0
    monkeypatch.setattr("dnf.game.time.time", lambda: 1.05)
    assert game._move("RIGHT", is_slow=True, _action_cache="RIGHT") == "RIGHT"
    assert presses == []
    assert releases == []

    monkeypatch.setattr("dnf.game.time.time", lambda: 1.13)
    assert game._move("RIGHT", is_slow=True, _action_cache="RIGHT") == "RIGHT"
    assert presses == ["right"]
    assert releases == []


def test_diagonal_route_hint_uses_right_door_instead_of_fallbacking_up() -> None:
    _reset_search_state()
    game = Game(
        [
            {"door": {"xywh": [699.0, 468.0, 84.0, 81.0], "conf": 0.9}},
            {"player": {"xywh": [560.0, 300.0, 84.0, 147.0], "conf": 0.9}},
        ],
        width=800,
        height=600,
        direction="RIGHT_UP",
    )
    moves: list[str] = []

    def record_move(direction: str, **kwargs) -> str:
        moves.append(direction)
        return direction

    game._move = record_move  # type: ignore[method-assign]

    game.run()

    assert moves == ["RIGHT"]


def test_diagonal_route_hint_still_moves_straight_to_right_door_when_door_is_high() -> None:
    _reset_search_state()
    game = Game(
        [
            {"door": {"xywh": [721.0, 220.0, 78.0, 101.0], "conf": 0.9}},
            {"player": {"xywh": [417.0, 337.0, 57.0, 116.0], "conf": 0.9}},
        ],
        width=800,
        height=600,
        direction="RIGHT_UP",
    )
    moves: list[str] = []

    def record_move(direction: str, **kwargs) -> str:
        moves.append(direction)
        return direction

    game._move = record_move  # type: ignore[method-assign]

    game.run()

    assert moves == ["RIGHT"]


def test_horizontal_route_moves_straight_to_close_right_door_without_vertical_wobble() -> None:
    _reset_search_state()
    game = Game(
        [
            {"door": {"xywh": [505.0, 410.0, 78.0, 101.0], "conf": 0.9}},
            {"player": {"xywh": [417.0, 337.0, 57.0, 116.0], "conf": 0.9}},
        ],
        width=800,
        height=600,
        direction="RIGHT",
    )
    moves: list[str] = []

    def record_move(direction: str, **kwargs) -> str:
        moves.append(direction)
        return direction

    game._move = record_move  # type: ignore[method-assign]

    game.run()

    assert moves == ["RIGHT"]


def test_diagonal_route_hint_uses_cardinal_when_door_center_is_not_above() -> None:
    _reset_search_state()
    game = Game(
        [
            {"door": {"xywh": [721.0, 354.0, 78.0, 101.0], "conf": 0.9}},
            {"player": {"xywh": [417.0, 337.0, 57.0, 116.0], "conf": 0.9}},
        ],
        width=800,
        height=600,
        direction="RIGHT_UP",
    )
    moves: list[str] = []

    def record_move(direction: str, **kwargs) -> str:
        moves.append(direction)
        return direction

    game._move = record_move  # type: ignore[method-assign]

    game.run()

    assert moves == ["RIGHT"]


def test_diagonal_fallback_keeps_full_route_direction_when_no_matching_door() -> None:
    _reset_search_state()
    game = Game(
        [
            {"door": {"xywh": [201.0, 324.0, 80.0, 105.0], "conf": 0.9}},
            {"player": {"xywh": [776.0, 283.0, 24.0, 133.0], "conf": 0.9}},
        ],
        width=800,
        height=600,
        direction="RIGHT_UP",
    )
    moves: list[str] = []

    def record_move(direction: str, **kwargs) -> str:
        moves.append(direction)
        return direction

    game._move = record_move  # type: ignore[method-assign]

    game.run()

    assert moves == ["RIGHT_UP"]


def test_same_diagonal_route_keeps_compatible_cardinal_cache() -> None:
    _reset_search_state()
    game = Game([], width=800, height=600, direction="RIGHT_UP")
    Game._active_route_direction = "RIGHT_UP"
    Game._action_cache = "RIGHT"
    released: list[bool] = []

    def record_release() -> None:
        released.append(True)
        Game._action_cache = None

    game._release_cached_action = record_release  # type: ignore[method-assign]

    game._sync_route_direction_state()

    assert released == []


def test_same_diagonal_route_releases_incompatible_cardinal_cache() -> None:
    _reset_search_state()
    game = Game([], width=800, height=600, direction="RIGHT_UP")
    Game._active_route_direction = "RIGHT_UP"
    Game._action_cache = "LEFT"
    released: list[bool] = []

    def record_release() -> None:
        released.append(True)
        Game._action_cache = None

    game._release_cached_action = record_release  # type: ignore[method-assign]

    game._sync_route_direction_state()

    assert released == [True]


def test_pickup_prioritizes_y_axis_inside_x_deadzone() -> None:
    _reset_search_state()
    game, moves = _game_with_recorder()
    game._player_xywh = [400.0, 300.0, 0.0, 0.0]

    game._pick_up([455.0, 360.0, 0.0, 0.0])

    assert moves == ["DOWN"]


def test_pickup_uses_x_axis_when_y_aligned_but_x_not_close_enough() -> None:
    _reset_search_state()
    game, moves = _game_with_recorder()
    game._player_xywh = [400.0, 300.0, 0.0, 0.0]

    game._pick_up([455.0, 306.0, 0.0, 0.0])

    assert moves == ["RIGHT"]


def test_pickup_presses_key_only_when_x_and_y_are_tightly_aligned() -> None:
    _reset_search_state()
    game, moves = _game_with_recorder()
    game._player_xywh = [400.0, 300.0, 0.0, 0.0]
    keys: list[str] = []
    game._release_cached_action = lambda: None  # type: ignore[method-assign]
    game._key_press = lambda key: keys.append(key)  # type: ignore[method-assign]

    game._pick_up([414.0, 306.0, 0.0, 0.0])

    assert moves == []
    assert keys == ["x"]


def test_pickup_presses_key_when_money_is_underfoot_without_vertical_jitter() -> None:
    _reset_search_state()
    game, moves = _game_with_recorder()
    game._player_xywh = [453.90625, 425.09765625, 0.0, 0.0]
    keys: list[str] = []
    game._release_cached_action = lambda: None  # type: ignore[method-assign]
    game._key_press = lambda key: keys.append(key)  # type: ignore[method-assign]

    game._pick_up([461.328125, 402.734375, 55.46875, 21.875])

    assert moves == []
    assert keys == ["x"]


def test_pickup_uses_x_axis_only_when_item_is_far_outside_y_sweep_range() -> None:
    _reset_search_state()
    game, moves = _game_with_recorder()
    game._player_xywh = [400.0, 300.0, 0.0, 0.0]

    game._pick_up([540.0, 306.0, 0.0, 0.0])

    assert moves == ["RIGHT"]


def test_pickup_log_case_uses_x_axis_for_nearby_money() -> None:
    _reset_search_state()
    game, moves = _game_with_recorder()
    game._player_xywh = [354.1015625, 405.46875, 0.0, 0.0]

    game._pick_up([409.765625, 402.734375, 54.6875, 30.46875])

    assert moves == ["RIGHT"]


def test_route_money_far_below_does_not_interrupt_horizontal_route() -> None:
    _reset_search_state()
    game = Game(
        [
            {"money": {"xywh": [450.0, 455.859375, 56.25, 23.4375], "conf": 0.83}},
            {"player": {"xywh": [413.28125, 335.546875, 74.21875, 120.3125], "conf": 0.8}},
        ],
        width=800,
        height=600,
        direction="RIGHT",
    )
    moves: list[str] = []

    def record_move(direction: str, **kwargs) -> str:
        moves.append(direction)
        return direction

    game._move = record_move  # type: ignore[method-assign]

    game.run()

    assert moves == ["RIGHT"]


def test_route_money_close_underfoot_can_interrupt_route() -> None:
    _reset_search_state()
    game = Game(
        [
            {"money": {"xywh": [455.0, 410.0, 56.25, 23.4375], "conf": 0.83}},
            {"player": {"xywh": [413.28125, 335.546875, 74.21875, 120.3125], "conf": 0.8}},
        ],
        width=800,
        height=600,
        direction="RIGHT",
    )
    moves: list[str] = []

    def record_move(direction: str, **kwargs) -> str:
        moves.append(direction)
        return direction

    game._move = record_move  # type: ignore[method-assign]

    game.run()

    assert moves == ["DOWN"]


def test_vertical_route_uses_only_visible_nonmatching_door() -> None:
    _reset_search_state()
    game = Game(
        [
            {"player": {"xywh": [413.28125, 243.359375, 78.125, 133.59375], "conf": 0.89}},
            {"door": {"xywh": [600.78125, 312.890625, 82.8125, 97.65625], "conf": 0.88}},
        ],
        width=800,
        height=600,
        direction="UP",
    )
    moves: list[str] = []

    def record_move(direction: str, **kwargs) -> str:
        moves.append(direction)
        return direction

    game._move = record_move  # type: ignore[method-assign]

    game.run()

    assert moves == ["RIGHT_DOWN"]
