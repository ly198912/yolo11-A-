from __future__ import annotations

import time
import random
from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np
from dnf import input_backend
from loguru import logger


RETRY_COOLDOWN_SECONDS = 3.0
REWARD_SELECT_COOLDOWN_SECONDS = 2.0
TRY_AGAIN_TEMPLATE_THRESHOLD = 0.84
REWARD_TEMPLATE_THRESHOLD = 0.80
TRY_AGAIN_TEMPLATE_PATH = Path(__file__).resolve().parent / "res" / "Try Again.png"
REWARD_TEMPLATE_PATH = Path(__file__).resolve().parent / "res" / "jiangli.png"
_last_retry_press_time = 0.0
_last_reward_select_press_time = 0.0
_try_again_template_gray: Optional[np.ndarray] = None
_reward_template_gray: Optional[np.ndarray] = None


def _press_key(key: str) -> None:
    input_backend.press(key)


def _press_numpad_6() -> None:
    _press_key("num6")


def _release_movement_keys() -> None:
    for key in ("up", "down", "left", "right"):
        try:
            input_backend.keyUp(key)
        except Exception as exc:
            logger.warning("failed to release movement key {}: {}", key, exc)


def _retry_prompt_roi(frame_rgb: np.ndarray) -> np.ndarray:
    height, width = frame_rgb.shape[:2]
    x1 = 0
    x2 = min(width, int(width * 0.24))
    y1 = max(0, int(height * 0.78))
    y2 = min(height, int(height * 0.895))
    return frame_rgb[y1:y2, x1:x2]


def _load_gray_template(path: Path, description: str) -> Optional[np.ndarray]:
    if not path.exists():
        logger.warning("{} template not found: {}", description, path)
        return None

    data = np.fromfile(str(path), dtype=np.uint8)
    template = cv2.imdecode(data, cv2.IMREAD_GRAYSCALE)
    if template is None or template.size == 0:
        logger.warning("failed to load {} template: {}", description, path)
        return None

    return template


def _load_try_again_template() -> Optional[np.ndarray]:
    global _try_again_template_gray

    if _try_again_template_gray is not None:
        return _try_again_template_gray

    template = _load_gray_template(TRY_AGAIN_TEMPLATE_PATH, "try-again")
    if template is None:
        return None
    _try_again_template_gray = template
    return _try_again_template_gray


def _load_reward_template() -> Optional[np.ndarray]:
    global _reward_template_gray

    if _reward_template_gray is not None:
        return _reward_template_gray

    template = _load_gray_template(REWARD_TEMPLATE_PATH, "reward")
    if template is None:
        return None
    _reward_template_gray = template
    return _reward_template_gray


def _template_score(frame_rgb: np.ndarray, template: Optional[np.ndarray]) -> float:
    if template is None or frame_rgb is None or frame_rgb.size == 0:
        return 0.0
    if frame_rgb.shape[0] < template.shape[0] or frame_rgb.shape[1] < template.shape[1]:
        return 0.0

    frame_gray = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2GRAY)
    result = cv2.matchTemplate(frame_gray, template, cv2.TM_CCOEFF_NORMED)
    return float(cv2.minMaxLoc(result)[1])


def _try_again_template_score(frame_rgb: np.ndarray) -> float:
    return _template_score(frame_rgb, _load_try_again_template())


def _reward_template_score(frame_rgb: np.ndarray) -> float:
    return _template_score(frame_rgb, _load_reward_template())


def is_try_again_template_prompt(frame_rgb: np.ndarray) -> bool:
    return _try_again_template_score(frame_rgb) >= TRY_AGAIN_TEMPLATE_THRESHOLD


def is_reward_template_prompt(frame_rgb: np.ndarray) -> bool:
    return _reward_template_score(frame_rgb) >= REWARD_TEMPLATE_THRESHOLD


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
    if is_try_again_template_prompt(frame_rgb):
        return True

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
    time.sleep(random.uniform(0.5, 1.0))
    _press_numpad_6()
    _last_retry_press_time = now
    logger.info("retry challenge prompt detected, press Numpad_6")
    return True


def _dark_ratio(roi_rgb: np.ndarray) -> float:
    if roi_rgb.size == 0:
        return 0.0
    red = roi_rgb[:, :, 0]
    green = roi_rgb[:, :, 1]
    blue = roi_rgb[:, :, 2]
    return float(np.mean((red < 65) & (green < 65) & (blue < 65)))


def _white_yellow_mask(roi_rgb: np.ndarray) -> np.ndarray:
    red = roi_rgb[:, :, 0]
    green = roi_rgb[:, :, 1]
    blue = roi_rgb[:, :, 2]
    white = (red > 150) & (green > 150) & (blue > 150)
    yellow = (
        (red > 150)
        & (green > 100)
        & (blue < 120)
        & ((red.astype(int) - blue.astype(int)) > 60)
    )
    return ((white | yellow).astype(np.uint8)) * 255


def _gold_pixels(roi_rgb: np.ndarray) -> int:
    if roi_rgb.size == 0:
        return 0
    red = roi_rgb[:, :, 0]
    green = roi_rgb[:, :, 1]
    blue = roi_rgb[:, :, 2]
    gold = (
        (red > 150)
        & (green > 100)
        & (blue < 120)
        & ((red.astype(int) - blue.astype(int)) > 60)
    )
    return int(np.count_nonzero(gold))


def _bright_text_line_count(roi_rgb: np.ndarray) -> int:
    if roi_rgb.size == 0:
        return 0

    mask = _white_yellow_mask(roi_rgb)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((2, 1), dtype=np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 12), dtype=np.uint8))
    count, _, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)

    line_count = 0
    for index in range(1, count):
        area = int(stats[index, cv2.CC_STAT_AREA])
        width = int(stats[index, cv2.CC_STAT_WIDTH])
        height = int(stats[index, cv2.CC_STAT_HEIGHT])
        if 35 <= width <= 260 and 8 <= height <= 26 and 80 <= area <= 2500:
            line_count += 1
    return line_count


def is_end_reward_screen(frame_rgb: np.ndarray) -> bool:
    if frame_rgb is None or frame_rgb.size == 0:
        return False

    height, width = frame_rgb.shape[:2]
    continue_menu = frame_rgb[int(height * 0.03):int(height * 0.20), int(width * 0.60):int(width * 0.99)]
    score_panel = frame_rgb[int(height * 0.18):int(height * 0.78), int(width * 0.58):int(width * 0.99)]
    if continue_menu.size == 0 or score_panel.size == 0:
        return False

    return (
        _bright_text_line_count(continue_menu) >= 2
        and _dark_ratio(score_panel) >= 0.45
        and _gold_pixels(score_panel) >= 1200
    )


def handle_end_reward_screen(frame_rgb: np.ndarray) -> bool:
    if is_retry_challenge_prompt(frame_rgb):
        return False

    if not is_end_reward_screen(frame_rgb):
        return False

    _release_movement_keys()
    logger.info("end reward/continue screen detected, hold position")
    return True


def is_reward_selection_screen(frame_rgb: np.ndarray) -> bool:
    if frame_rgb is None or frame_rgb.size == 0:
        return False
    if is_reward_template_prompt(frame_rgb):
        return True

    height, width = frame_rgb.shape[:2]
    top_center = frame_rgb[int(height * 0.02):int(height * 0.12), int(width * 0.30):int(width * 0.70)]
    left_panel = frame_rgb[int(height * 0.08):int(height * 0.50), int(width * 0.02):int(width * 0.28)]
    if top_center.size == 0 or left_panel.size == 0:
        return False

    top_gold = _gold_pixels(top_center)
    left_bright = int(np.count_nonzero(_white_yellow_mask(left_panel)))
    return (
        _dark_ratio(frame_rgb) >= 0.50
        and _dark_ratio(top_center) >= 0.75
        and top_gold >= 180
        and _dark_ratio(left_panel) >= 0.75
        and left_bright >= 250
    )


def handle_reward_selection_screen(frame_rgb: np.ndarray) -> bool:
    global _last_reward_select_press_time

    if not is_reward_selection_screen(frame_rgb):
        return False

    now = time.time()
    if now - _last_reward_select_press_time < REWARD_SELECT_COOLDOWN_SECONDS:
        return True

    _release_movement_keys()
    time.sleep(random.uniform(1.0, 2.0))
    reward_key = str(random.randint(1, 4))
    _press_key(reward_key)
    _last_reward_select_press_time = now
    logger.info("reward selection screen detected, press {}", reward_key)
    return True
