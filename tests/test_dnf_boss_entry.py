import numpy as np

from dnf.minimap_nav import MiniMapNavigator


class SameGridBossNavigator(MiniMapNavigator):
    def detect_room_markers(self, frame):
        return {
            "current_room": (1, 7),
            "boss_room": (1, 7),
            "query_room": None,
            "elite_room": (1, 7),
            "down_room": None,
            "current_marker": (188.0, 50.5),
            "boss_marker": (188.0, 50.5),
            "query_marker": None,
            "elite_marker": (188.0, 50.5),
            "down_marker": None,
        }

    def get_debug_scores(self, frame):
        return {"hero": 0.9, "boss": 0.9}


class RightRouteOvershotDoorNavigator(MiniMapNavigator):
    def detect_room_markers(self, frame):
        return {
            "current_room": (2, 5),
            "boss_room": (1, 7),
            "query_room": None,
            "elite_room": (1, 7),
            "down_room": None,
            "current_marker": (152.5, 55.0),
            "boss_marker": (188.0, 35.5),
            "query_marker": None,
            "elite_marker": (188.0, 35.5),
            "down_marker": None,
        }

    def get_debug_scores(self, frame):
        return {"hero": 0.84, "boss": 0.88}


def test_same_grid_boss_uses_visible_door_as_entry_target():
    navigator = SameGridBossNavigator("generic")
    frame = np.zeros((600, 800, 3), dtype=np.uint8)
    objects = [
        {"player": {"xywh": [413.6, 386.0, 69.2, 120.6], "conf": 0.73}},
        {"door": {"xywh": [574.0, 299.9, 81.0, 88.6], "conf": 0.83}},
    ]

    snapshot = navigator.build_route_snapshot(frame, objects)

    assert snapshot.target_kind == "boss"
    assert snapshot.target_room == (1, 7)
    assert snapshot.next_room_direction == "right_up"
    assert snapshot.selected_door_center == (614.5, 344.2)


def test_same_grid_boss_uses_cached_player_center_when_current_frame_has_only_doors():
    navigator = SameGridBossNavigator("generic")
    frame = np.zeros((600, 800, 3), dtype=np.uint8)
    player = {"player": {"xywh": [413.6, 386.0, 69.2, 120.6], "conf": 0.73}}
    door = {"door": {"xywh": [697.6, 295.5, 82.6, 92.6], "conf": 0.82}}

    navigator.build_route_snapshot(frame, [player, door])
    snapshot = navigator.build_route_snapshot(frame, [door])

    assert snapshot.target_kind == "boss"
    assert snapshot.target_room == (1, 7)
    assert snapshot.next_room_direction == "right_up"
    assert snapshot.selected_door_center == (738.9, 341.8)


def test_right_route_uses_edge_side_door_after_player_overshoots_center():
    navigator = RightRouteOvershotDoorNavigator("generic")
    frame = np.zeros((600, 800, 3), dtype=np.uint8)
    objects = [
        {"door": {"xywh": [479.0, 292.0, 74.0, 83.0], "conf": 0.82}},
        {"player": {"xywh": [548.0, 322.0, 59.0, 114.0], "conf": 0.76}},
    ]

    snapshot = navigator.build_route_snapshot(frame, objects)

    assert snapshot.next_room_direction == "right"
    assert snapshot.selected_door_center == (516.0, 333.5)
