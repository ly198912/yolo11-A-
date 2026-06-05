import cv2
import numpy as np

import dnf.ui_detector as ui_detector


def test_try_again_template_matches_embedded_resource():
    ui_detector._try_again_template_gray = None
    template = ui_detector._load_try_again_template()
    assert template is not None

    frame = np.zeros((160, 260, 3), dtype=np.uint8)
    template_rgb = cv2.cvtColor(template, cv2.COLOR_GRAY2RGB)
    height, width = template.shape[:2]
    frame[70:70 + height, 120:120 + width] = template_rgb

    assert ui_detector.is_try_again_template_prompt(frame) is True


def test_reward_template_matches_embedded_resource():
    ui_detector._reward_template_gray = None
    template = ui_detector._load_reward_template()
    assert template is not None

    frame = np.zeros((220, 320, 3), dtype=np.uint8)
    template_rgb = cv2.cvtColor(template, cv2.COLOR_GRAY2RGB)
    height, width = template.shape[:2]
    frame[80:80 + height, 140:140 + width] = template_rgb

    assert ui_detector.is_reward_template_prompt(frame) is True
    assert ui_detector.is_reward_selection_screen(frame) is True


def test_try_again_handler_waits_random_delay_and_presses_num6(monkeypatch):
    ui_detector._last_retry_press_time = 0.0
    events = []

    monkeypatch.setattr(ui_detector, "is_retry_challenge_prompt", lambda frame: True)
    monkeypatch.setattr(ui_detector.time, "time", lambda: 10.0)
    monkeypatch.setattr(ui_detector.random, "uniform", lambda start, end: 0.73)
    monkeypatch.setattr(ui_detector.time, "sleep", lambda seconds: events.append(("sleep", seconds)))
    monkeypatch.setattr(ui_detector.input_backend, "keyUp", lambda key: events.append(("up", key)))
    monkeypatch.setattr(ui_detector.input_backend, "press", lambda key: events.append(("press", key)))

    assert ui_detector.handle_retry_challenge_prompt(np.zeros((120, 180, 3), dtype=np.uint8)) is True

    assert events == [
        ("up", "up"),
        ("up", "down"),
        ("up", "left"),
        ("up", "right"),
        ("sleep", 0.73),
        ("press", "num6"),
    ]


def test_reward_handler_waits_random_delay_and_presses_random_reward_key(monkeypatch):
    ui_detector._last_reward_select_press_time = 0.0
    events = []

    monkeypatch.setattr(ui_detector, "is_reward_selection_screen", lambda frame: True)
    monkeypatch.setattr(ui_detector.time, "time", lambda: 20.0)
    monkeypatch.setattr(ui_detector.random, "uniform", lambda start, end: 1.62)
    monkeypatch.setattr(ui_detector.random, "randint", lambda start, end: 3)
    monkeypatch.setattr(ui_detector.time, "sleep", lambda seconds: events.append(("sleep", seconds)))
    monkeypatch.setattr(ui_detector.input_backend, "keyUp", lambda key: events.append(("up", key)))
    monkeypatch.setattr(ui_detector.input_backend, "press", lambda key: events.append(("press", key)))

    assert ui_detector.handle_reward_selection_screen(np.zeros((120, 180, 3), dtype=np.uint8)) is True

    assert events == [
        ("up", "up"),
        ("up", "down"),
        ("up", "left"),
        ("up", "right"),
        ("sleep", 1.62),
        ("press", "3"),
    ]


def test_end_reward_handler_does_not_block_retry_prompt(monkeypatch):
    monkeypatch.setattr(ui_detector, "is_retry_challenge_prompt", lambda frame: True)
    monkeypatch.setattr(ui_detector, "is_end_reward_screen", lambda frame: True)

    assert ui_detector.handle_end_reward_screen(np.zeros((120, 180, 3), dtype=np.uint8)) is False
