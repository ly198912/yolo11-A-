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
    Game._last_player_center = None
    Game._room_entry_position = None
    Game._room_entry_time = 0.0
    Game._player_missing_count = 0
    Game._player_missing_started_at = None
    Game._missing_player_recovery_attempted = False
    Game._missing_player_recovery_attempts = 0
    Game._missing_player_next_recovery_at = 0.0
    Game._right_edge_missing_started_at = None
    Game._right_edge_recovery_attempted = False
    Game._cached_money_target = None
    Game._cached_money_seen_at = 0.0


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


def test_missing_player_recovery_waits_for_elapsed_time(monkeypatch):
    _reset_game_state()
    recoveries = []

    class DryGame(Game):
        def _start_stuck_recovery(self):
            recoveries.append("generic")

        def _release_movement(self):
            return None

    monkeypatch.setattr("dnf.game.time.time", lambda: 1.0)
    Game._pre_player = {"xywh": [300.0, 200.0, 80.0, 100.0]}
    Game._player_missing_count = 999
    Game._player_missing_started_at = 0.5

    DryGame([], 800, 600, None).run()

    assert recoveries == []


def test_missing_player_without_cached_center_uses_astar_direction(monkeypatch):
    _reset_game_state()
    moves = []

    class DryGame(Game):
        def _move(self, direction, is_slow=False, press_time=0.1, release_time=0.1):
            moves.append((direction, is_slow))

        def _start_stuck_recovery(self):
            raise AssertionError("no cached player center should use route direction first")

    monkeypatch.setattr("dnf.game.time.time", lambda: 1.0)
    Game._player_missing_started_at = 0.0

    DryGame([], 800, 600, "UP").run()

    assert moves == [("UP", True)]


def test_missing_player_recovery_does_not_wait_for_frame_count(monkeypatch):
    _reset_game_state()
    recoveries = []

    class DryGame(Game):
        def _start_stuck_recovery(self):
            recoveries.append("generic")

    monkeypatch.setattr("dnf.game.time.time", lambda: 1.0)
    Game._pre_player = {"xywh": [300.0, 200.0, 80.0, 100.0]}
    Game._player_missing_started_at = 0.0

    DryGame([], 800, 600, None).run()

    assert Game._player_missing_count == 1
    assert recoveries == ["generic"]


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
    Game._player_missing_started_at = 0.0

    DryGame([], 800, 600, None).run()

    assert Game._missing_player_recovery_attempted is True
    assert Game._missing_player_recovery_attempts == 1
    assert Game._recovery_active is True
    assert events == [
        ("release",),
        ("down", "down"),
        ("sleep", 0.4),
        ("up", "down"),
        ("release",),
        ("down", "right"),
    ]


def test_long_missing_player_retries_controlled_recovery_after_cooldown(monkeypatch):
    _reset_game_state()
    recoveries = []
    now = [1.0]

    class DryGame(Game):
        def _start_stuck_recovery(self):
            recoveries.append(now[0])

        def _release_movement(self):
            return None

    monkeypatch.setattr("dnf.game.time.time", lambda: now[0])
    Game._pre_player = {"xywh": [300.0, 200.0, 80.0, 100.0]}
    Game._player_missing_started_at = 0.0
    game = DryGame([], 800, 600, "DOWN")

    game.run()
    now[0] = 3.99
    game.run()
    now[0] = 4.0
    game.run()
    now[0] = 7.0
    game.run()
    now[0] = 10.0
    game.run()

    assert recoveries == [1.0, 4.0, 7.0]
    assert Game._missing_player_recovery_attempts == Game._missing_player_recovery_max_attempts


def test_missing_player_near_route_edge_continues_room_transition(monkeypatch):
    _reset_game_state()
    moves = []

    class DryGame(Game):
        def _move(self, direction, is_slow=False, press_time=0.1, release_time=0.1):
            moves.append((direction, is_slow))

        def _start_stuck_recovery(self):
            raise AssertionError("edge transition should not start generic recovery")

    monkeypatch.setattr("dnf.game.time.time", lambda: 1.0)
    Game._pre_player = {"xywh": [700.0, 200.0, 80.0, 100.0]}
    Game._player_missing_started_at = 0.0

    DryGame([], 800, 600, "RIGHT").run()

    assert moves == [("RIGHT", True)]


def test_missing_player_stalled_near_right_edge_aligns_up_then_down(monkeypatch):
    _reset_game_state()
    events = []

    class DryGame(Game):
        def _release_direction_keys(self):
            events.append(("release",))

        def _key_down(self, key):
            events.append(("down", key))

        def _key_up(self, key):
            events.append(("up", key))

        def _start_stuck_recovery(self):
            raise AssertionError("right-edge doorway recovery should stay isolated")

    monkeypatch.setattr("dnf.game.time.time", lambda: 2.0)
    monkeypatch.setattr("dnf.game.time.sleep", lambda seconds: events.append(("sleep", seconds)))
    Game._pre_player = {"xywh": [700.0, 200.0, 80.0, 100.0]}
    Game._player_missing_started_at = 0.0
    Game._right_edge_missing_started_at = 1.0

    DryGame([], 800, 600, "RIGHT").run()

    assert Game._right_edge_recovery_attempted is True
    assert events == [
        ("release",),
        ("down", "right"),
        ("down", "up"),
        ("sleep", Game._right_edge_vertical_seconds),
        ("up", "up"),
        ("down", "down"),
        ("sleep", Game._right_edge_vertical_seconds),
        ("up", "down"),
    ]


def test_missing_player_stalled_away_from_right_edge_uses_existing_recovery(monkeypatch):
    _reset_game_state()
    recoveries = []

    class DryGame(Game):
        def _start_stuck_recovery(self):
            recoveries.append("generic")

    monkeypatch.setattr("dnf.game.time.time", lambda: 1.0)
    Game._pre_player = {"xywh": [300.0, 200.0, 80.0, 100.0]}
    Game._player_missing_started_at = 0.0

    DryGame([], 800, 600, "RIGHT").run()

    assert recoveries == ["generic"]
    assert Game._right_edge_recovery_attempted is False


def test_missing_player_near_right_edge_with_other_route_uses_existing_recovery(monkeypatch):
    _reset_game_state()
    recoveries = []

    class DryGame(Game):
        def _start_stuck_recovery(self):
            recoveries.append("generic")

    monkeypatch.setattr("dnf.game.time.time", lambda: 1.0)
    Game._pre_player = {"xywh": [700.0, 200.0, 80.0, 100.0]}
    Game._player_missing_started_at = 0.0

    DryGame([], 800, 600, "UP").run()

    assert recoveries == ["generic"]
    assert Game._right_edge_recovery_attempted is False


def test_visible_player_stalled_near_right_edge_uses_doorway_alignment():
    _reset_game_state()
    recoveries = []

    class DryGame(Game):
        def _update_motion_state(self, expect_motion, player_visible):
            return True

        def _start_right_edge_door_recovery(self, target_door=None):
            recoveries.append(("right-edge", target_door))

        def _start_stuck_recovery(self):
            recoveries.append("generic")

    player = {"player": {"xywh": [700.0, 200.0, 80.0, 100.0]}}

    DryGame([player], 800, 600, "RIGHT").run()

    assert recoveries == [("right-edge", None)]


def test_right_edge_route_uses_visible_edge_door_even_when_door_is_left_of_player(monkeypatch):
    _reset_game_state()
    moves = []

    class DryGame(Game):
        def _move(self, direction, is_slow=False, press_time=0.1, release_time=0.1):
            moves.append((direction, is_slow))

    player = {"player": {"xywh": [777.5, 445.4, 22.5, 115.8]}}
    left_door = {"door": {"xywh": [0.1, 494.8, 59.1, 100.3], "conf": 0.82}}
    right_door = {"door": {"xywh": [702.8, 333.1, 77.8, 104.1], "conf": 0.78}}

    DryGame([left_door, right_door, player], 800, 600, "RIGHT").run()

    assert moves == [("UP", False)]


def test_right_edge_stall_aligns_to_visible_edge_door_y(monkeypatch):
    _reset_game_state()
    events = []

    class DryGame(Game):
        def _update_motion_state(self, expect_motion, player_visible):
            return True

        def _release_direction_keys(self):
            events.append(("release",))

        def _key_down(self, key):
            events.append(("down", key))

        def _key_up(self, key):
            events.append(("up", key))

    monkeypatch.setattr("dnf.game.time.sleep", lambda seconds: events.append(("sleep", round(seconds, 3))))
    player = {"player": {"xywh": [777.5, 445.4, 22.5, 115.8]}}
    right_door = {"door": {"xywh": [702.8, 333.1, 77.8, 104.1], "conf": 0.78}}

    DryGame([right_door, player], 800, 600, "RIGHT").run()

    assert events == [
        ("release",),
        ("down", "right"),
        ("down", "up"),
        ("sleep", 0.454),
        ("up", "up"),
    ]


def test_no_route_and_no_targets_holds_without_stuck_recovery():
    _reset_game_state()
    events = []

    class DryGame(Game):
        def _release_direction_keys(self):
            events.append(("release",))

        def _start_stuck_recovery(self):
            events.append(("generic_recovery",))

    Game._motion_active = True
    player = {"player": {"xywh": [760.0, 480.0, 60.0, 100.0]}}

    DryGame([player], 800, 600, None).run()

    assert events == [("release",)]
    assert Game._motion_active is False
