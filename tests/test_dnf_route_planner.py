import json
import time

import cv2
import numpy as np

from dnf.door_strategy import DoorCandidate, choose_best_door
from dnf.game import Game
from dnf.map_specs import load_map_specs
from dnf.main import (
    DEFAULT_FIXED_ROUTE,
    RouteDebugSaveState,
    _has_room_action_objects,
    _parse_non_negative_int,
    _parse_optional_positive_int,
    _parse_positive_int,
    _resolve_game_direction,
    _route_debug_issue_reason,
    _route_debug_save_reason,
    _should_save_route_debug,
    build_runtime_config,
)
from dnf.minimap_nav import MiniMapNavigator, RouteSnapshot
from dnf.route_debug import analyze_debug_payload, resolve_debug_json_path, summarize_debug_file, summarize_debug_payload
from dnf.route_check import DetectionFrameResult, analyze_frame_sequence
from dnf.route_acceptance import analyze_acceptance_payload, build_acceptance_report
from dnf.route_advice import build_route_advice
from dnf.route_probe import analyze_screenshot_file, main as route_probe_main
from dnf.route_planner import nearest_reachable_room, next_direction, shortest_path
from dnf.route_runtime import RouteProgressTracker
from dnf.route_sequence_debug import analyze_debug_sequence, summarize_debug_sequence


def test_route_planner_uses_bfs_without_changing_grid_shape():
    grid = [
        [0, 1, 0],
        [0, 1, 0],
        [0, 0, 0],
    ]

    path = shortest_path(grid, (0, 0), (0, 2), priority="right")

    assert path == [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (1, 2), (0, 2)]
    assert len(grid) == 3
    assert len(grid[0]) == 3


def test_next_direction_from_bfs_path():
    grid = [
        [0, 1, 0],
        [0, 1, 0],
        [0, 0, 0],
    ]

    assert next_direction(grid, (0, 0), (0, 2), priority="right") == "down"


def test_nearest_reachable_room_skips_visited_rooms():
    grid = [
        [0, 0, 0],
        [1, 1, 0],
        [0, 0, 0],
    ]

    target = nearest_reachable_room(grid, (0, 0), blocked_rooms=[(0, 0), (0, 1)], priority="right")

    assert target == (0, 2)


def test_runtime_config_uses_safe_defaults_for_bad_env(monkeypatch):
    monkeypatch.setenv("DNF_CAPTURE_WIDTH", "bad")
    monkeypatch.setenv("DNF_CAPTURE_HEIGHT", "-1")
    monkeypatch.setenv("DNF_DEBUG_ROUTE_EVERY", "0")
    monkeypatch.setenv("DNF_DEBUG_MINIMAP", "true")
    monkeypatch.setenv("DNF_DRY_RUN", "1")
    monkeypatch.setenv("DNF_MAX_FRAMES", "3")
    monkeypatch.setenv("DNF_ROUTE_ONLY", "1")
    monkeypatch.setenv("DNF_ALLOW_FIXED_FALLBACK", "1")
    monkeypatch.setenv("DNF_ROUTE_STUCK_FRAMES", "4")

    config = build_runtime_config()

    assert _parse_positive_int("12", 30) == 12
    assert _parse_positive_int("bad", 30) == 30
    assert _parse_non_negative_int("0", 6) == 0
    assert _parse_non_negative_int("-1", 6) == 6
    assert config.width == 1600
    assert config.height == 900
    assert config.debug_route_every == 30
    assert config.debug_minimap is True
    assert config.dry_run is True
    assert config.max_frames == 3
    assert config.route_only is True
    assert config.allow_fixed_fallback is True
    assert config.route_stuck_frames == 4
    assert _parse_optional_positive_int("bad") is None
    assert _parse_optional_positive_int("0") is None


def test_resolve_game_direction_requires_smart_route_by_default(monkeypatch):
    monkeypatch.delenv("DNF_ALLOW_FIXED_FALLBACK", raising=False)
    config = build_runtime_config()

    assert _resolve_game_direction("RIGHT", config) == "RIGHT"
    assert _resolve_game_direction(None, config) is None


def test_resolve_game_direction_can_allow_fixed_fallback(monkeypatch):
    monkeypatch.setenv("DNF_ALLOW_FIXED_FALLBACK", "1")
    config = build_runtime_config()

    assert _resolve_game_direction(None, config) == DEFAULT_FIXED_ROUTE


def test_room_action_objects_allow_combat_without_route_direction():
    assert _has_room_action_objects([{"monster": {"xywh": [1, 2, 3, 4]}}]) is True
    assert _has_room_action_objects([{"goods": {"xywh": [1, 2, 3, 4]}}]) is True
    assert _has_room_action_objects([{"door": {"xywh": [1, 2, 3, 4]}}]) is False
    assert _has_room_action_objects([{"player": {"xywh": [1, 2, 3, 4]}}]) is False


def test_route_debug_save_schedule_includes_first_frame():
    assert _should_save_route_debug(1, 30) is True
    assert _should_save_route_debug(2, 30) is False
    assert _should_save_route_debug(30, 30) is True


def _route_snapshot(**overrides):
    values = {
        "current_room": (0, 0),
        "boss_room": None,
        "query_room": (0, 2),
        "elite_room": None,
        "down_room": None,
        "target_kind": "query",
        "target_room": (0, 2),
        "route_path": [(0, 0), (0, 1), (0, 2)],
        "route_status": "moving",
        "next_room_direction": "right",
        "selected_door_center": (740.0, 340.0),
        "detector_enabled": True,
        "detection_objects_count": 2,
        "door_candidates_count": 1,
        "player_detected": True,
        "debug_scores": {"hero": 0.9, "query": 0.9},
    }
    values.update(overrides)
    return RouteSnapshot(**values)


def test_route_debug_issue_reason_detects_route_and_door_failures():
    assert _route_debug_issue_reason(_route_snapshot(route_status="missing_current")) == "missing_current"
    assert _route_debug_issue_reason(_route_snapshot(route_status="unreachable")) == "unreachable"
    assert (
        _route_debug_issue_reason(
            _route_snapshot(selected_door_center=None, door_candidates_count=0)
        )
        == "door_not_detected"
    )
    assert (
        _route_debug_issue_reason(
            _route_snapshot(selected_door_center=None, door_candidates_count=1)
        )
        == "door_not_selected"
    )
    assert _route_debug_issue_reason(_route_snapshot(), recovery_active=True) == "route_recovery_active"


def test_route_debug_save_reason_prefers_issues_over_schedule():
    assert _route_debug_save_reason(_route_snapshot(), 2, 30) is None
    assert _route_debug_save_reason(_route_snapshot(), 30, 30) == "scheduled"
    assert (
        _route_debug_save_reason(_route_snapshot(route_status="missing_target"), 30, 30)
        == "missing_target"
    )


def test_route_debug_save_reason_throttles_repeated_issue():
    state = RouteDebugSaveState()
    snapshot = _route_snapshot(route_status="missing_current")

    assert _route_debug_save_reason(snapshot, 2, 5, state=state) == "missing_current"
    assert _route_debug_save_reason(snapshot, 3, 5, state=state) is None
    assert _route_debug_save_reason(snapshot, 7, 5, state=state) == "missing_current"
    assert (
        _route_debug_save_reason(_route_snapshot(route_status="missing_target"), 8, 5, state=state)
        == "missing_target"
    )
    assert _route_debug_save_reason(_route_snapshot(), 9, 5, state=state) is None
    assert state.last_issue_reason is None


def test_choose_best_door_rejects_wrong_side_door():
    player = (700.0, 310.0)
    left_door = DoorCandidate(bbox=[80, 280, 80, 140], center=(120.0, 350.0))
    low_door = DoorCandidate(bbox=[720, 390, 80, 140], center=(760.0, 460.0))

    selected = choose_best_door([left_door, low_door], player, expected_direction="up")

    assert selected is None


def test_choose_best_door_uses_clear_right_door_for_vertical_route():
    player = (400.0, 330.0)
    right_door = DoorCandidate(bbox=[617, 289, 80, 93], center=(657.0, 335.0))

    selected = choose_best_door([right_door], player, expected_direction="up")

    assert selected is right_door


def test_top_wall_stuck_escapes_down_then_right():
    class DryGame(Game):
        def __init__(self):
            super().__init__([], 800, 600, "UP")
            self._player_xywh = [420.0, 300.0, 50.0, 120.0]
            self.actions = []

        def _move(self, direction, is_slow=False, _action_cache=None, press_time=0.1, release_time=0.1):
            self.actions.append(("move", direction))
            return direction

        def _tap_direction(self, direction, duration=0.12):
            self.actions.append(("tap", direction, duration))

        def _release_cached_action(self):
            self.actions.append(("release",))
            Game._action_cache = None

    game = DryGame()
    Game._action_cache = "UP"
    Game._top_wall_escape_until = 0.0
    Game._top_wall_escape_origin_x = None
    Game._top_wall_tracking = True
    Game._top_wall_stuck_start = time.time() - 0.8
    Game._top_wall_stuck_origin = (420.0, 300.0)

    assert game._handle_top_wall_stuck() is True
    assert game.actions == [
        ("release",),
        ("tap", "DOWN", Game._top_wall_escape_down_seconds),
        ("move", "RIGHT"),
    ]
    assert Game._action_cache == "RIGHT"
    Game._top_wall_escape_until = 0.0
    Game._top_wall_escape_origin_x = None


def test_game_does_not_move_to_door_without_route_direction():
    class DryGame(Game):
        def __init__(self, objects):
            super().__init__(objects, 800, 600, None)
            self.actions = []

        def _move(self, direction, is_slow=False, _action_cache=None, press_time=0.1, release_time=0.1):
            self.actions.append(("move", direction))
            return direction

    Game._pre_player = None
    Game._player = None
    Game._action_cache = None
    game = DryGame(
        [
            {"player": {"xywh": [380, 280, 80, 120], "conf": 0.99}},
            {"door": {"xywh": [700, 280, 80, 120], "conf": 0.88}},
        ]
    )

    game.run()

    assert game.actions == []
    assert Game._action_cache is None


def test_game_without_route_direction_can_still_attack_monster():
    class DryGame(Game):
        def __init__(self, objects):
            super().__init__(objects, 800, 600, None)
            self.attacks = []
            self.actions = []

        def _move(self, direction, is_slow=False, _action_cache=None, press_time=0.1, release_time=0.1):
            self.actions.append(("move", direction))
            return direction

        def _kill_monster(self, obj_box):
            self.attacks.append(tuple(obj_box))

    Game._pre_player = None
    Game._player = None
    Game._action_cache = None
    game = DryGame(
        [
            {"player": {"xywh": [380, 280, 80, 120], "conf": 0.99}},
            {"monster": {"xywh": [420, 280, 80, 120], "conf": 0.88}},
        ]
    )

    game.run()

    assert game.attacks
    assert game.actions == []


def test_game_force_route_move_uses_raw_direction_before_door_tracking():
    class DryGame(Game):
        def __init__(self, objects):
            super().__init__(objects, 800, 600, "RIGHT", force_route_move=True)
            self.actions = []

        def _move(self, direction, is_slow=False, _action_cache=None, press_time=0.1, release_time=0.1):
            self.actions.append(("move", direction, is_slow))
            return direction

        def _move_to_door(self, obj_box):
            self.actions.append(("door", tuple(obj_box)))

    Game._pre_player = None
    Game._player = None
    Game._action_cache = None
    game = DryGame(
        [
            {"player": {"xywh": [380, 280, 80, 120], "conf": 0.99}},
            {"door": {"xywh": [700, 280, 80, 120], "conf": 0.88}},
        ]
    )

    game.run()

    assert game.actions == [("move", "RIGHT", True)]


def test_route_progress_tracker_enables_recovery_after_repeated_moving_route():
    tracker = RouteProgressTracker(stuck_frames=3)
    snapshot = {
        "route_status": "moving",
        "current_room": [0, 0],
        "target_room": [0, 2],
        "next_room_direction": "right",
    }

    assert tracker.update(snapshot).recovery_active is False
    assert tracker.update(snapshot).recovery_active is False
    decision = tracker.update(snapshot)

    assert decision.recovery_active is True
    assert decision.repeated_frames == 3
    assert "0,0->0,2 right" in decision.recovery_reason


def test_route_progress_tracker_resets_when_room_changes_or_not_moving():
    tracker = RouteProgressTracker(stuck_frames=2)
    moving = {
        "route_status": "moving",
        "current_room": [0, 0],
        "target_room": [0, 2],
        "next_room_direction": "right",
    }
    changed = {
        "route_status": "moving",
        "current_room": [0, 1],
        "target_room": [0, 2],
        "next_room_direction": "right",
    }

    assert tracker.update(moving).repeated_frames == 1
    assert tracker.update(changed).repeated_frames == 1
    assert tracker.update({"route_status": "at_target"}).repeated_frames == 0


def test_minimap_navigator_builds_route_snapshot_from_real_templates():
    nav = MiniMapNavigator("generic")
    frame = np.zeros((900, 1600, 3), dtype=np.uint8)
    _, room_rect = nav._spec_rects(frame, nav.spec)
    rx1, ry1, rx2, ry2 = room_rect

    def paste_marker(name, row, col):
        template = nav.templates[name]
        height, width = template.shape[:2]
        center_x = int(rx1 + (rx2 - rx1) * (col + 0.5) / nav.spec.cols)
        center_y = int(ry1 + (ry2 - ry1) * (row + 0.5) / nav.spec.rows)
        x1 = center_x - width // 2
        y1 = center_y - height // 2
        frame[y1:y1 + height, x1:x1 + width] = template

    paste_marker("hero", 0, 0)
    paste_marker("query", 0, 2)
    objects = [
        {"player": {"xywh": [400, 280, 80, 120], "conf": 0.99}},
        {"door": {"xywh": [700, 280, 80, 120], "conf": 0.88}},
    ]

    snapshot = nav.build_route_snapshot(frame, objects)

    assert snapshot.current_room == (0, 0)
    assert snapshot.query_room == (0, 2)
    assert snapshot.route_path == [(0, 0), (0, 1), (0, 2)]
    assert snapshot.route_status == "moving"
    assert snapshot.next_room_direction == "right"
    assert snapshot.selected_door_center == (740.0, 340.0)


def test_minimap_navigator_explores_unvisited_room_when_no_target_marker():
    nav = MiniMapNavigator("generic")
    frame = np.zeros((900, 1600, 3), dtype=np.uint8)
    _, room_rect = nav._spec_rects(frame, nav.spec)
    rx1, ry1, rx2, ry2 = room_rect
    template = nav.templates["hero"]
    height, width = template.shape[:2]
    center_x = int(rx1 + (rx2 - rx1) * 0.5 / nav.spec.cols)
    center_y = int(ry1 + (ry2 - ry1) * 0.5 / nav.spec.rows)
    x1 = center_x - width // 2
    y1 = center_y - height // 2
    frame[y1:y1 + height, x1:x1 + width] = template
    objects = [
        {"player": {"xywh": [400, 280, 80, 120], "conf": 0.99}},
        {"door": {"xywh": [700, 280, 80, 120], "conf": 0.88}},
    ]

    snapshot = nav.build_route_snapshot(frame, objects)

    assert snapshot.current_room == (0, 0)
    assert snapshot.target_kind == "explore"
    assert snapshot.target_room == (0, 1)
    assert snapshot.route_path == [(0, 0), (0, 1)]
    assert snapshot.route_status == "moving"
    assert snapshot.next_room_direction == "right"
    assert snapshot.selected_door_center == (740.0, 340.0)


def test_minimap_navigator_stays_when_target_is_current_room():
    class SameRoomNavigator(MiniMapNavigator):
        def detect_room_markers(self, frame):
            return {
                "current_room": (1, 1),
                "boss_room": None,
                "query_room": (1, 1),
                "elite_room": None,
                "down_room": None,
                "current_marker": None,
                "boss_marker": None,
                "query_marker": None,
                "elite_marker": None,
                "down_marker": None,
            }

        def get_debug_scores(self, frame):
            return {"hero": 0.9, "query": 0.9}

    nav = SameRoomNavigator("generic")
    frame = np.zeros((900, 1600, 3), dtype=np.uint8)

    snapshot = nav.build_route_snapshot(frame, [])
    summary = summarize_debug_payload(
        {
            "map_name": "generic",
            "rows": nav.spec.rows,
            "cols": nav.spec.cols,
            "room_grid": nav.spec.room_grid,
            "visited_rooms": [[1, 1]],
            "snapshot": snapshot.to_dict(),
        }
    )

    assert snapshot.target_kind == "query"
    assert snapshot.target_room == (1, 1)
    assert snapshot.route_path == [(1, 1)]
    assert snapshot.route_status == "at_target"
    assert snapshot.next_room_direction is None
    assert analyze_debug_payload({"snapshot": snapshot.to_dict()}) == []
    assert "\u8def\u7ebf\u6b65\u6570: 0" in summary


def test_minimap_navigator_resets_explore_memory_after_all_rooms_visited():
    nav = MiniMapNavigator("generic")
    nav._visited_rooms = {
        (row, col)
        for row, rooms in enumerate(nav.spec.room_grid)
        for col, value in enumerate(rooms)
        if value == 0
    }

    target = nav._pick_explore_target((0, 0))

    assert target == (0, 1)
    assert nav._visited_rooms == {(0, 0)}


def test_minimap_rect_env_overrides_crop_and_room(monkeypatch):
    nav = MiniMapNavigator("generic")
    frame = np.zeros((900, 1600, 3), dtype=np.uint8)
    monkeypatch.setenv("DNF_MINIMAP_GENERIC_CROP_1067", "900,50,1040,140")
    monkeypatch.setenv("DNF_MINIMAP_GENERIC_ROOM_1067", "910,70,1030,130")

    crop_rect, room_rect = nav._spec_rects(frame, nav.spec)

    assert crop_rect == (900, 50, 1040, 140)
    assert room_rect == (910, 70, 1030, 130)


def test_minimap_rect_env_can_override_crop_without_losing_default_room(monkeypatch):
    nav = MiniMapNavigator("generic")
    frame = np.zeros((600, 800, 3), dtype=np.uint8)
    monkeypatch.setenv("DNF_MINIMAP_CROP_800", "1,2,101,102")

    crop_rect, room_rect = nav._spec_rects(frame, nav.spec)

    assert crop_rect == (1, 2, 101, 102)
    assert room_rect == nav.spec.room_rect_800


def test_minimap_marker_threshold_env_overrides(monkeypatch):
    nav = MiniMapNavigator("generic")
    monkeypatch.setenv("DNF_MINIMAP_HERO_THRESHOLD", "0.42")
    monkeypatch.setenv("DNF_MINIMAP_GENERIC_QUERY_THRESHOLD", "0.33")
    monkeypatch.setenv("DNF_MINIMAP_BOSS_THRESHOLD", "0")

    thresholds = nav.marker_thresholds()

    assert thresholds["hero"] == 0.42
    assert thresholds["query"] == 0.33
    assert thresholds["boss"] == 0.0


def test_minimap_marker_threshold_env_rejects_invalid_value(monkeypatch):
    nav = MiniMapNavigator("generic")
    monkeypatch.setenv("DNF_MINIMAP_HERO_THRESHOLD", "1.2")

    try:
        nav.marker_thresholds()
    except ValueError as exc:
        assert "DNF_MINIMAP_HERO_THRESHOLD" in str(exc)
    else:
        raise AssertionError("expected invalid threshold to raise ValueError")


def test_external_map_spec_file_can_define_blocked_rooms(tmp_path, monkeypatch):
    spec_path = tmp_path / "maps.json"
    spec_path.write_text(
        json.dumps(
            {
                "maps": {
                    "detour": {
                        "base": "generic",
                        "rows": 3,
                        "cols": 3,
                        "room_grid": [
                            [0, 1, 0],
                            [0, 1, 0],
                            [0, 0, 0],
                        ],
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("DNF_MAP_SPEC_FILE", str(spec_path))
    specs = load_map_specs()
    nav = MiniMapNavigator("detour")
    frame = np.zeros((900, 1600, 3), dtype=np.uint8)
    _, room_rect = nav._spec_rects(frame, nav.spec)
    rx1, ry1, rx2, ry2 = room_rect

    def paste_marker(name, row, col):
        template = nav.templates[name]
        height, width = template.shape[:2]
        center_x = int(rx1 + (rx2 - rx1) * (col + 0.5) / nav.spec.cols)
        center_y = int(ry1 + (ry2 - ry1) * (row + 0.5) / nav.spec.rows)
        x1 = center_x - width // 2
        y1 = center_y - height // 2
        frame[y1:y1 + height, x1:x1 + width] = template

    paste_marker("hero", 0, 0)
    paste_marker("query", 0, 2)
    snapshot = nav.build_route_snapshot(frame, [])

    assert specs["detour"].room_grid[0][1] == 1
    assert nav.map_name == "detour"
    assert snapshot.current_room == (0, 0)
    assert snapshot.target_room == (0, 2)
    assert snapshot.route_path == [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (1, 2), (0, 2)]
    assert snapshot.route_status == "moving"
    assert snapshot.next_room_direction == "down"


def test_minimap_navigator_reports_unreachable_route(tmp_path, monkeypatch):
    spec_path = tmp_path / "maps.json"
    spec_path.write_text(
        json.dumps(
            {
                "maps": {
                    "blocked": {
                        "base": "generic",
                        "rows": 1,
                        "cols": 3,
                        "room_grid": [[0, 1, 0]],
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("DNF_MAP_SPEC_FILE", str(spec_path))
    nav = MiniMapNavigator("blocked")
    frame = np.zeros((900, 1600, 3), dtype=np.uint8)
    _, room_rect = nav._spec_rects(frame, nav.spec)
    rx1, ry1, rx2, ry2 = room_rect

    def paste_marker(name, row, col):
        template = nav.templates[name]
        height, width = template.shape[:2]
        center_x = int(rx1 + (rx2 - rx1) * (col + 0.5) / nav.spec.cols)
        center_y = int(ry1 + (ry2 - ry1) * (row + 0.5) / nav.spec.rows)
        x1 = center_x - width // 2
        y1 = center_y - height // 2
        frame[y1:y1 + height, x1:x1 + width] = template

    paste_marker("hero", 0, 0)
    paste_marker("query", 0, 2)
    snapshot = nav.build_route_snapshot(frame, [])
    issues = analyze_debug_payload({"snapshot": snapshot.to_dict()})

    assert snapshot.route_status == "unreachable"
    assert snapshot.route_path is None
    assert snapshot.next_room_direction is None
    assert any("\u4e0d\u8fde\u901a" in issue for issue in issues)


def test_minimap_navigator_saves_route_debug_package(tmp_path):
    nav = MiniMapNavigator("generic")
    frame = np.zeros((900, 1600, 3), dtype=np.uint8)
    _, room_rect = nav._spec_rects(frame, nav.spec)
    rx1, ry1, rx2, ry2 = room_rect

    def paste_marker(name, row, col):
        template = nav.templates[name]
        height, width = template.shape[:2]
        center_x = int(rx1 + (rx2 - rx1) * (col + 0.5) / nav.spec.cols)
        center_y = int(ry1 + (ry2 - ry1) * (row + 0.5) / nav.spec.rows)
        x1 = center_x - width // 2
        y1 = center_y - height // 2
        frame[y1:y1 + height, x1:x1 + width] = template

    paste_marker("hero", 0, 0)
    paste_marker("query", 0, 2)
    objects = [
        {"player": {"xywh": [400, 280, 80, 120], "conf": 0.99}},
        {"door": {"xywh": [700, 280, 80, 120], "conf": 0.88}},
    ]
    snapshot = nav.build_route_snapshot(frame, objects)

    json_path = nav.save_route_debug(frame, snapshot, tmp_path, frame_index=7, debug_reason="scheduled")
    payload = json.loads(json_path.read_text(encoding="utf-8"))

    assert json_path.exists()
    assert json_path.with_suffix(".png").exists()
    assert json_path.with_name(f"{json_path.stem}_frame.png").exists()
    assert payload["map_name"] == "generic"
    assert payload["frame_index"] == 7
    assert payload["debug_reason"] == "scheduled"
    assert payload["debug_minimap_image"] == json_path.with_suffix(".png").name
    assert payload["debug_frame_image"] == json_path.with_name(f"{json_path.stem}_frame.png").name
    assert payload["marker_thresholds"]["hero"] == nav.marker_thresholds()["hero"]
    assert "current" in payload["marker_centers"]
    assert "query" in payload["marker_centers"]
    assert payload["room_grid"] == nav.spec.room_grid
    assert payload["snapshot"]["current_room"] == [0, 0]
    assert payload["snapshot"]["target_room"] == [0, 2]
    assert payload["snapshot"]["route_path"] == [[0, 0], [0, 1], [0, 2]]
    assert payload["snapshot"]["route_status"] == "moving"
    assert payload["snapshot"]["next_room_direction"] == "right"
    summary = summarize_debug_file(json_path)
    assert "\u8c03\u8bd5 JSON:" in summary
    assert str(json_path) in summary
    assert "\u5c0f\u5730\u56fe\u56fe\u7247:" in summary
    assert str(json_path.with_suffix(".png")) in summary
    assert "\u5168\u5c4f\u6807\u6ce8\u56fe:" in summary
    assert str(json_path.with_name(f"{json_path.stem}_frame.png")) in summary
    assert "\u623f\u95f4\u7f51\u683c:" in summary
    assert "\u5e27\u5e8f\u53f7: 7" in summary
    assert "\u4fdd\u5b58\u539f\u56e0: scheduled" in summary
    assert "\u6a21\u677f\u9608\u503c:" in summary
    assert "\u6807\u8bb0\u4e2d\u5fc3:" in summary
    assert "\u8def\u7ebf\u72b6\u6001: moving" in summary
    assert "\u8def\u7ebf\u6b65\u6570: 2" in summary
    assert "\u4e0d\u53ef\u8d70\u623f\u95f4\u6570: 0" in summary
    assert "\u6682\u672a\u53d1\u73b0\u660e\u663e\u95ee\u9898" in summary


def test_auto_map_scores_are_saved_in_route_debug_package(tmp_path):
    nav = MiniMapNavigator("auto")
    frame = np.zeros((900, 1600, 3), dtype=np.uint8)
    generic = nav.map_specs["generic"]
    _, room_rect = nav._spec_rects(frame, generic)
    rx1, ry1, rx2, ry2 = room_rect

    def paste_marker(name, row, col):
        template = nav.templates[name]
        height, width = template.shape[:2]
        center_x = int(rx1 + (rx2 - rx1) * (col + 0.5) / generic.cols)
        center_y = int(ry1 + (ry2 - ry1) * (row + 0.5) / generic.rows)
        x1 = center_x - width // 2
        y1 = center_y - height // 2
        frame[y1:y1 + height, x1:x1 + width] = template

    paste_marker("hero", 0, 0)
    paste_marker("query", 0, 2)

    snapshot = nav.build_route_snapshot(frame, [])
    json_path = nav.save_route_debug(frame, snapshot, tmp_path)
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    summary = summarize_debug_file(json_path)

    assert payload["auto_map"] is True
    assert "generic" in payload["auto_map_scores"]
    assert "haibolun" in payload["auto_map_scores"]
    assert "\u81ea\u52a8\u9009\u56fe\u5206\u6570:" in summary


def test_route_debug_reports_missing_door_and_low_scores():
    payload = {
        "map_name": "generic",
        "visited_rooms": [[0, 0]],
        "snapshot": {
            "current_room": [0, 0],
            "target_kind": "query",
            "target_room": [0, 1],
            "next_room_direction": "right",
            "selected_door_center": None,
            "detector_enabled": True,
            "detection_objects_count": 1,
            "door_candidates_count": 0,
            "player_detected": True,
            "debug_scores": {"hero": 0.31, "query": 0.2},
        },
    }

    issues = analyze_debug_payload(payload)
    summary = summarize_debug_payload(payload)

    assert any("YOLO \u6ca1\u6709\u68c0\u6d4b\u5230\u95e8" in issue for issue in issues)
    assert any("hero \u6a21\u677f\u5206\u6570\u504f\u4f4e" in issue for issue in issues)
    assert "\u4e0b\u4e00\u6b65\u65b9\u5411: right" in summary


def test_route_debug_uses_configured_template_thresholds_for_score_warnings():
    payload = {
        "map_name": "generic",
        "marker_thresholds": {"hero": 0.3, "query": 0.15},
        "snapshot": {
            "current_room": [0, 0],
            "target_room": None,
            "route_status": "missing_target",
            "next_room_direction": None,
            "selected_door_center": None,
            "detector_enabled": False,
            "debug_scores": {"hero": 0.31, "query": 0.2},
        },
    }

    issues = analyze_debug_payload(payload)

    assert not any("hero \u6a21\u677f\u5206\u6570\u504f\u4f4e" in issue for issue in issues)
    assert not any("\u76ee\u6807\u6a21\u677f\u6700\u9ad8\u5206\u504f\u4f4e" in issue for issue in issues)


def test_route_debug_reports_target_score_below_configured_threshold():
    payload = {
        "map_name": "generic",
        "marker_thresholds": {"hero": 0.3, "query": 0.45},
        "snapshot": {
            "current_room": [0, 0],
            "target_room": None,
            "route_status": "missing_target",
            "next_room_direction": None,
            "selected_door_center": None,
            "detector_enabled": False,
            "debug_scores": {"hero": 0.9, "query": 0.4, "query1": 0.41},
        },
    }

    issues = analyze_debug_payload(payload)

    assert any("query1=0.4100 < 0.4500" in issue for issue in issues)


def test_route_debug_does_not_report_missing_door_when_detector_disabled():
    payload = {
        "map_name": "generic",
        "snapshot": {
            "current_room": [0, 0],
            "target_kind": "query",
            "target_room": [0, 1],
            "route_status": "moving",
            "route_path": [[0, 0], [0, 1]],
            "next_room_direction": "right",
            "selected_door_center": None,
            "detector_enabled": False,
            "detection_objects_count": 0,
            "door_candidates_count": 0,
            "player_detected": False,
            "debug_scores": {"hero": 0.9, "query": 0.9},
        },
    }

    issues = analyze_debug_payload(payload)

    assert issues == []


def test_route_debug_reports_unusable_door_when_door_exists_but_not_selected():
    payload = {
        "map_name": "generic",
        "snapshot": {
            "current_room": [0, 0],
            "target_kind": "query",
            "target_room": [0, 1],
            "route_status": "moving",
            "route_path": [[0, 0], [0, 1]],
            "next_room_direction": "right",
            "selected_door_center": None,
            "detector_enabled": True,
            "detection_objects_count": 2,
            "door_candidates_count": 1,
            "player_detected": True,
            "debug_scores": {"hero": 0.9, "query": 0.9},
        },
    }

    issues = analyze_debug_payload(payload)

    assert any("\u6ca1\u6709\u9009\u4e2d\u53ef\u7528\u95e8" in issue for issue in issues)


def test_route_debug_can_resolve_latest_json_from_directory(tmp_path):
    older = tmp_path / "route_20260101_000000_000.json"
    newer = tmp_path / "route_20260101_000001_000.json"
    older.write_text(json.dumps({"snapshot": {}}), encoding="utf-8")
    newer.write_text(json.dumps({"snapshot": {"current_room": [1, 1]}}), encoding="utf-8")

    resolved = resolve_debug_json_path(tmp_path)

    assert resolved == newer
    assert "\u5f53\u524d\u623f\u95f4: [1, 1]" in summarize_debug_file(tmp_path)


def test_route_sequence_debug_reports_repeated_stuck_room(tmp_path):
    for index in range(4):
        payload = {
            "map_name": "generic",
            "snapshot": {
                "current_room": [0, 0],
                "target_room": [0, 2],
                "target_kind": "query",
                "route_status": "moving",
                "route_path": [[0, 0], [0, 1], [0, 2]],
                "next_room_direction": "right",
                "selected_door_center": [740.0, 340.0],
                "debug_scores": {"hero": 0.9, "query": 0.9},
            },
        }
        (tmp_path / f"route_20260101_00000{index}_000.json").write_text(json.dumps(payload), encoding="utf-8")

    issues = analyze_debug_sequence([json.loads(path.read_text(encoding="utf-8")) for path in sorted(tmp_path.glob("*.json"))])
    summary = summarize_debug_sequence(tmp_path)

    assert any("\u540c\u4e00\u623f\u95f4" in issue for issue in issues)
    assert "\u72b6\u6001\u7edf\u8ba1" in summary
    assert "moving" in summary


def test_route_sequence_debug_reports_repeated_bad_status():
    payloads = [
        {
            "snapshot": {
                "current_room": [0, 0],
                "target_room": [0, 2],
                "route_status": "unreachable",
                "route_path": None,
                "next_room_direction": None,
                "selected_door_center": None,
            }
        }
        for _ in range(3)
    ]

    issues = analyze_debug_sequence(payloads)

    assert any("unreachable" in issue for issue in issues)


def test_route_sequence_debug_orders_by_frame_index(tmp_path):
    payloads = [
        (
            "route_late_name.json",
            {
                "frame_index": 2,
                "snapshot": {
                    "current_room": [0, 1],
                    "target_room": [0, 2],
                    "route_status": "moving",
                    "route_path": [[0, 1], [0, 2]],
                    "next_room_direction": "right",
                    "selected_door_center": [740.0, 340.0],
                    "detector_enabled": False,
                    "debug_scores": {"hero": 0.9, "query": 0.9},
                },
            },
        ),
        (
            "route_early_name.json",
            {
                "frame_index": 1,
                "snapshot": {
                    "current_room": [0, 0],
                    "target_room": [0, 2],
                    "route_status": "moving",
                    "route_path": [[0, 0], [0, 1], [0, 2]],
                    "next_room_direction": "right",
                    "selected_door_center": [740.0, 340.0],
                    "detector_enabled": False,
                    "debug_scores": {"hero": 0.9, "query": 0.9},
                },
            },
        ),
    ]
    for filename, payload in payloads:
        (tmp_path / filename).write_text(json.dumps(payload), encoding="utf-8")

    summary = summarize_debug_sequence(tmp_path)

    assert "\u5e27\u8303\u56f4: 1 -> 2" in summary
    assert "\u7b2c\u4e00\u5e27: moving [0, 0] -> [0, 2]" in summary
    assert "\u6700\u540e\u4e00\u5e27: moving [0, 1] -> [0, 2]" in summary


def test_route_probe_analyzes_saved_screenshot(tmp_path):
    nav = MiniMapNavigator("generic")
    frame = np.zeros((900, 1600, 3), dtype=np.uint8)
    _, room_rect = nav._spec_rects(frame, nav.spec)
    rx1, ry1, rx2, ry2 = room_rect

    def paste_marker(name, row, col):
        template = nav.templates[name]
        height, width = template.shape[:2]
        center_x = int(rx1 + (rx2 - rx1) * (col + 0.5) / nav.spec.cols)
        center_y = int(ry1 + (ry2 - ry1) * (row + 0.5) / nav.spec.rows)
        x1 = center_x - width // 2
        y1 = center_y - height // 2
        frame[y1:y1 + height, x1:x1 + width] = template

    paste_marker("hero", 0, 0)
    paste_marker("query", 0, 2)
    image_path = tmp_path / "screenshot.png"
    assert cv2.imwrite(str(image_path), frame)

    json_path = analyze_screenshot_file(
        image_path,
        tmp_path / "debug",
        map_name="generic",
        detection_objects=[
            {"player": {"xywh": [400, 280, 80, 120], "conf": 0.99}},
            {"door": {"xywh": [700, 280, 80, 120], "conf": 0.88}},
        ],
    )
    payload = json.loads(json_path.read_text(encoding="utf-8"))

    assert payload["snapshot"]["current_room"] == [0, 0]
    assert payload["snapshot"]["target_room"] == [0, 2]
    assert payload["snapshot"]["route_path"] == [[0, 0], [0, 1], [0, 2]]
    assert payload["snapshot"]["route_status"] == "moving"
    assert payload["snapshot"]["next_room_direction"] == "right"
    assert payload["snapshot"]["detector_enabled"] is True
    assert payload["snapshot"]["detection_objects_count"] == 2
    assert payload["snapshot"]["door_candidates_count"] == 1
    assert payload["snapshot"]["player_detected"] is True
    assert payload["snapshot"]["selected_door_center"] == [740.0, 340.0]
    assert json_path.with_name(f"{json_path.stem}_frame.png").exists()


def test_route_probe_cli_without_objects_marks_detector_disabled(tmp_path):
    nav = MiniMapNavigator("generic")
    frame = np.zeros((900, 1600, 3), dtype=np.uint8)
    _, room_rect = nav._spec_rects(frame, nav.spec)
    rx1, ry1, rx2, ry2 = room_rect

    def paste_marker(name, row, col):
        template = nav.templates[name]
        height, width = template.shape[:2]
        center_x = int(rx1 + (rx2 - rx1) * (col + 0.5) / nav.spec.cols)
        center_y = int(ry1 + (ry2 - ry1) * (row + 0.5) / nav.spec.rows)
        x1 = center_x - width // 2
        y1 = center_y - height // 2
        frame[y1:y1 + height, x1:x1 + width] = template

    paste_marker("hero", 0, 0)
    paste_marker("query", 0, 2)
    image_path = tmp_path / "screenshot.png"
    output_dir = tmp_path / "debug"
    assert cv2.imwrite(str(image_path), frame)

    assert route_probe_main([str(image_path), "--out", str(output_dir), "--map", "generic"]) == 0
    payload = json.loads(next(output_dir.glob("route_*.json")).read_text(encoding="utf-8"))

    assert payload["snapshot"]["route_status"] == "moving"
    assert payload["snapshot"]["detector_enabled"] is False
    assert analyze_debug_payload(payload) == []


def test_route_check_analyzes_frame_without_detector(tmp_path):
    nav = MiniMapNavigator("generic")
    frame = np.zeros((900, 1600, 3), dtype=np.uint8)
    _, room_rect = nav._spec_rects(frame, nav.spec)
    rx1, ry1, rx2, ry2 = room_rect

    def paste_marker(name, row, col):
        template = nav.templates[name]
        height, width = template.shape[:2]
        center_x = int(rx1 + (rx2 - rx1) * (col + 0.5) / nav.spec.cols)
        center_y = int(ry1 + (ry2 - ry1) * (row + 0.5) / nav.spec.rows)
        x1 = center_x - width // 2
        y1 = center_y - height // 2
        frame[y1:y1 + height, x1:x1 + width] = template

    paste_marker("hero", 0, 0)
    paste_marker("query", 0, 2)

    paths = analyze_frame_sequence([frame], tmp_path / "check", map_name="generic")
    payload = json.loads(paths[0].read_text(encoding="utf-8"))

    assert payload["frame_index"] == 1
    assert payload["snapshot"]["route_status"] == "moving"
    assert payload["snapshot"]["next_room_direction"] == "right"
    assert payload["snapshot"]["detector_enabled"] is False
    assert payload["detection_objects"] == []
    assert payload["snapshot"]["selected_door_center"] is None
    assert analyze_debug_payload(payload) == []
    report = build_acceptance_report(paths[0].parent, stage="minimap")
    assert report.passed is True
    assert "\u53ef\u4ee5\u7ee7\u7eed\u8dd1 route_check --with-detector" in report.to_text()


def test_route_check_uses_detector_provider_for_door_selection(tmp_path):
    nav = MiniMapNavigator("generic")
    frame = np.zeros((900, 1600, 3), dtype=np.uint8)
    _, room_rect = nav._spec_rects(frame, nav.spec)
    rx1, ry1, rx2, ry2 = room_rect

    def paste_marker(name, row, col):
        template = nav.templates[name]
        height, width = template.shape[:2]
        center_x = int(rx1 + (rx2 - rx1) * (col + 0.5) / nav.spec.cols)
        center_y = int(ry1 + (ry2 - ry1) * (row + 0.5) / nav.spec.rows)
        x1 = center_x - width // 2
        y1 = center_y - height // 2
        frame[y1:y1 + height, x1:x1 + width] = template

    paste_marker("hero", 0, 0)
    paste_marker("query", 0, 2)

    def detect(_frame, frame_index):
        assert frame_index == 1
        return DetectionFrameResult(objects=[
            {"player": {"xywh": [400, 280, 80, 120], "conf": 0.99}},
            {"door": {"xywh": [700, 280, 80, 120], "conf": 0.88}},
        ], debug_frame=frame.copy())

    paths = analyze_frame_sequence([frame], tmp_path / "check", map_name="generic", detection_provider=detect)
    payload = json.loads(paths[0].read_text(encoding="utf-8"))
    summary = summarize_debug_file(paths[0])

    assert payload["snapshot"]["detector_enabled"] is True
    assert payload["snapshot"]["detection_objects_count"] == 2
    assert payload["snapshot"]["door_candidates_count"] == 1
    assert payload["snapshot"]["player_detected"] is True
    assert payload["snapshot"]["selected_door_center"] == [740.0, 340.0]
    assert payload["detection_objects"] == [
        {"player": {"xywh": [400, 280, 80, 120], "conf": 0.99}},
        {"door": {"xywh": [700, 280, 80, 120], "conf": 0.88}},
    ]
    assert payload["debug_detector_image"] == paths[0].with_name(f"{paths[0].stem}_detector.png").name
    assert paths[0].with_name(payload["debug_detector_image"]).exists()
    assert "YOLO \u6807\u6ce8\u56fe:" in summary
    assert "\u68c0\u6d4b\u6807\u7b7e: door=1, player=1" in summary
    report = build_acceptance_report(paths[0].parent, stage="detector")
    assert report.passed is True
    assert "DNF_DRY_RUN=1" in report.to_text()


def test_route_acceptance_blocks_bad_minimap_payload(tmp_path):
    payload = {
        "map_name": "generic",
        "snapshot": {
            "current_room": None,
            "target_room": None,
            "route_status": "missing_current",
            "route_path": None,
            "next_room_direction": None,
            "selected_door_center": None,
            "detector_enabled": False,
            "debug_scores": {"hero": 0.2, "query": 0.1},
        },
    }
    json_path = tmp_path / "route_bad.json"
    json_path.write_text(json.dumps(payload), encoding="utf-8")

    issues = analyze_acceptance_payload(payload, json_path, stage="minimap")
    report = build_acceptance_report(json_path, stage="minimap")

    assert report.passed is False
    assert any("\u6ca1\u6709\u8bc6\u522b\u5230\u5f53\u524d\u89d2\u8272\u623f\u95f4" in issue for issue in issues)
    assert "\u672a\u901a\u8fc7" in report.to_text()


def test_route_acceptance_dry_run_blocks_repeated_stuck_route(tmp_path):
    for index in range(4):
        payload = {
            "map_name": "generic",
            "frame_index": index + 1,
            "debug_minimap_image": f"route_{index}.png",
            "debug_frame_image": f"route_{index}_frame.png",
            "snapshot": {
                "current_room": [0, 0],
                "target_room": [0, 2],
                "target_kind": "query",
                "route_status": "moving",
                "route_path": [[0, 0], [0, 1], [0, 2]],
                "next_room_direction": "right",
                "selected_door_center": [740.0, 340.0],
                "detector_enabled": True,
                "detection_objects_count": 2,
                "door_candidates_count": 1,
                "player_detected": True,
                "debug_scores": {"hero": 0.9, "query": 0.9},
            },
        }
        (tmp_path / f"route_{index}.json").write_text(json.dumps(payload), encoding="utf-8")
        (tmp_path / f"route_{index}.png").write_bytes(b"png")
        (tmp_path / f"route_{index}_frame.png").write_bytes(b"png")

    report = build_acceptance_report(tmp_path, stage="dry-run")

    assert report.passed is False
    assert any("\u540c\u4e00\u623f\u95f4" in issue for issue in report.issues)


def test_route_advice_suggests_threshold_when_hero_score_is_close(tmp_path):
    payload = {
        "map_name": "generic",
        "marker_thresholds": {"hero": 0.58, "query": 0.5},
        "snapshot": {
            "current_room": None,
            "target_room": [0, 2],
            "route_status": "missing_current",
            "next_room_direction": None,
            "selected_door_center": None,
            "detector_enabled": False,
            "debug_scores": {"hero": 0.55, "query": 0.8},
        },
    }
    json_path = tmp_path / "route_hero.json"
    json_path.write_text(json.dumps(payload), encoding="utf-8")

    advice = build_route_advice(json_path).to_text()

    assert 'DNF_MINIMAP_HERO_THRESHOLD="0.52"' in advice


def test_route_advice_suggests_fixed_map_when_auto_scores_are_close(tmp_path):
    payload = {
        "map_name": "generic",
        "auto_map_scores": {"generic": 0.72, "haibolun": 0.70},
        "snapshot": {
            "current_room": [0, 0],
            "target_room": [0, 2],
            "route_status": "moving",
            "next_room_direction": "right",
            "selected_door_center": None,
            "detector_enabled": False,
            "debug_scores": {"hero": 0.9, "query": 0.9},
        },
    }
    json_path = tmp_path / "route_auto.json"
    json_path.write_text(json.dumps(payload), encoding="utf-8")

    advice = build_route_advice(json_path).to_text()

    assert "--map generic" in advice
    assert "DNF_MAP_NAME" in advice


def test_route_advice_suggests_detector_when_minimap_route_is_ready(tmp_path):
    payload = {
        "map_name": "generic",
        "snapshot": {
            "current_room": [0, 0],
            "target_room": [0, 2],
            "route_status": "moving",
            "next_room_direction": "right",
            "selected_door_center": None,
            "detector_enabled": False,
            "debug_scores": {"hero": 0.9, "query": 0.9},
        },
    }
    json_path = tmp_path / "route_ready.json"
    json_path.write_text(json.dumps(payload), encoding="utf-8")

    advice = build_route_advice(json_path).to_text()

    assert "route_check" in advice
    assert "--with-detector" in advice
