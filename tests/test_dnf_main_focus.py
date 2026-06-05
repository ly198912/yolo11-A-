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


def test_focus_window_clicks_title_area_when_set_foreground_fails(monkeypatch):
    events = []

    monkeypatch.setattr("dnf.main.win32gui.GetForegroundWindow", lambda: 123)
    monkeypatch.setattr(
        "dnf.main.win32gui.ShowWindow",
        lambda hwnd, command: events.append(("show", hwnd, command)),
    )

    def fail_focus(hwnd):
        events.append(("focus", hwnd))
        raise RuntimeError("focus blocked")

    monkeypatch.setattr("dnf.main.win32gui.SetForegroundWindow", fail_focus)
    monkeypatch.setattr("dnf.main.win32gui.error", RuntimeError)
    monkeypatch.setattr("dnf.main.win32gui.GetWindowRect", lambda hwnd: (10, 20, 210, 420))
    monkeypatch.setattr("dnf.main.pyautogui.click", lambda x, y: events.append(("click", x, y)))

    _focus_window(456)

    assert events == [
        ("show", 456, 9),
        ("focus", 456),
        ("click", 110, 32),
    ]


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
