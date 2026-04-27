from __future__ import annotations

import time
from typing import Optional, Tuple

import cv2
import numpy as np
import pydirectinput
from loguru import logger


RETRY_COOLDOWN_SECONDS = 3.0
_last_retry_press_time = 0.0


def _press_numpad_6() -> None:
    pydirectinput.KEYBOARD_MAPPING.setdefault("num6", 0x4D)
    pydirectinput.keyDown("num6")
    time.sleep(0.08)
    pydirectinput.keyUp("num6")


def _release_movement_keys() -> None:
    for key in ("up", "down", "left", "right"):
        pydirectinput.keyUp(key)


def _retry_prompt_roi(frame_rgb: np.ndarray) -> np.ndarray:
    height, width = frame_rgb.shape[:2]
    x1 = 0
    x2 = min(width, int(width * 0.24))
    y1 = max(0, int(height * 0.78))
    y2 = min(height, int(height * 0.895))
    return frame_rgb[y1:y2, x1:x2]


def _yellow_text_stats(roi_rgb: np.ndarray) -> Tuple[int, int, Optional[Tuple[int, int, int, int]]]:
    hsv = cv2.cvtColor(roi_rgb, cv2.COLOR_RGB2HSV)
    yellow_mask = cv2.inRange(hsv, np.array([15, 80, 110]), np.array([42, 255, 255]))
    yellow_mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_OPEN, np.ones((2, 2), dtype=np.uint8))
    count, _, stats, _ = cv2.connectedComponentsWithStats(yellow_mask, connectivity=8)

    yellow_pixels = int(cv2.countNonZero(yellow_mask))
    text_like_components = 0
    xs = []
    ys = []
    for index in range(1, count):
        area = int(stats[index, cv2.CC_STAT_AREA])
        width = int(stats[index, cv2.CC_STAT_WIDTH])
        height = int(stats[index, cv2.CC_STAT_HEIGHT])
        if 3 <= area <= 120 and 1 <= width <= 24 and 3 <= height <= 18:
            text_like_components += 1
            left = int(stats[index, cv2.CC_STAT_LEFT])
            top = int(stats[index, cv2.CC_STAT_TOP])
            xs.extend([left, left + width])
            ys.extend([top, top + height])

    if not xs or not ys:
        return yellow_pixels, text_like_components, None
    return yellow_pixels, text_like_components, (min(xs), min(ys), max(xs), max(ys))


def is_retry_challenge_prompt(frame_rgb: np.ndarray) -> bool:
    roi = _retry_prompt_roi(frame_rgb)
    if roi.size == 0:
        return False

    yellow_pixels, text_like_components, bbox = _yellow_text_stats(roi)
    if bbox is None:
        return False

    x1, y1, x2, y2 = bbox
    text_width = x2 - x1
    text_height = y2 - y1
    return (
        30 <= yellow_pixels <= 700
        and 4 <= text_like_components <= 35
        and 70 <= text_width <= roi.shape[1]
        and 6 <= text_height <= 32
    )


def handle_retry_challenge_prompt(frame_rgb: np.ndarray) -> bool:
    global _last_retry_press_time

    if not is_retry_challenge_prompt(frame_rgb):
        return False

    now = time.time()
    if now - _last_retry_press_time < RETRY_COOLDOWN_SECONDS:
        return True

    _release_movement_keys()
    _press_numpad_6()
    _last_retry_press_time = now
    logger.info("retry challenge prompt detected, press Numpad_6")
    return True
