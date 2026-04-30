from __future__ import annotations

import random
import time
from typing import Optional, Tuple

import cv2
import numpy as np
import pydirectinput
from loguru import logger


RETRY_COOLDOWN_SECONDS = 3.0
REWARD_COOLDOWN_SECONDS = 1.0
_last_retry_press_time = 0.0
_last_reward_press_time = 0.0

ScreenOrigin = Tuple[int, int]


def _press_numpad_6() -> None:
    pydirectinput.KEYBOARD_MAPPING.setdefault("num6", 0x4D)
    pydirectinput.keyDown("num6")
    time.sleep(0.08)
    pydirectinput.keyUp("num6")


def _press_random_reward_key() -> str:
    key = random.choice(("1", "2", "3", "4"))
    pydirectinput.keyDown(key)
    time.sleep(0.08)
    pydirectinput.keyUp(key)
    time.sleep(0.08)
    return key


def _release_movement_keys() -> None:
    for key in ("up", "down", "left", "right"):
        pydirectinput.keyUp(key)


def _click_game_surface(frame_rgb: np.ndarray, screen_origin: ScreenOrigin = (0, 0)) -> None:
    height, width = frame_rgb.shape[:2]
    origin_x, origin_y = screen_origin
    pydirectinput.click(x=origin_x + max(1, width // 2), y=origin_y + max(1, height // 2))
    time.sleep(0.08)


def _retry_prompt_roi(frame_rgb: np.ndarray) -> np.ndarray:
    height, width = frame_rgb.shape[:2]
    x1 = max(0, int(width * 0.58))
    x2 = min(width, int(width * 0.98))
    y1 = max(0, int(height * 0.11))
    y2 = min(height, int(height * 0.18))
    return frame_rgb[y1:y2, x1:x2]


def _reward_title_roi(frame_rgb: np.ndarray) -> np.ndarray:
    height, width = frame_rgb.shape[:2]
    x1 = max(0, int(width * 0.28))
    x2 = min(width, int(width * 0.72))
    y1 = max(0, int(height * 0.02))
    y2 = min(height, int(height * 0.09))
    return frame_rgb[y1:y2, x1:x2]


def _reward_skip_roi(frame_rgb: np.ndarray) -> np.ndarray:
    height, width = frame_rgb.shape[:2]
    x1 = max(0, int(width * 0.82))
    x2 = min(width, int(width * 0.99))
    y1 = max(0, int(height * 0.07))
    y2 = min(height, int(height * 0.14))
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
        25 <= yellow_pixels <= 900
        and 4 <= text_like_components <= 45
        and 75 <= text_width <= roi.shape[1]
        and 8 <= text_height <= 26
    )


def is_reward_selection_prompt(frame_rgb: np.ndarray) -> bool:
    title_roi = _reward_title_roi(frame_rgb)
    if title_roi.size:
        yellow_pixels, text_like_components, bbox = _yellow_text_stats(title_roi)
        if bbox is not None:
            x1, y1, x2, y2 = bbox
            text_width = x2 - x1
            text_height = y2 - y1
            if (
                15 <= yellow_pixels <= 900
                and 2 <= text_like_components <= 60
                and 75 <= text_width <= title_roi.shape[1]
                and 6 <= text_height <= 32
            ):
                return True

    skip_roi = _reward_skip_roi(frame_rgb)
    if skip_roi.size == 0:
        return False
    yellow_pixels, text_like_components, bbox = _yellow_text_stats(skip_roi)
    if bbox is None:
        return False
    x1, y1, x2, y2 = bbox
    text_width = x2 - x1
    text_height = y2 - y1
    return (
        8 <= yellow_pixels <= 700
        and 1 <= text_like_components <= 40
        and 25 <= text_width <= skip_roi.shape[1]
        and 6 <= text_height <= 32
    )


def handle_reward_selection_prompt(frame_rgb: np.ndarray, screen_origin: ScreenOrigin = (0, 0)) -> bool:
    global _last_reward_press_time

    if not is_reward_selection_prompt(frame_rgb):
        return False

    now = time.time()
    if now - _last_reward_press_time < REWARD_COOLDOWN_SECONDS:
        return True

    _release_movement_keys()
    _click_game_surface(frame_rgb, screen_origin)
    key = _press_random_reward_key()
    _last_reward_press_time = now
    logger.info("reward selection prompt detected, press reward shortcut {}", key)
    return True


def handle_retry_challenge_prompt(frame_rgb: np.ndarray, screen_origin: ScreenOrigin = (0, 0)) -> bool:
    global _last_retry_press_time

    if not is_retry_challenge_prompt(frame_rgb):
        return False

    now = time.time()
    if now - _last_retry_press_time < RETRY_COOLDOWN_SECONDS:
        return True

    _release_movement_keys()
    _click_game_surface(frame_rgb, screen_origin)
    _press_numpad_6()
    _last_retry_press_time = now
    logger.info("retry challenge prompt detected, click game surface and press Numpad_6")
    return True
