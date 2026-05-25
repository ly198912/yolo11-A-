from __future__ import annotations

import os
from pathlib import Path

import cv2
import numpy as np
from loguru import logger


class SkillReadinessDetector:
    def __init__(self, assets_dir: Path | None = None) -> None:
        self.assets_dir = assets_dir or (Path(__file__).resolve().parent / "res")
        self.enabled = os.getenv("DNF_SKILL_ICON_ENABLED", "1") == "1"
        self.threshold = float(os.getenv("DNF_SKILL_ICON_THRESHOLD", "0.86"))
        self.margin = float(os.getenv("DNF_SKILL_ICON_MARGIN", "0.03"))
        self.search_bottom_ratio = float(os.getenv("DNF_SKILL_ICON_SEARCH_BOTTOM_RATIO", "0.55"))
        self.ready_template = self._load_template_optional("jn.png")
        self.cooldown_template = self._load_template_optional("jn1.png")
        if self.enabled and self.ready_template is None:
            logger.warning("skill ready template missing: {}", self.assets_dir / "jn.png")

    def _load_template_optional(self, filename: str) -> np.ndarray | None:
        path = self.assets_dir / filename
        if not path.exists():
            return None
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        return image

    @staticmethod
    def _score(image: np.ndarray, template: np.ndarray | None) -> float:
        if template is None:
            return 0.0
        image_h, image_w = image.shape[:2]
        template_h, template_w = template.shape[:2]
        if template_h > image_h or template_w > image_w:
            return 0.0
        result = cv2.matchTemplate(image, template, cv2.TM_SQDIFF_NORMED)
        min_val, _, _, _ = cv2.minMaxLoc(result)
        return float(max(0.0, 1.0 - min_val))

    def detect(self, frame_bgr: np.ndarray) -> tuple[bool | None, dict[str, float]]:
        if not self.enabled or self.ready_template is None:
            return None, {}

        height = frame_bgr.shape[0]
        start_y = max(0, min(height - 1, int(height * self.search_bottom_ratio)))
        search_region = frame_bgr[start_y:height, :]
        ready_score = self._score(search_region, self.ready_template)
        cooldown_score = self._score(search_region, self.cooldown_template)
        scores = {
            "ready": round(ready_score, 4),
            "cooldown": round(cooldown_score, 4),
        }
        ready = ready_score >= self.threshold and ready_score >= cooldown_score + self.margin
        return ready, scores
