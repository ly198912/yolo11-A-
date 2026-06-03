from dataclasses import replace
import sys
import types

import cv2
import numpy as np
import pytest

from dnf.config import NavigationConfig
from dnf.detector import _float_env, _normalize_label
from dnf.game import Game, GameRuntimeState
from dnf.map_specs import MAP_SPECS, scaled_rects_for_frame
from dnf.navigation import (
    DoorSearcher,
    DoorSelector,
    NavigationMemory,
    PositionFilter,
    StuckDetector,
    StuckHandler,
    LocalAStarPlanner,
    player_foot,
)
from dnf.reward_handler import EndRewardHandler
from dnf.window_capture import ScreenCapture, WindowController


class FakeController:
    def __init__(self):
        self.actions = []

    def key_down(self, key):
        self.actions.append(("down", key))

    def key_up(self, key):
        self.actions.append(("up", key))

    def tap_key(self, key, duration=0.08):
        self.actions.append(("tap", key, duration))

    def release_direction_keys(self):
        self.actions.append(("release",))


def _config(**overrides):
    return replace(NavigationConfig(), **overrides)


def test_player_position_uses_feet_and_ema_filter():
    assert player_foot([100, 200, 80, 120]) == (140.0, 302.0)
    position_filter = PositionFilter(alpha=0.35)
    assert position_filter.update((100.0, 200.0)) == (100.0, 200.0)
    assert position_filter.update((120.0, 240.0)) == (107.0, 214.0)


def test_config_rejects_out_of_range_filter_and_template_values(monkeypatch):
    monkeypatch.setenv("DNF_POSITION_SMOOTH_ALPHA", "3")
    monkeypatch.setenv("DNF_TEMPLATE_MATCH_THRESHOLD", "-1")
    monkeypatch.setenv("DNF_X_DEAD_ZONE", "30")

    config = NavigationConfig.from_env()

    assert config.position_smooth_alpha == 0.35
    assert config.template_match_threshold == 0.8
    assert config.x_dead_zone == 30


def test_config_reads_window_position_offsets(monkeypatch):
    monkeypatch.setenv("DNF_WINDOW_LEFT", "7")
    monkeypatch.setenv("DNF_WINDOW_TOP", "9")

    config = NavigationConfig.from_env()

    assert config.window_left == 7
    assert config.window_top == 9


def test_detector_normalizes_dnf_variant_labels():
    assert _normalize_label("boss_115_1") == "boss"
    assert _normalize_label("monster_frost") == "monster"
    assert _normalize_label("door_sy") == "door"
    assert _normalize_label("goods_money") == "money"


def test_detector_yolo_threshold_env_rejects_invalid_values(monkeypatch):
    monkeypatch.setenv("DNF_YOLO_CONF", "0.42")
    monkeypatch.setenv("DNF_YOLO_IOU", "2")

    assert _float_env("DNF_YOLO_CONF", 0.3) == 0.42
    assert _float_env("DNF_YOLO_IOU", 0.5) == 0.5


def test_screen_capture_uses_dynamic_client_region_and_returns_rgb(monkeypatch):
    requested = []

    class FakeMss:
        def grab(self, monitor):
            requested.append(monitor)
            return np.array([[[10, 20, 30, 255]]], dtype=np.uint8)

    monkeypatch.setitem(sys.modules, "mss", types.SimpleNamespace(mss=lambda: FakeMss()))
    controller = types.SimpleNamespace(client_region=lambda: (11, 22, 1, 1))
    capture = ScreenCapture(controller)

    frame, size = capture.grab_rgb()

    assert requested == [{"left": 11, "top": 22, "width": 1, "height": 1}]
    assert size == (1, 1)
    assert frame.tolist() == [[[30, 20, 10]]]


def test_window_controller_places_bound_window(monkeypatch):
    calls = []

    class FakeWin32Gui:
        @staticmethod
        def IsWindowVisible(hwnd):
            return True

        @staticmethod
        def GetWindowText(hwnd):
            return "地下城与勇士：创新世纪"

        @staticmethod
        def GetClassName(hwnd):
            return "地下城与勇士"

        @staticmethod
        def GetClientRect(hwnd):
            return (0, 0, 800, 600)

        @staticmethod
        def EnumWindows(callback, payload):
            callback(123, payload)

        @staticmethod
        def ShowWindow(hwnd, command):
            calls.append(("show", hwnd, command))

        @staticmethod
        def GetWindowRect(hwnd):
            return (50, 60, 850, 660)

        @staticmethod
        def SetWindowPos(hwnd, insert_after, left, top, width, height, flags):
            calls.append(("pos", hwnd, insert_after, left, top, width, height, flags))

    fake_win32con = types.SimpleNamespace(SW_RESTORE=9, SWP_NOZORDER=4, SWP_SHOWWINDOW=64)
    monkeypatch.setitem(sys.modules, "win32con", fake_win32con)
    monkeypatch.setitem(sys.modules, "win32gui", FakeWin32Gui)

    hwnd = WindowController(window_left=3, window_top=3).bind()

    assert hwnd == 123
    assert ("show", 123, 9) in calls
    assert ("pos", 123, 0, 3, 3, 800, 600, 68) in calls


def test_universal_minimap_basket_wraps_top_right_panel():
    spec = MAP_SPECS["universal"]

    assert scaled_rects_for_frame(spec, 800, 600) == (
        (560, 0, 800, 210),
        (560, 0, 800, 210),
    )
    assert scaled_rects_for_frame(spec, 1067, 600) == (
        (747, 0, 1067, 210),
        (747, 0, 1067, 210),
    )
    assert (spec.rows, spec.cols) == (1, 1)
    assert spec.room_grid == [[0]]
    assert MAP_SPECS["generic"].name == "generic"


def test_door_selector_prefers_non_backtrack_unvisited_door():
    selector = DoorSelector(_config())
    memory = NavigationMemory()
    memory.room.backtrack_direction = "LEFT"
    objects = [
        {"door": {"xywh": [20, 250, 60, 100], "conf": 0.9}},
        {"door": {"xywh": [720, 250, 60, 100], "conf": 0.9}},
    ]

    selected = selector.select(objects, (400, 320), 800, 600, memory)

    assert selected is not None
    assert selected.direction == "RIGHT"
    assert all("回头门" not in reason for reason in selected.reasons)


def test_door_searcher_keeps_direction_then_delays_backtrack():
    searcher = DoorSearcher(_config(search_direction_ticks=2))

    assert searcher.next_direction("RIGHT") == "LEFT"
    assert searcher.next_direction("RIGHT") == "LEFT"
    assert searcher.next_direction("RIGHT") == "UP"
    assert searcher.next_direction("RIGHT") == "UP"
    assert searcher.next_direction("RIGHT") == "DOWN"
    assert searcher.next_direction("RIGHT") == "DOWN"
    assert searcher.next_direction("RIGHT") == "RIGHT"


def test_stuck_detector_waits_until_point_six_seconds():
    detector = StuckDetector(_config(stuck_time=0.6, stuck_pixel_threshold=5))

    assert detector.observe((100, 100), "UP", now=1.0) is False
    assert detector.observe((102, 101), "UP", now=1.3) is False
    assert detector.observe((101, 102), "UP", now=1.59) is True


def test_top_stuck_recovery_nudges_down_then_resumes_right():
    controller = FakeController()
    planner = LocalAStarPlanner(cell_size=32)
    handler = StuckHandler(_config(nudge_press_time=0.03), planner)

    resume = handler.recover(controller, "UP", (400, 30), 800, 600)

    assert resume == "RIGHT"
    assert controller.actions == [("release",), ("tap", "down", 0.03)]
    assert planner.blocked


@pytest.mark.parametrize(
    ("direction", "nudge"),
    [("UP", "down"), ("DOWN", "up"), ("LEFT", "right"), ("RIGHT", "left")],
)
def test_stuck_recovery_nudges_away_from_each_edge(direction, nudge):
    controller = FakeController()
    handler = StuckHandler(_config(), LocalAStarPlanner(cell_size=32))

    handler.recover(controller, direction, (400, 300), 800, 600)

    assert controller.actions[:2] == [("release",), ("tap", nudge, 0.03)]


def test_local_astar_routes_around_blocked_grid_cell():
    planner = LocalAStarPlanner(cell_size=100)
    planner.mark_blocked((150, 50), 300, 300)

    assert planner.next_step_to((50, 50), (250, 50), 300, 300, prefer_horizontal=True) == "DOWN"


def test_reward_handler_matches_fanpai_once_during_cooldown(tmp_path):
    template = np.array(
        [
            [[0, 0, 0], [0, 0, 255], [0, 255, 0]],
            [[255, 0, 0], [255, 255, 255], [0, 255, 255]],
            [[255, 0, 255], [255, 255, 0], [20, 80, 160]],
        ],
        dtype=np.uint8,
    )
    assert cv2.imwrite(str(tmp_path / "fanpai.png"), template)
    assert cv2.imwrite(str(tmp_path / "zailaiyici.png"), np.flipud(template))
    frame_bgr = np.zeros((20, 20, 3), dtype=np.uint8)
    frame_bgr[5:8, 7:10] = template
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    controller = FakeController()
    now = [10.0]
    waits = []
    handler = EndRewardHandler(
        controller,
        _config(template_match_threshold=0.99, fanpai_cooldown=5),
        assets_dir=tmp_path,
        clock=lambda: now[0],
        sleep=waits.append,
        random_uniform=lambda start, end: 1.25,
        random_choice=lambda values: 3,
    )

    assert handler.handle(frame_rgb) == "fanpai"
    assert handler.handle(frame_rgb) == "fanpai"
    assert waits == [1.25]
    assert controller.actions == [("tap", "3", 0.08)]


def test_reward_handler_matches_retry_and_presses_numpad_6(tmp_path):
    fanpai = np.array(
        [
            [[0, 0, 0], [0, 0, 255], [0, 255, 0]],
            [[255, 0, 0], [255, 255, 255], [0, 255, 255]],
            [[255, 0, 255], [255, 255, 0], [20, 80, 160]],
        ],
        dtype=np.uint8,
    )
    retry = np.rot90(fanpai).copy()
    assert cv2.imwrite(str(tmp_path / "fanpai.png"), fanpai)
    assert cv2.imwrite(str(tmp_path / "zailaiyici.png"), retry)
    frame_bgr = np.zeros((20, 20, 3), dtype=np.uint8)
    frame_bgr[5:8, 7:10] = retry
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    controller = FakeController()
    handler = EndRewardHandler(
        controller,
        _config(template_match_threshold=0.99),
        assets_dir=tmp_path,
        sleep=lambda _: None,
        random_uniform=lambda start, end: 0.75,
    )

    assert handler.handle(frame_rgb) == "zailaiyici"
    assert controller.actions == [("tap", "num6", 0.08)]


def test_game_attacks_before_door_navigation():
    config = _config()
    controller = FakeController()
    state = GameRuntimeState.create(config)
    game = Game(
        [
            {"player": {"xywh": [300, 220, 80, 120], "conf": 0.99}},
            {"monster": {"xywh": [350, 250, 60, 90], "conf": 0.90}},
            {"door": {"xywh": [720, 250, 60, 100], "conf": 0.80}},
        ],
        800,
        600,
        controller=controller,
        config=config,
        state=state,
    )

    game.run()

    assert ("tap", "x", 0.08) in controller.actions
    assert state.memory.room.attempted_doors == set()


def test_game_skips_pickup_opposite_minimap_route():
    config = _config(local_astar_enabled=False)
    controller = FakeController()
    state = GameRuntimeState.create(config)
    game = Game([], 800, 600, "RIGHT", controller=controller, config=config, state=state)

    game.update(
        [
            {"player": {"xywh": [300, 220, 80, 120], "conf": 0.99}},
            {"goods": {"xywh": [120, 305, 20, 20], "conf": 0.90}},
        ],
        800,
        600,
        route_direction="RIGHT",
    )

    game.run()

    assert state.action_cache == "RIGHT"
    assert ("down", "left") not in controller.actions


def test_game_tracks_single_visible_door_when_minimap_direction_is_vertical():
    config = _config(local_astar_enabled=False)
    controller = FakeController()
    state = GameRuntimeState.create(config)
    state.memory.room.backtrack_direction = "LEFT"
    game = Game([], 800, 600, "UP", controller=controller, config=config, state=state)

    game.update(
        [
            {"player": {"xywh": [700, 220, 80, 120], "conf": 0.99}},
            {"door": {"xywh": [620, 250, 80, 140], "conf": 0.90}},
        ],
        800,
        600,
        route_direction="UP",
    )

    game.run()

    assert state.selected_door is not None
    assert state.action_cache == "LEFT"


def test_game_uses_local_astar_to_route_around_blocked_cell():
    config = _config(local_astar_cell_size=100)
    controller = FakeController()
    state = GameRuntimeState.create(config)
    state.local_astar.mark_blocked((150, 50), 300, 300)
    game = Game(
        [
            {"player": {"xywh": [10, 0, 80, 60], "conf": 0.99}},
            {"door": {"xywh": [220, 0, 60, 100], "conf": 0.80}},
        ],
        300,
        300,
        controller=controller,
        config=config,
        state=state,
    )

    game.run()

    assert state.action_cache == "DOWN"


def test_game_clears_local_astar_blocked_cells_after_room_transition():
    config = _config(room_transition_distance=100, local_astar_cell_size=100)
    controller = FakeController()
    state = GameRuntimeState.create(config)
    state.local_astar.mark_blocked((150, 50), 300, 300)
    game = Game([], 300, 300, controller=controller, config=config, state=state)
    game.update(
        [
            {"player": {"xywh": [10, 0, 80, 60], "conf": 0.99}},
            {"door": {"xywh": [220, 0, 60, 100], "conf": 0.80}},
        ],
        300,
        300,
    )
    game.run()

    game.update([{"player": {"xywh": [180, 0, 80, 60], "conf": 0.99}}], 300, 300)
    game.run()

    assert state.memory.current_room == "room-001"
    assert state.local_astar.blocked == set()


def test_game_marks_successful_room_transition_and_avoids_entry_side():
    config = _config(room_transition_distance=100)
    controller = FakeController()
    state = GameRuntimeState.create(config)
    game = Game([], 800, 600, controller=controller, config=config, state=state)
    game.update(
        [
            {"player": {"xywh": [300, 220, 80, 120], "conf": 0.99}},
            {"door": {"xywh": [720, 250, 60, 100], "conf": 0.80}},
        ],
        800,
        600,
    )
    game.run()
    assert state.selected_door.direction == "RIGHT"

    game.update([{"player": {"xywh": [20, 220, 80, 120], "conf": 0.99}}], 800, 600)
    game.run()

    assert state.memory.current_room == "room-001"
    assert state.memory.backtrack_direction == "LEFT"
    assert state.action_cache == "RIGHT"


def test_game_marks_timed_out_door_failed_and_tries_another(monkeypatch):
    now = [10.0]
    monkeypatch.setattr("dnf.game.time.monotonic", lambda: now[0])
    config = _config(door_attempt_timeout=0.5)
    controller = FakeController()
    state = GameRuntimeState.create(config)
    game = Game([], 800, 600, "RIGHT", controller=controller, config=config, state=state)
    objects = [
        {"player": {"xywh": [300, 220, 80, 120], "conf": 0.99}},
        {"door": {"xywh": [20, 250, 60, 100], "conf": 0.80}},
        {"door": {"xywh": [720, 250, 60, 100], "conf": 0.80}},
    ]
    game.update(objects, 800, 600)
    game.run()
    first = state.selected_door
    assert first.direction == "RIGHT"

    now[0] = 11.0
    game.update(objects, 800, 600)
    game.run()

    assert first.key in state.memory.room.failed_doors
    assert state.selected_door.direction == "LEFT"


def test_game_retries_only_visible_failed_door_immediately(monkeypatch):
    now = [10.0]
    monkeypatch.setattr("dnf.game.time.monotonic", lambda: now[0])
    config = _config(door_attempt_timeout=0.5, door_retry_cooldown=2.0)
    controller = FakeController()
    state = GameRuntimeState.create(config)
    game = Game([], 800, 600, controller=controller, config=config, state=state)
    objects = [
        {"player": {"xywh": [300, 220, 80, 120], "conf": 0.99}},
        {"door": {"xywh": [720, 250, 60, 100], "conf": 0.80}},
    ]

    game.update(objects, 800, 600)
    game.run()
    first = state.selected_door

    now[0] = 11.0
    game.update(objects, 800, 600)
    game.run()

    assert state.selected_door.key == first.key
    assert first.key not in state.memory.room.failed_doors
    assert state.action_cache == "RIGHT"


def test_game_door_progress_refreshes_attempt_timeout(monkeypatch):
    now = [10.0]
    monkeypatch.setattr("dnf.game.time.monotonic", lambda: now[0])
    config = _config(door_attempt_timeout=0.5, room_transition_distance=1000)
    controller = FakeController()
    state = GameRuntimeState.create(config)
    game = Game([], 800, 600, controller=controller, config=config, state=state)
    door = {"door": {"xywh": [720, 250, 60, 100], "conf": 0.80}}

    game.update([{"player": {"xywh": [300, 220, 80, 120], "conf": 0.99}}, door], 800, 600)
    game.run()
    selected = state.selected_door

    now[0] = 11.0
    game.update([{"player": {"xywh": [340, 220, 80, 120], "conf": 0.99}}, door], 800, 600)
    game.run()

    assert state.selected_door.key == selected.key
    assert selected.key not in state.memory.room.failed_doors
    assert state.selected_door_last_progress_at == 11.0


def test_game_keeps_moving_during_short_player_detection_gap(monkeypatch):
    now = [10.0]
    monkeypatch.setattr("dnf.game.time.monotonic", lambda: now[0])
    config = _config(player_missing_grace=1.2)
    controller = FakeController()
    state = GameRuntimeState.create(config)
    game = Game([], 800, 600, controller=controller, config=config, state=state)
    door = {"door": {"xywh": [720, 250, 60, 100], "conf": 0.80}}

    game.update([{"player": {"xywh": [300, 220, 80, 120], "conf": 0.99}}, door], 800, 600)
    game.run()
    controller.actions.clear()

    now[0] = 10.8
    game.update([door], 800, 600)
    game.run()

    assert state.action_cache == "RIGHT"
    assert controller.actions == []


def test_game_stops_after_player_detection_gap_exceeds_grace(monkeypatch):
    now = [10.0]
    monkeypatch.setattr("dnf.game.time.monotonic", lambda: now[0])
    config = _config(player_missing_grace=1.2)
    controller = FakeController()
    state = GameRuntimeState.create(config)
    game = Game([], 800, 600, controller=controller, config=config, state=state)
    door = {"door": {"xywh": [720, 250, 60, 100], "conf": 0.80}}

    game.update([{"player": {"xywh": [300, 220, 80, 120], "conf": 0.99}}, door], 800, 600)
    game.run()
    controller.actions.clear()

    now[0] = 11.3
    game.update([door], 800, 600)
    game.run()

    assert state.action_cache is None
    assert controller.actions == [("release",)]
