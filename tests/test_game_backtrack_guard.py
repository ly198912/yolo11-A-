from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dnf.game import Game


def _reset_game_state() -> None:
    Game._action_cache = None
    Game._player = None
    Game._pre_player = None
    Game._index = 0
    Game._route_signature = None
    Game._forbidden_direction = None
    Game._exit_zone_frames = 0


def test_route_progress_sets_forbidden_backtrack_direction() -> None:
    _reset_game_state()
    game = Game([], width=1000, height=800, direction=["RIGHT", "UP"])
    game._player_xywh = [900.0, 400.0, 0.0, 0.0]

    for _ in range(3):
        game._update_route_progress()

    assert Game._index == 1
    assert Game._forbidden_direction == "LEFT"


def test_select_door_skips_forbidden_backtrack_door() -> None:
    _reset_game_state()
    game = Game([], width=1000, height=800, direction=["UP"])
    game._player_xywh = [500.0, 400.0, 0.0, 0.0]
    Game._forbidden_direction = "LEFT"

    doors = [
        {"xywh": [100.0, 360.0, 40.0, 80.0], "conf": 0.9},
        {"xywh": [820.0, 360.0, 40.0, 80.0], "conf": 0.9},
    ]

    selected = game._select_door(doors)

    assert selected is not None
    assert selected["xywh"][0] > game._player_xywh[0]
