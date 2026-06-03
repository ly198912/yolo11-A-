import pytest

from dnf.main import TARGET_FRAME_SECONDS, _focus_window, _limit_frame_rate


def test_focus_window_activates_dnf_when_another_window_has_focus(monkeypatch):
    events = []

    monkeypatch.setattr("dnf.main.win32gui.GetForegroundWindow", lambda: 123)
    monkeypatch.setattr(
        "dnf.main.win32gui.ShowWindow",
        lambda hwnd, command: events.append(("show", hwnd, command)),
    )
    monkeypatch.setattr(
        "dnf.main.win32gui.SetForegroundWindow",
        lambda hwnd: events.append(("focus", hwnd)),
    )

    _focus_window(456)

    assert events == [
        ("show", 456, 9),
        ("focus", 456),
    ]


def test_focus_window_does_nothing_when_dnf_already_has_focus(monkeypatch):
    events = []

    monkeypatch.setattr("dnf.main.win32gui.GetForegroundWindow", lambda: 456)
    monkeypatch.setattr(
        "dnf.main.win32gui.ShowWindow",
        lambda hwnd, command: events.append(("show", hwnd, command)),
    )
    monkeypatch.setattr(
        "dnf.main.win32gui.SetForegroundWindow",
        lambda hwnd: events.append(("focus", hwnd)),
    )

    _focus_window(456)

    assert events == []


def test_limit_frame_rate_sleeps_only_when_loop_is_faster_than_target(monkeypatch):
    sleeps = []

    monkeypatch.setattr("dnf.main.time.perf_counter", lambda: 10.02)
    monkeypatch.setattr("dnf.main.time.sleep", lambda seconds: sleeps.append(seconds))

    slept = _limit_frame_rate(10.0)

    assert slept == pytest.approx(TARGET_FRAME_SECONDS - 0.02)
    assert sleeps == [pytest.approx(TARGET_FRAME_SECONDS - 0.02)]


def test_limit_frame_rate_does_not_slow_down_expensive_frame(monkeypatch):
    sleeps = []

    monkeypatch.setattr("dnf.main.time.perf_counter", lambda: 10.2)
    monkeypatch.setattr("dnf.main.time.sleep", lambda seconds: sleeps.append(seconds))

    slept = _limit_frame_rate(10.0)

    assert slept == 0.0
    assert sleeps == []
