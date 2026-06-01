from dnf.minimap_nav import (
    MARKER_THRESHOLDS,
    QUERY_CONFIRM_FRAMES,
    QUERY_MISS_TOLERANCE_FRAMES,
    MiniMapNavigator,
)


def test_query_marker_threshold_rejects_weak_matches():
    assert MARKER_THRESHOLDS["query"] == 0.62


def test_query_marker_requires_consecutive_confirmations():
    navigator = MiniMapNavigator("generic")
    marker = (42.0, 18.0)

    for _ in range(QUERY_CONFIRM_FRAMES - 1):
        assert navigator._stabilize_query_room((1, 3), marker) == (None, None)

    assert navigator._stabilize_query_room((1, 3), marker) == ((1, 3), marker)


def test_confirmed_query_marker_tolerates_brief_detection_gaps():
    navigator = MiniMapNavigator("generic")
    marker = (42.0, 18.0)

    for _ in range(QUERY_CONFIRM_FRAMES):
        navigator._stabilize_query_room((1, 3), marker)

    for _ in range(QUERY_MISS_TOLERANCE_FRAMES):
        assert navigator._stabilize_query_room(None, None) == ((1, 3), marker)

    assert navigator._stabilize_query_room(None, None) == (None, None)
