from __future__ import annotations

import numpy as np

from dnf.map_specs import MAP_SPECS
from dnf.minimap_nav import MiniMapNavigator


def _make_navigator_with_marker_matches(has_query: bool) -> MiniMapNavigator:
    navigator = MiniMapNavigator.__new__(MiniMapNavigator)
    navigator.map_name = "universal"
    navigator.spec = MAP_SPECS["universal"]
    navigator.templates = {
        "hero": "hero-template",
        "query": "query-template",
        "boss": "boss-template",
        "elite": "elite-template",
        "special": "special-template",
    }

    navigator.extract_minimap = lambda frame: np.zeros((80, 120, 3), dtype=np.uint8)

    def match_marker(minimap, names, threshold_key):
        if threshold_key == "hero":
            return [(0.9, 10.0, 10.0, "hero")]
        if threshold_key == "query" and has_query:
            return [(0.9, 10.0, 30.0, "query")]
        return []

    def match_template(minimap, template, threshold=None):
        if template == "boss-template":
            return [(110.0, 70.0)]
        return []

    room_by_point = {
        (10.0, 10.0): (0, 0),
        (10.0, 30.0): (1, 0),
        (110.0, 70.0): (3, 4),
    }

    navigator._match_marker = match_marker
    navigator._match_template = match_template
    navigator.compute_room_id = lambda x, y, minimap: room_by_point[(float(x), float(y))]
    return navigator


def test_detect_room_markers_keeps_real_query_when_boss_is_also_visible() -> None:
    navigator = _make_navigator_with_marker_matches(has_query=True)

    room_info = navigator.detect_room_markers(np.zeros((600, 800, 3), dtype=np.uint8))

    assert room_info["current_room"] == (0, 0)
    assert room_info["query_room"] == (1, 0)
    assert room_info["boss_room"] == (3, 4)


def test_detect_room_markers_keeps_boss_separate_when_query_missing() -> None:
    navigator = _make_navigator_with_marker_matches(has_query=False)

    room_info = navigator.detect_room_markers(np.zeros((600, 800, 3), dtype=np.uint8))

    assert room_info["query_room"] is None
    assert room_info["boss_room"] == (3, 4)


def test_detect_room_markers_ignores_low_confidence_query_match() -> None:
    navigator = _make_navigator_with_marker_matches(has_query=False)

    def match_marker(minimap, names, threshold_key):
        if threshold_key == "hero":
            return [(0.9, 10.0, 10.0, "hero")]
        if threshold_key == "query":
            return []
        return []

    navigator._match_marker = match_marker

    room_info = navigator.detect_room_markers(np.zeros((600, 800, 3), dtype=np.uint8))

    assert room_info["query_room"] is None
    assert room_info["boss_room"] == (3, 4)


def test_build_route_snapshot_uses_right_when_query_is_missing() -> None:
    navigator = _make_navigator_with_marker_matches(has_query=False)
    navigator._match_template = lambda minimap, template, threshold=None: [] if template == "boss-template" else []
    navigator.last_direction = None
    navigator._debug_scores_frame = 0
    navigator._debug_scores_cache = {}
    navigator._debug_scores_interval = 5
    navigator.get_debug_scores = lambda frame: {}  # type: ignore[method-assign]

    snapshot = navigator.build_route_snapshot(
        np.zeros((600, 800, 3), dtype=np.uint8),
        [{"player": {"xywh": [100.0, 100.0, 20.0, 20.0], "conf": 0.9}}],
    )

    assert snapshot.query_room is None
    assert snapshot.target_kind == "query_missing"
    assert snapshot.next_room_direction is None


def test_build_route_snapshot_uses_visible_boss_when_query_is_missing() -> None:
    navigator = _make_navigator_with_marker_matches(has_query=False)
    navigator.last_direction = None
    navigator._debug_scores_frame = 0
    navigator._debug_scores_cache = {}
    navigator._debug_scores_interval = 5
    navigator.get_debug_scores = lambda frame: {}  # type: ignore[method-assign]

    snapshot = navigator.build_route_snapshot(
        np.zeros((600, 800, 3), dtype=np.uint8),
        [{"player": {"xywh": [100.0, 100.0, 20.0, 20.0], "conf": 0.9}}],
    )

    assert snapshot.query_room is None
    assert snapshot.target_kind == "boss"
    assert snapshot.target_room == (3, 4)
    assert snapshot.next_room_direction == "right"


def test_universal_map_uses_large_top_right_search_box() -> None:
    navigator = MiniMapNavigator.__new__(MiniMapNavigator)
    navigator.auto_map = False
    navigator._set_active_map = MiniMapNavigator._set_active_map.__get__(navigator, MiniMapNavigator)
    navigator._set_active_map("universal")

    assert navigator.crop_rect_800 == (598, 23, 799, 192)
    assert navigator.room_rect_800 == (674, 29, 794, 123)
    assert navigator.spec.rows == 5
    assert navigator.spec.cols == 6


def test_marker_direction_can_route_without_room_grid() -> None:
    navigator = MiniMapNavigator.__new__(MiniMapNavigator)
    navigator.spec = MAP_SPECS["universal"]
    navigator.last_direction = None
    navigator.get_debug_scores = lambda frame: {}  # type: ignore[method-assign]
    navigator.detect_room_markers = lambda frame: {  # type: ignore[method-assign]
        "current_room": (3, 3),
        "boss_room": None,
        "query_room": None,
        "elite_room": None,
        "down_room": None,
        "current_marker": (50.0, 50.0),
        "boss_marker": None,
        "query_marker": (120.0, 52.0),
        "elite_marker": None,
        "down_marker": None,
    }
    navigator._door_candidates_from_objects = lambda objects: []  # type: ignore[method-assign]

    snapshot = navigator.build_route_snapshot(np.zeros((600, 800, 3), dtype=np.uint8), [])

    assert snapshot.target_kind == "query"
    assert snapshot.next_room_direction == "right"


def test_diagonal_marker_direction_uses_primary_axis_for_next_step() -> None:
    navigator = MiniMapNavigator.__new__(MiniMapNavigator)
    navigator.spec = MAP_SPECS["universal"]
    navigator.last_direction = None
    navigator.get_debug_scores = lambda frame: {}  # type: ignore[method-assign]
    navigator.detect_room_markers = lambda frame: {  # type: ignore[method-assign]
        "current_room": (4, 2),
        "boss_room": (3, 4),
        "query_room": None,
        "elite_room": None,
        "down_room": None,
        "current_marker": (40.0, 80.0),
        "boss_marker": (120.0, 50.0),
        "query_marker": None,
        "elite_marker": None,
        "down_marker": None,
    }
    navigator._door_candidates_from_objects = lambda objects: []  # type: ignore[method-assign]

    snapshot = navigator.build_route_snapshot(np.zeros((600, 800, 3), dtype=np.uint8), [])

    assert snapshot.target_kind == "boss"
    assert snapshot.next_room_direction == "right"


def test_universal_query_marker_survives_bad_room_grid_mapping() -> None:
    navigator = MiniMapNavigator.__new__(MiniMapNavigator)
    navigator.map_name = "universal"
    navigator.spec = MAP_SPECS["universal"]
    navigator.templates = {
        "hero": "hero-template",
        "query": "query-template",
        "boss": "boss-template",
        "elite": "elite-template",
        "special": "special-template",
    }
    navigator.extract_minimap = lambda frame: np.zeros((80, 120, 3), dtype=np.uint8)
    navigator.compute_room_id = lambda x, y, minimap: (0, 0)
    navigator._match_template = lambda minimap, template, threshold=None: []
    navigator.get_debug_scores = lambda frame: {}  # type: ignore[method-assign]
    navigator.last_direction = None

    def match_marker(minimap, names, threshold_key):
        if threshold_key == "hero":
            return [(0.9, 30.0, 30.0, "hero")]
        if threshold_key == "query":
            return [(0.9, 80.0, 32.0, "query")]
        return []

    navigator._match_marker = match_marker

    snapshot = navigator.build_route_snapshot(np.zeros((600, 800, 3), dtype=np.uint8), [])

    assert snapshot.current_room == (0, 0)
    assert snapshot.query_room == (0, 0)
    assert snapshot.target_kind == "query"
    assert snapshot.next_room_direction == "right"


def test_query_marker_same_room_still_overrides_boss_when_marker_points_right() -> None:
    navigator = MiniMapNavigator.__new__(MiniMapNavigator)
    navigator.spec = MAP_SPECS["universal"]
    navigator.last_direction = None
    navigator.get_debug_scores = lambda frame: {}  # type: ignore[method-assign]
    navigator.detect_room_markers = lambda frame: {  # type: ignore[method-assign]
        "current_room": (4, 2),
        "boss_room": (3, 4),
        "query_room": (4, 2),
        "elite_room": (3, 4),
        "down_room": (3, 2),
        "current_marker": (40.0, 80.0),
        "boss_marker": (120.0, 20.0),
        "query_marker": (112.0, 82.0),
        "elite_marker": (120.0, 20.0),
        "down_marker": (42.0, 30.0),
    }
    navigator._door_candidates_from_objects = lambda objects: []  # type: ignore[method-assign]

    snapshot = navigator.build_route_snapshot(np.zeros((600, 800, 3), dtype=np.uint8), [])

    assert snapshot.target_kind == "query"
    assert snapshot.next_room_direction == "right"


def test_grid_step_overrides_noisy_marker_when_target_room_is_different() -> None:
    navigator = MiniMapNavigator.__new__(MiniMapNavigator)
    navigator.spec = MAP_SPECS["universal"]
    navigator.last_direction = None
    navigator.get_debug_scores = lambda frame: {}  # type: ignore[method-assign]
    navigator.detect_room_markers = lambda frame: {  # type: ignore[method-assign]
        "current_room": (4, 3),
        "boss_room": (3, 4),
        "query_room": (4, 2),
        "elite_room": (3, 4),
        "down_room": (4, 2),
        "current_marker": (90.0, 80.0),
        "boss_marker": (120.0, 20.0),
        "query_marker": (88.0, 20.0),
        "elite_marker": (120.0, 20.0),
        "down_marker": (88.0, 20.0),
    }
    navigator._door_candidates_from_objects = lambda objects: []  # type: ignore[method-assign]

    snapshot = navigator.build_route_snapshot(np.zeros((600, 800, 3), dtype=np.uint8), [])

    assert snapshot.target_kind == "query"
    assert snapshot.target_room == (4, 2)
    assert snapshot.next_room_direction == "left"


def test_visible_right_door_and_marker_override_wrong_left_grid_step() -> None:
    navigator = MiniMapNavigator.__new__(MiniMapNavigator)
    navigator.spec = MAP_SPECS["universal"]
    navigator.last_direction = None
    navigator.get_debug_scores = lambda frame: {}  # type: ignore[method-assign]
    navigator.detect_room_markers = lambda frame: {  # type: ignore[method-assign]
        "current_room": (4, 3),
        "boss_room": (3, 4),
        "query_room": (3, 2),
        "elite_room": (3, 4),
        "down_room": (4, 2),
        "current_marker": (90.0, 80.0),
        "boss_marker": (140.0, 55.0),
        "query_marker": (150.0, 72.0),
        "elite_marker": (140.0, 55.0),
        "down_marker": (88.0, 85.0),
    }

    snapshot = navigator.build_route_snapshot(
        np.zeros((600, 800, 3), dtype=np.uint8),
        [
            {"player": {"xywh": [75.1953125, 294.921875, 69.3359375, 128.125], "conf": 0.9}},
            {"door": {"xywh": [518.359375, 291.796875, 82.8125, 93.75], "conf": 0.89}},
            {"door": {"xywh": [18.26171875, 401.953125, 84.08203125, 80.46875], "conf": 0.6}},
        ],
    )

    assert snapshot.target_kind == "query"
    assert snapshot.target_room == (3, 2)
    assert snapshot.next_room_direction == "right"
    assert snapshot.selected_door_center == (559.765625, 338.671875)


def test_only_universal_map_spec_is_available() -> None:
    assert list(MAP_SPECS) == ["universal"]
