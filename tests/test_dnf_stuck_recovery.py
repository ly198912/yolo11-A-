from dnf.game import Game


def _reset_game_state():
    Game._motion_active = False
    Game._position_history.clear()
    Game._stuck_started_at = None
    Game._stuck_anchor = None
    Game._recovery_active = False
    Game._recovery_origin_x = None
    Game._recovery_started_at = None
    Game._player = None
    Game._pre_player = None
    Game._player_missing_count = 0
    Game._missing_player_recovery_attempted = False


def test_motion_stall_requires_point_six_seconds(monkeypatch):
    _reset_game_state()
    times = iter([1.0, 1.59, 1.60])
    monkeypatch.setattr("dnf.game.time.time", lambda: next(times))
    game = Game([], 800, 600, "RIGHT")
    game._player_xywh = [100.0, 200.0, 50.0, 100.0]

    assert game._update_motion_state(True, True) is False
    assert game._update_motion_state(True, True) is False
    assert game._update_motion_state(True, True) is True


def test_stuck_recovery_moves_down_once_then_right_until_fifty_pixels(monkeypatch):
    _reset_game_state()
    events = []

    class DryGame(Game):
        def _release_direction_keys(self):
            events.append(("release",))

        def _key_down(self, key):
            events.append(("down", key))

        def _key_up(self, key):
            events.append(("up", key))

    monkeypatch.setattr("dnf.game.random.uniform", lambda start, end: 0.4)
    monkeypatch.setattr("dnf.game.time.sleep", lambda seconds: events.append(("sleep", seconds)))
    game = DryGame([], 800, 600, "LEFT")
    game._player_xywh = [100.0, 200.0, 50.0, 100.0]

    game._start_stuck_recovery()

    assert events == [
        ("release",),
        ("down", "down"),
        ("sleep", 0.4),
        ("up", "down"),
        ("release",),
        ("down", "right"),
    ]
    assert Game._recovery_active is True

    game._player_xywh[0] = 149.0
    assert game._continue_stuck_recovery() is True
    assert Game._recovery_active is True

    game._player_xywh[0] = 150.0
    assert game._continue_stuck_recovery() is False
    assert Game._recovery_active is False
    assert ("down", "up") not in events


def test_missing_player_frames_keep_accumulating_stall_time(monkeypatch):
    _reset_game_state()
    times = iter([1.0, 1.3, 1.6])
    monkeypatch.setattr("dnf.game.time.time", lambda: next(times))
    game = Game([], 800, 600, "UP")
    game._player_xywh = [100.0, 200.0, 50.0, 100.0]

    assert game._update_motion_state(True, True) is False
    assert game._update_motion_state(True, False) is False
    assert game._update_motion_state(True, False) is True


def test_long_missing_player_starts_only_one_controlled_recovery(monkeypatch):
    _reset_game_state()
    events = []

    class DryGame(Game):
        def _release_direction_keys(self):
            events.append(("release",))

        def _key_down(self, key):
            events.append(("down", key))

        def _key_up(self, key):
            events.append(("up", key))

    monkeypatch.setattr("dnf.game.random.uniform", lambda start, end: 0.4)
    monkeypatch.setattr("dnf.game.time.sleep", lambda seconds: events.append(("sleep", seconds)))
    monkeypatch.setattr("dnf.game.time.time", lambda: 1.0)
    Game._pre_player = {"xywh": [100.0, 200.0, 50.0, 100.0]}
    Game._player_missing_count = Game._missing_player_recover_threshold - 1

    DryGame([], 800, 600, None).run()

    assert Game._missing_player_recovery_attempted is True
    assert Game._recovery_active is True
    assert events == [
        ("release",),
        ("down", "down"),
        ("sleep", 0.4),
        ("up", "down"),
        ("release",),
        ("down", "right"),
    ]
