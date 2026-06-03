from dnf.game import Game
from dnf.hybrid_route import HybridRouteState, next_direction, shortest_path
from dnf.local_astar import local_next_direction
from dnf.minimap_grid_preview import save_minimap_grid_preview
from dnf.minimap_target import detect_red_target_route
from dnf.route_grid_preview import save_preview


def test_astar_next_direction_avoids_blocked_room():
    grid = [
        [0, 1, 0],
        [0, 1, 0],
        [0, 0, 0],
    ]

    assert shortest_path(grid, (0, 0), (0, 2), priority="RIGHT") == [
        (0, 0),
        (1, 0),
        (2, 0),
        (2, 1),
        (2, 2),
        (1, 2),
        (0, 2),
    ]
    assert next_direction(grid, (0, 0), (0, 2), priority="RIGHT") == "DOWN"


def test_local_astar_routes_character_around_blocked_cells():
    direction = local_next_direction(
        320,
        240,
        start=(48, 48),
        target=(272, 48),
        cell_size=32,
        blocked_rects=[(64, 0, 128, 180)],
    )

    assert direction == "DOWN"


def test_hybrid_route_advances_only_after_spawn_edge_is_seen():
    state = HybridRouteState(grid=[[0, 0, 0]], current_room=(0, 0), target_room=(0, 2))

    assert state.next_direction() == "RIGHT"
    state.mark_enter_attempt("RIGHT")
    state.observe([{"player": {"xywh": [720, 250, 60, 100], "conf": 0.9}}], 800, 600)
    assert state.current_room == (0, 0)

    state.observe([{"player": {"xywh": [20, 250, 60, 100], "conf": 0.9}}], 800, 600)

    assert state.current_room == (0, 1)
    assert state.backtrack_direction == "LEFT"
    assert state.next_direction() == "RIGHT"


def test_game_with_route_ignores_backtrack_door_and_uses_next_door():
    class DryGame(Game):
        def __init__(self, objects):
            super().__init__(objects, 800, 600, direction="RIGHT", backtrack_direction="LEFT", route_strict=True)
            self.holds = []

        def _hold_direction(self, direction, seconds=0.8):
            self.holds.append((direction, seconds))

    game = DryGame(
        [
            {"player": {"xywh": [360, 250, 80, 120], "conf": 0.99}},
            {"door": {"xywh": [8, 260, 70, 100], "conf": 0.9}},
            {"door": {"xywh": [720, 260, 70, 100], "conf": 0.9}},
        ]
    )

    result = game.run()

    assert game.holds == [("RIGHT", 0.45)]
    assert result["entered_direction"] == "RIGHT"


def test_game_searches_route_direction_when_only_backtrack_door_is_visible():
    class DryGame(Game):
        def __init__(self, objects):
            super().__init__(objects, 800, 600, direction="RIGHT", backtrack_direction="LEFT", route_strict=True)
            self.holds = []

        def _hold_direction(self, direction, seconds=0.8):
            self.holds.append((direction, seconds))

    Game._route_search_count = 0
    game = DryGame(
        [
            {"player": {"xywh": [360, 250, 80, 120], "conf": 0.99}},
            {"door": {"xywh": [8, 260, 70, 100], "conf": 0.9}},
        ]
    )

    result = game.run()

    assert game.holds == [("RIGHT", 0.45)]
    assert result["searched_direction"] == "RIGHT"


def test_game_holds_room_when_route_has_no_next_direction():
    class DryGame(Game):
        def __init__(self, objects):
            super().__init__(objects, 800, 600, direction=None, backtrack_direction="LEFT", route_strict=True)
            self.holds = []

        def _hold_direction(self, direction, seconds=0.8):
            self.holds.append((direction, seconds))

    game = DryGame(
        [
            {"player": {"xywh": [360, 250, 80, 120], "conf": 0.99}},
            {"door": {"xywh": [720, 260, 70, 100], "conf": 0.9}},
        ]
    )

    result = game.run()

    assert game.holds == []
    assert result["entered_direction"] is None
    assert result["searched_direction"] is None


def test_route_grid_preview_writes_png(tmp_path):
    out_path = tmp_path / "grid.png"

    save_preview("000/010/000", "0,0", "0,2", out_path)

    assert out_path.exists()
    assert out_path.stat().st_size > 0


def test_minimap_grid_preview_writes_png(tmp_path):
    out_path = tmp_path / "minimap_grid.png"

    save_minimap_grid_preview(out_path, rows=4, cols=5)

    assert out_path.exists()
    assert out_path.stat().st_size > 0


def test_minimap_red_target_route_detects_bull_head_direction():
    import cv2
    import numpy as np

    frame = np.zeros((600, 800, 3), dtype=np.uint8)
    frame[:, :] = (25, 25, 25)
    cv2.circle(frame, (720, 82), 4, (0, 80, 255), -1)
    cv2.rectangle(frame, (770, 77), (782, 89), (255, 20, 20), -1)

    route = detect_red_target_route(frame)

    assert route is not None
    assert route.kind == "red_boss"
    assert route.direction == "RIGHT"
    assert route.red_area > 0


def test_minimap_red_target_route_snaps_to_scaled_room_graph():
    import cv2
    import numpy as np

    frame = np.zeros((620, 1000, 3), dtype=np.uint8)
    frame[:, :] = (20, 20, 20)

    origin_x, origin_y = 780, 42
    cell, gap = 22, 7
    open_rooms = {
        (0, 0),
        (0, 2),
        (1, 0),
        (1, 2),
        (2, 0),
        (2, 1),
        (2, 2),
    }
    for row, col in open_rooms:
        x1 = origin_x + col * (cell + gap)
        y1 = origin_y + row * (cell + gap)
        cv2.rectangle(frame, (x1, y1), (x1 + cell, y1 + cell), (45, 180, 45), -1)

    current_x = origin_x + cell // 2
    current_y = origin_y + cell // 2
    target_x = origin_x + 2 * (cell + gap) + cell // 2
    target_y = origin_y + cell // 2
    cv2.circle(frame, (current_x, current_y), 4, (0, 80, 255), -1)
    cv2.rectangle(frame, (target_x - 5, target_y - 5), (target_x + 5, target_y + 5), (255, 20, 20), -1)

    route = detect_red_target_route(frame)

    assert route is not None
    assert route.current_room == (0, 0)
    assert route.target_room == (0, 2)
    assert route.direction == "DOWN"
    assert route.room_grid == [
        [0, 1, 0],
        [0, 1, 0],
        [0, 0, 0],
    ]
    assert 0.0 <= route.current_norm[0] <= 1.0
    assert 0.0 <= route.target_norm[0] <= 1.0


def test_minimap_rect_ignores_distant_colored_ui_noise():
    import cv2
    import numpy as np

    frame = np.zeros((600, 800, 3), dtype=np.uint8)
    frame[:, :] = (20, 20, 20)
    cv2.rectangle(frame, (470, 5), (535, 20), (40, 180, 40), -1)
    cv2.rectangle(frame, (680, 58), (700, 78), (45, 180, 45), -1)
    cv2.rectangle(frame, (768, 84), (790, 106), (45, 180, 45), -1)
    cv2.circle(frame, (690, 74), 4, (0, 80, 255), -1)
    cv2.rectangle(frame, (777, 88), (789, 100), (255, 20, 20), -1)

    route = detect_red_target_route(frame)

    assert route is not None
    assert route.minimap_rect == (600, 25, 800, 215)
    assert route.direction == "RIGHT"
