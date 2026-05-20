from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from dnf.skill_detector import SkillReadinessDetector


def _write_image(path: Path, image: np.ndarray) -> None:
    assert cv2.imwrite(str(path), image)


def test_skill_detector_uses_ready_template_over_cooldown(tmp_path: Path) -> None:
    ready = np.zeros((12, 12, 3), dtype=np.uint8)
    ready[:, :] = (0, 180, 255)
    ready[3:9, 3:9] = (255, 255, 255)
    cooldown = np.zeros((12, 12, 3), dtype=np.uint8)
    cooldown[:, :] = (40, 40, 40)
    cooldown[3:9, 3:9] = (90, 90, 90)
    _write_image(tmp_path / "jn.png", ready)
    _write_image(tmp_path / "jn1.png", cooldown)

    frame = np.zeros((80, 120, 3), dtype=np.uint8)
    frame[60:72, 50:62] = ready

    detector = SkillReadinessDetector(tmp_path)
    detector.threshold = 0.9
    detector.margin = 0.03

    is_ready, scores = detector.detect(frame)

    assert is_ready is True
    assert scores["ready"] >= 0.99


def test_skill_detector_rejects_cooldown_template(tmp_path: Path) -> None:
    ready = np.zeros((12, 12, 3), dtype=np.uint8)
    ready[:, :] = (0, 180, 255)
    ready[3:9, 3:9] = (255, 255, 255)
    cooldown = np.zeros((12, 12, 3), dtype=np.uint8)
    cooldown[:, :] = (40, 40, 40)
    cooldown[3:9, 3:9] = (90, 90, 90)
    _write_image(tmp_path / "jn.png", ready)
    _write_image(tmp_path / "jn1.png", cooldown)

    frame = np.zeros((80, 120, 3), dtype=np.uint8)
    frame[60:72, 50:62] = cooldown

    detector = SkillReadinessDetector(tmp_path)
    detector.threshold = 0.9
    detector.margin = 0.03

    is_ready, scores = detector.detect(frame)

    assert is_ready is False
    assert scores["cooldown"] >= 0.99
