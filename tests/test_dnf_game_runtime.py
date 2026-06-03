import pytest

from dnf.game import Game


def test_hold_direction_releases_pressed_key_when_interrupted(monkeypatch):
    events = []

    monkeypatch.setattr("dnf.game.pydirectinput.keyDown", lambda key: events.append(("down", key)))
    monkeypatch.setattr("dnf.game.pydirectinput.keyUp", lambda key: events.append(("up", key)))
    monkeypatch.setattr(
        "dnf.game.time.sleep",
        lambda seconds: (_ for _ in ()).throw(KeyboardInterrupt()) if seconds == 0.8 else None,
    )

    Game._action_cache = None
    game = Game([], 800, 600)

    with pytest.raises(KeyboardInterrupt):
        game._hold_direction("RIGHT", 0.8)

    assert events == [("down", "right"), ("up", "right")]


def test_run_does_not_execute_fallback_move_after_handled_exception():
    class BrokenGame(Game):
        def __init__(self):
            super().__init__([], 800, 600)
            self.holds = []

        def _get_cls(self, cls_name):
            raise RuntimeError("detector payload is invalid")

        def _hold_direction(self, direction, seconds=0.8):
            self.holds.append((direction, seconds))

    Game._action_cache = None
    game = BrokenGame()

    game.run()

    assert game.holds == []
