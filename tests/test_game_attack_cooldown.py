from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dnf.game import Game


def test_monster_attack_does_not_press_x_every_frame(monkeypatch) -> None:
    Game._last_attack_time = 0.0
    Game._next_special_attack_time = 999.0
    Game._next_extra_attack_time = 999.0
    Game._attack_cooldown_seconds = 0.45
    now = 100.0
    monkeypatch.setattr("dnf.game.time.time", lambda: now)

    game = Game([], width=800, height=600, direction="RIGHT")
    game._player_xywh = [400.0, 300.0, 0.0, 0.0]
    pressed: list[str] = []
    release_count = 0

    def record_press(key: str) -> None:
        pressed.append(key)

    def record_release() -> None:
        nonlocal release_count
        release_count += 1
        Game._action_cache = None

    game._key_press = record_press  # type: ignore[method-assign]
    game._release_cached_action = record_release  # type: ignore[method-assign]

    game._kill_monster([430.0, 300.0, 0.0, 0.0])
    game._kill_monster([430.0, 300.0, 0.0, 0.0])

    assert pressed == ["right", "x"]
    assert release_count == 2


def test_monster_attack_can_press_x_after_cooldown(monkeypatch) -> None:
    Game._last_attack_time = 0.0
    Game._next_special_attack_time = 999.0
    Game._next_extra_attack_time = 999.0
    Game._attack_cooldown_seconds = 0.45
    current_time = 100.0
    monkeypatch.setattr("dnf.game.time.time", lambda: current_time)

    game = Game([], width=800, height=600, direction="RIGHT")
    game._player_xywh = [400.0, 300.0, 0.0, 0.0]
    pressed: list[str] = []

    game._key_press = pressed.append  # type: ignore[method-assign]
    game._release_cached_action = lambda: None  # type: ignore[method-assign]

    game._kill_monster([430.0, 300.0, 0.0, 0.0])
    current_time = 100.5
    game._kill_monster([430.0, 300.0, 0.0, 0.0])

    assert pressed == ["right", "x", "right", "x"]


def test_monster_attack_uses_q_with_random_cooldown(monkeypatch) -> None:
    Game._last_attack_time = 0.0
    Game._next_special_attack_time = 0.0
    Game._next_extra_attack_time = 999.0
    Game._attack_cooldown_seconds = 0.45
    Game._special_attack_cooldown_range = (8.0, 9.0)
    current_time = 100.0
    monkeypatch.setattr("dnf.game.time.time", lambda: current_time)
    monkeypatch.setattr("dnf.game.random.uniform", lambda start, end: 8.5)

    game = Game([], width=800, height=600, direction="RIGHT")
    game._player_xywh = [430.0, 300.0, 0.0, 0.0]
    pressed: list[str] = []

    game._key_press = pressed.append  # type: ignore[method-assign]
    game._release_cached_action = lambda: None  # type: ignore[method-assign]

    game._kill_monster([400.0, 300.0, 0.0, 0.0])

    assert pressed == ["left", "q"]
    assert Game._next_special_attack_time == 108.5


def test_monster_attack_skips_q_when_skill_icon_not_ready(monkeypatch) -> None:
    Game._last_attack_time = 0.0
    Game._next_special_attack_time = 0.0
    Game._next_extra_attack_time = 999.0
    Game._attack_cooldown_seconds = 0.45
    current_time = 100.0
    monkeypatch.setattr("dnf.game.time.time", lambda: current_time)

    game = Game([], width=800, height=600, direction="RIGHT", special_skill_ready=False)
    game._player_xywh = [430.0, 300.0, 0.0, 0.0]
    pressed: list[str] = []

    game._key_press = pressed.append  # type: ignore[method-assign]
    game._release_cached_action = lambda: None  # type: ignore[method-assign]

    game._kill_monster([400.0, 300.0, 0.0, 0.0])

    assert pressed == ["left", "x"]


def test_monster_moves_closer_before_pressing_attack() -> None:
    Game._next_special_attack_time = 999.0
    Game._next_extra_attack_time = 999.0
    game = Game([], width=800, height=600, direction="RIGHT")
    game._player_xywh = [400.0, 300.0, 0.0, 0.0]
    pressed: list[str] = []
    moves: list[str] = []

    game._key_press = pressed.append  # type: ignore[method-assign]

    def record_move(direction: str, **kwargs) -> str:
        moves.append(direction)
        return direction

    game._move = record_move  # type: ignore[method-assign]

    game._kill_monster([480.0, 300.0, 0.0, 0.0])

    assert pressed == []
    assert moves == ["RIGHT"]
