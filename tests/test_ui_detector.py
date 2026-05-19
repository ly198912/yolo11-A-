from __future__ import annotations

import numpy as np

import dnf.ui_detector as ui_detector


def _reset_reward_cache() -> None:
    ui_detector._reward_template = None
    ui_detector._reward_template_unavailable = False
    ui_detector._last_reward_miss_time = 0.0


def test_reward_prompt_detects_template(monkeypatch) -> None:
    _reset_reward_cache()
    template = np.zeros((12, 12, 3), dtype=np.uint8)
    template[3:9, 4:8] = (255, 220, 40)
    frame = np.zeros((80, 100, 3), dtype=np.uint8)
    frame[30:42, 45:57] = template

    template_gray = ui_detector.cv2.cvtColor(template, ui_detector.cv2.COLOR_RGB2GRAY)
    monkeypatch.setattr(ui_detector, "_load_reward_template", lambda: (template, template_gray))
    monkeypatch.setattr(ui_detector, "REWARD_TEMPLATE_THRESHOLD", 0.99)

    assert ui_detector.is_reward_selection_prompt(frame)


def test_reward_prompt_ignores_frame_when_template_misses(monkeypatch) -> None:
    _reset_reward_cache()
    monkeypatch.setattr(ui_detector, "_is_reward_template_like", lambda frame: False)

    assert not ui_detector.is_reward_selection_prompt(np.zeros((600, 800, 3), dtype=np.uint8))


def test_reward_prompt_does_not_match_blank_or_random_frames() -> None:
    _reset_reward_cache()

    blank = np.full((600, 800, 3), 255, dtype=np.uint8)
    random_frame = np.random.default_rng(1).integers(0, 255, (600, 800, 3), dtype=np.uint8)

    assert not ui_detector.is_reward_selection_prompt(blank)
    assert not ui_detector.is_reward_selection_prompt(random_frame)


def test_reward_prompt_presses_random_number_key(monkeypatch) -> None:
    _reset_reward_cache()
    actions: list[str] = []

    monkeypatch.setattr(ui_detector, "_last_reward_press_time", 0.0)
    monkeypatch.setattr(ui_detector, "is_reward_selection_prompt", lambda frame: True)
    monkeypatch.setattr(ui_detector.time, "time", lambda: 100.0)
    monkeypatch.setattr(ui_detector, "_release_movement_keys", lambda: actions.append("release"))
    monkeypatch.setattr(ui_detector, "_press_random_reward_number", lambda: actions.append("3") or "3")
    monkeypatch.setattr(ui_detector, "_click_game_surface", lambda *args, **kwargs: actions.append("click"))

    assert ui_detector.handle_reward_selection_prompt(np.zeros((600, 800, 3), dtype=np.uint8))
    assert actions == ["release", "3"]
