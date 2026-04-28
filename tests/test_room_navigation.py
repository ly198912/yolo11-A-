from __future__ import annotations

import copy

import numpy as np

from dnf import door_direction_config as nav_config
from dnf.room_navigation import RoomNavigator


def _make_frame_with_highlight(point):
    frame = np.zeros((600, 800, 3), dtype=np.uint8)
    left, top, _, _ = nav_config.MINIMAP_REGION
    x, y = point
    frame[top + y, left + x] = np.array(nav_config.ROOM_HIGHLIGHT_COLOR_BGR, dtype=np.uint8)
    return frame


def test_validate_map_nav_config_flags_empty_marker_points():
    config = copy.deepcopy(nav_config.MAP_NAV_CONFIG)
    issues = nav_config.validate_map_nav_config(config)
    assert any("marker_points must not be empty" in issue for issue in issues)


def test_room_navigator_locks_map_and_room_after_stable_frames():
    original = copy.deepcopy(nav_config.MAP_NAV_CONFIG)
    try:
        for map_name, rooms in nav_config.MAP_NAV_CONFIG.items():
            for room_name in rooms:
                nav_config.MAP_NAV_CONFIG[map_name][room_name]["marker_points"] = []
                nav_config.MAP_NAV_CONFIG[map_name][room_name]["exit"] = "RIGHT"

        nav_config.MAP_NAV_CONFIG["妖气追踪1"]["room1"]["marker_points"] = [(10, 10)]
        nav_config.MAP_NAV_CONFIG["妖气追踪1"]["room1"]["exit"] = "RIGHT"
        nav_config.MAP_NAV_CONFIG["妖气追踪2"]["room1"]["marker_points"] = [(20, 20)]
        nav_config.MAP_NAV_CONFIG["妖气追踪2"]["room1"]["exit"] = "LEFT"

        navigator = RoomNavigator()
        frame = _make_frame_with_highlight((10, 10))

        snapshot = None
        for _ in range(nav_config.STABLE_FRAMES):
            snapshot = navigator.update(frame)

        assert snapshot is not None
        assert snapshot.current_map_name == "妖气追踪1"
        assert snapshot.current_room_name == "room1"
        assert snapshot.expected_exit == "RIGHT"
        assert snapshot.hold_position is False
    finally:
        nav_config.MAP_NAV_CONFIG.clear()
        nav_config.MAP_NAV_CONFIG.update(original)


def test_room_navigator_holds_when_room_is_unknown():
    original = copy.deepcopy(nav_config.MAP_NAV_CONFIG)
    try:
        for map_name, rooms in nav_config.MAP_NAV_CONFIG.items():
            for room_name in rooms:
                nav_config.MAP_NAV_CONFIG[map_name][room_name]["marker_points"] = []
                nav_config.MAP_NAV_CONFIG[map_name][room_name]["exit"] = "RIGHT"

        navigator = RoomNavigator()
        frame = np.zeros((600, 800, 3), dtype=np.uint8)
        snapshot = navigator.update(frame)

        assert snapshot.current_room_name is None
        assert snapshot.hold_position is True
    finally:
        nav_config.MAP_NAV_CONFIG.clear()
        nav_config.MAP_NAV_CONFIG.update(original)
