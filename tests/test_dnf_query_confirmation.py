import numpy as np

from dnf.map_specs import MAP_SPECS
from dnf.minimap_nav import (
    MARKER_THRESHOLDS,
    QUERY_CONFIRM_SECONDS,
    QUERY_MISS_TOLERANCE_SECONDS,
    MiniMapNavigator,
)


def test_generic_minimap_region_expands_without_changing_grid_shape():
    spec = MAP_SPECS["generic"]

    assert spec.crop_rect_800 == (592, 25, 800, 230)
    assert spec.room_rect_800 == (612, 35, 791, 156)
    assert spec.crop_rect_1067 == (790, 25, 1067, 230)
    assert spec.room_rect_1067 == (816, 35, 1055, 156)
    assert (spec.rows, spec.cols) == (7, 8)


def test_generic_room_rect_keeps_vertically_adjacent_query_out_of_current_room():
    navigator = MiniMapNavigator("generic")
    frame = np.zeros((600, 800, 3), dtype=np.uint8)
    minimap = navigator.extract_minimap(frame)

    assert navigator.compute_room_id(98.5, 37.0, minimap) == (1, 3)
    assert navigator.compute_room_id(99.0, 53.0, minimap) == (2, 3)
    assert navigator.compute_room_id(188.0, 71.5, minimap) == (3, 7)


def test_query_candidate_prefers_strongest_valid_match_over_closer_weak_match():
    navigator = MiniMapNavigator("generic")
    minimap = np.zeros((195, 204, 3), dtype=np.uint8)
    matches = [
        (0.70, 114.75, 41.75, "query"),
        (0.96, 140.25, 41.75, "query"),
    ]

    room, marker = navigator._closest_query_room_and_center_from_matches(
        matches,
        minimap,
        current_room=(1, 3),
    )

    assert room == (1, 5)
    assert marker == (140.25, 41.75)


def test_query_marker_threshold_rejects_weak_matches():
    assert MARKER_THRESHOLDS["query"] == 0.62


def test_query_marker_requires_consecutive_confirmation_time(monkeypatch):
    navigator = MiniMapNavigator("generic")
    marker = (42.0, 18.0)
    now = [10.0]
    monkeypatch.setattr("dnf.minimap_nav.time.monotonic", lambda: now[0])

    assert navigator._stabilize_query_room((1, 3), marker) == (None, None)

    now[0] += QUERY_CONFIRM_SECONDS - 0.01
    assert navigator._stabilize_query_room((1, 3), marker) == (None, None)

    now[0] += 0.011
    assert navigator._stabilize_query_room((1, 3), marker) == ((1, 3), marker)


def test_confirmed_query_marker_tolerates_brief_detection_gaps(monkeypatch):
    navigator = MiniMapNavigator("generic")
    marker = (42.0, 18.0)
    now = [10.0]
    monkeypatch.setattr("dnf.minimap_nav.time.monotonic", lambda: now[0])

    navigator._stabilize_query_room((1, 3), marker)
    now[0] += QUERY_CONFIRM_SECONDS + 0.001
    navigator._stabilize_query_room((1, 3), marker)

    now[0] += QUERY_MISS_TOLERANCE_SECONDS - 0.01
    assert navigator._stabilize_query_room(None, None) == ((1, 3), marker)

    now[0] += 0.02
    assert navigator._stabilize_query_room(None, None) == (None, None)
