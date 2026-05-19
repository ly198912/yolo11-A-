from __future__ import annotations

import pytest

import dnf.timed_keys as timed_keys
from dnf.timed_keys import DEFAULT_TIMED_KEY_SPEC, TimedKeyRule, TimedKeyScheduler, parse_timed_key_spec


def test_default_timed_key_spec() -> None:
    assert parse_timed_key_spec(DEFAULT_TIMED_KEY_SPEC) == [
        TimedKeyRule("d", 5.0, 6.0, 1.0, 1.5),
        TimedKeyRule("s", 12.0, 13.0, 1.0, 1.5),
        TimedKeyRule("e", 6.0, 7.0, 1.0, 1.5),
    ]


def test_timed_key_spec_rejects_invalid_range() -> None:
    with pytest.raises(ValueError):
        parse_timed_key_spec("d:6.0-5.0:1.0-1.5")


def test_timed_key_scheduler_pause_releases_keys(monkeypatch) -> None:
    released: list[str] = []
    monkeypatch.setattr(timed_keys.pydirectinput, "keyUp", released.append)

    scheduler = TimedKeyScheduler([TimedKeyRule("q", 1.0, 1.0, 0.5, 0.5)])

    scheduler.pause()
    assert scheduler.paused is True
    assert released == ["q"]

    scheduler.resume()
    assert scheduler.paused is False
