from __future__ import annotations

import os
import random
import threading
import time
from dataclasses import dataclass
from typing import Callable, Iterable, Optional, Sequence

import pydirectinput
from loguru import logger


DEFAULT_TIMED_KEY_SPEC = "d:5.0-6.0:1.0-1.5;s:12.0-13.0:1.0-1.5;e:6.0-7.0:1.0-1.5"


@dataclass(frozen=True)
class TimedKeyRule:
    key: str
    interval_min: float
    interval_max: float
    hold_min: float
    hold_max: float

    def next_interval(self, rng: random.Random) -> float:
        return rng.uniform(self.interval_min, self.interval_max)

    def next_hold(self, rng: random.Random) -> float:
        return rng.uniform(self.hold_min, self.hold_max)


def _parse_range(value: str) -> tuple[float, float]:
    left, right = value.split("-", 1)
    min_value = float(left)
    max_value = float(right)
    if min_value < 0 or max_value < 0:
        raise ValueError("range values must be non-negative")
    if min_value > max_value:
        raise ValueError("range minimum must be <= maximum")
    return min_value, max_value


def parse_timed_key_spec(spec: str) -> list[TimedKeyRule]:
    rules: list[TimedKeyRule] = []
    for raw_item in spec.split(";"):
        item = raw_item.strip()
        if not item:
            continue
        key, interval_text, hold_text = [part.strip() for part in item.split(":", 2)]
        interval_min, interval_max = _parse_range(interval_text)
        hold_min, hold_max = _parse_range(hold_text)
        if not key:
            raise ValueError("key cannot be empty")
        rules.append(TimedKeyRule(key, interval_min, interval_max, hold_min, hold_max))
    return rules


class TimedKeyScheduler:
    def __init__(
        self,
        rules: Sequence[TimedKeyRule],
        *,
        rng: Optional[random.Random] = None,
        monotonic: Callable[[], float] = time.monotonic,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self._rules = list(rules)
        self._rng = rng or random.Random()
        self._monotonic = monotonic
        self._sleeper = sleeper
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    @property
    def rules(self) -> Sequence[TimedKeyRule]:
        return tuple(self._rules)

    def start(self) -> None:
        if not self._rules or (self._thread and self._thread.is_alive()):
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, name="dnf-timed-keys", daemon=True)
        self._thread.start()
        logger.info("timed key scheduler started: {}", self._rules)

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._thread = None
        for rule in self._rules:
            pydirectinput.keyUp(rule.key)
        logger.info("timed key scheduler stopped")

    def pause(self) -> None:
        if self._pause_event.is_set():
            return
        self._pause_event.set()
        self.release_keys()
        logger.info("timed key scheduler paused")

    def resume(self) -> None:
        if not self._pause_event.is_set():
            return
        self._pause_event.clear()
        logger.info("timed key scheduler resumed")

    @property
    def paused(self) -> bool:
        return self._pause_event.is_set()

    def release_keys(self) -> None:
        for rule in self._rules:
            pydirectinput.keyUp(rule.key)

    def _run(self) -> None:
        next_times = {
            rule.key: self._monotonic() + rule.next_interval(self._rng)
            for rule in self._rules
        }

        while not self._stop_event.is_set():
            if self._pause_event.is_set():
                self.release_keys()
                self._stop_event.wait(0.1)
                next_times = {
                    rule.key: self._monotonic() + rule.next_interval(self._rng)
                    for rule in self._rules
                }
                continue

            now = self._monotonic()
            due_rules = [rule for rule in self._rules if now >= next_times[rule.key]]
            if not due_rules:
                next_due = min(next_times.values())
                self._stop_event.wait(max(0.01, min(0.2, next_due - now)))
                continue

            for rule in due_rules:
                self._press_rule(rule)
                next_times[rule.key] = self._monotonic() + rule.next_interval(self._rng)

    def _press_rule(self, rule: TimedKeyRule) -> None:
        hold_seconds = rule.next_hold(self._rng)
        logger.info("timed key press: key={}, hold={:.2f}s", rule.key, hold_seconds)
        pydirectinput.keyDown(rule.key)
        deadline = self._monotonic() + hold_seconds
        while self._monotonic() < deadline:
            if self._stop_event.wait(0.03) or self._pause_event.is_set():
                pydirectinput.keyUp(rule.key)
                return
        pydirectinput.keyUp(rule.key)
        self._sleeper(0.03)


def build_timed_key_scheduler_from_env() -> Optional[TimedKeyScheduler]:
    if os.getenv("DNF_TIMED_KEYS_ENABLED", "1") != "1":
        return None

    spec = os.getenv("DNF_TIMED_KEYS", DEFAULT_TIMED_KEY_SPEC)
    try:
        rules = parse_timed_key_spec(spec)
    except Exception as exc:
        logger.warning("timed key spec invalid, disabled: {}", exc)
        return None
    if not rules:
        return None
    return TimedKeyScheduler(rules)
