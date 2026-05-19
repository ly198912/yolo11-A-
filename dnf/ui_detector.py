from __future__ import annotations

import os
import random
import time
from pathlib import Path

import cv2
import numpy as np
import pydirectinput
from loguru import logger

RETRY_COOLDOWN_SECONDS = 3.0
REWARD_COOLDOWN_SECONDS = 1.0
REWARD_TEMPLATE_PATH = Path(__file__).resolve().parent / "res" / "Select your reward.png"
REWARD_TEMPLATE_THRESHOLD = float(os.getenv("DNF_REWARD_TEMPLATE_THRESHOLD", "0.88"))
REWARD_TEMPLATE_MEAN_DIFF_MAX = float(os.getenv("DNF_REWARD_TEMPLATE_MEAN_DIFF_MAX", "35"))
REWARD_CHECK_INTERVAL_SECONDS = float(os.getenv("DNF_REWARD_CHECK_INTERVAL", "0.5"))
_last_retry_press_time = 0.0
_last_reward_press_time = 0.0
_last_reward_miss_time = 0.0
_reward_template: tuple[np.ndarray, np.ndarray] | None = None
_reward_template_unavailable = False

ScreenOrigin = tuple[int, int]


def _press_numpad_6() -> None:
    pydirectinput.KEYBOARD_MAPPING.setdefault("num6", 0x4D)
    pydirectinput.keyDown("num6")
    time.sleep(0.08)
    pydirectinput.keyUp("num6")


def _press_random_reward_number() -> str:
    key = random.choice(("1", "2", "3", "4"))
    pydirectinput.keyDown(key)
    time.sleep(random.uniform(0.08, 0.16))
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


def _load_reward_template() -> tuple[np.ndarray, np.ndarray] | None:
    global _reward_template, _reward_template_unavailable

    if _reward_template is not None:
        return _reward_template
    if _reward_template_unavailable:
        return None

    template = cv2.imread(str(REWARD_TEMPLATE_PATH), cv2.IMREAD_UNCHANGED)
    if template is None:
        _reward_template_unavailable = True
        logger.warning("reward template unavailable: {}", REWARD_TEMPLATE_PATH)
        return None

    if template.ndim == 3 and template.shape[2] == 4:
        alpha = template[:, :, 3]
        ys, xs = np.where(alpha > 16)
        if len(xs) == 0 or len(ys) == 0:
            _reward_template_unavailable = True
            logger.warning("reward template has no visible pixels: {}", REWARD_TEMPLATE_PATH)
            return None
        template = template[ys.min() : ys.max() + 1, xs.min() : xs.max() + 1, :3]
        template = cv2.cvtColor(template, cv2.COLOR_BGR2RGB)
    else:
        template = cv2.cvtColor(template, cv2.COLOR_BGR2RGB)

    _reward_template = (template, cv2.cvtColor(template, cv2.COLOR_RGB2GRAY))
    return _reward_template


def _is_reward_template_like(frame_rgb: np.ndarray) -> bool:
    loaded_template = _load_reward_template()
    if loaded_template is None or frame_rgb.size == 0:
        return False

    template_rgb, template_gray = loaded_template
    frame_gray = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2GRAY)
    template_height, template_width = template_rgb.shape[:2]
    if template_height > frame_gray.shape[0] or template_width > frame_gray.shape[1]:
        return False

    result = cv2.matchTemplate(frame_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    _, max_score, _, max_loc = cv2.minMaxLoc(result)
    if not np.isfinite(max_score) or max_score < REWARD_TEMPLATE_THRESHOLD:
        return False

    x, y = max_loc
    matched_roi = frame_rgb[y : y + template_height, x : x + template_width]
    mean_diff = float(np.mean(np.abs(matched_roi.astype(np.float32) - template_rgb.astype(np.float32))))
    if mean_diff > REWARD_TEMPLATE_MEAN_DIFF_MAX:
        return False

    logger.debug("reward template matched: score={:.3f}, mean_diff={:.1f}", max_score, mean_diff)
    return True


def _yellow_text_stats(roi_rgb: np.ndarray) -> tuple[int, int, tuple[int, int, int, int] | None]:
    hsv = cv2.cvtColor(roi_rgb, cv2.COLOR_RGB2HSV)
    yellow_mask = cv2.inRange(hsv, np.array([15, 80, 110]), np.array([42, 255, 255]))
    yellow_mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_OPEN, np.ones((2, 2), dtype=np.uint8))
    return _text_stats_from_mask(yellow_mask)


def _text_stats_from_mask(mask: np.ndarray) -> tuple[int, int, tuple[int, int, int, int] | None]:
    count, _, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)

    text_pixels = int(cv2.countNonZero(mask))
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
        return text_pixels, text_like_components, None
    return text_pixels, text_like_components, (min(xs), min(ys), max(xs), max(ys))


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
    global _last_reward_miss_time

    now = time.time()
    if now - _last_reward_miss_time < REWARD_CHECK_INTERVAL_SECONDS:
        return False

    if _is_reward_template_like(frame_rgb):
        return True

    _last_reward_miss_time = now
    return False


def handle_reward_selection_prompt(frame_rgb: np.ndarray, screen_origin: ScreenOrigin = (0, 0)) -> bool:
    global _last_reward_press_time

    if not is_reward_selection_prompt(frame_rgb):
        return False

    now = time.time()
    if now - _last_reward_press_time < REWARD_COOLDOWN_SECONDS:
        return True

    _release_movement_keys()
    key = _press_random_reward_number()
    _last_reward_press_time = now
    logger.info("reward selection prompt detected, press reward key {}", key)
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
