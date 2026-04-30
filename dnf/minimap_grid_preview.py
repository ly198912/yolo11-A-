from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np
import pyautogui
import win32gui

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dnf.minimap_nav import MiniMapNavigator


MAP_NAME = "haibolun"
WINDOW_TITLE_KEYWORD = "地下城与勇士"
WINDOW_CLASS_NAMES = {"地下城与勇士", "地下城与勇士创新世纪"}
PREVIEW_WINDOW_NAME = "dnf-minimap-grid-preview"
ZOOM_WINDOW_NAME = "dnf-minimap-zoom"

Rect = Tuple[int, int, int, int]


def _clamp_rect(rect: Rect, width: int, height: int) -> Rect:
    x1, y1, x2, y2 = rect
    x1 = max(0, min(width - 1, x1))
    y1 = max(0, min(height - 1, y1))
    x2 = max(x1 + 1, min(width, x2))
    y2 = max(y1 + 1, min(height, y2))
    return x1, y1, x2, y2


def _find_dnf_window() -> Optional[int]:
    candidates = []

    def _enum_windows(hwnd: int, _: object) -> None:
        if not win32gui.IsWindowVisible(hwnd):
            return

        title = win32gui.GetWindowText(hwnd).strip()
        class_name = win32gui.GetClassName(hwnd).strip()
        title_match = WINDOW_TITLE_KEYWORD in title
        class_match = class_name in WINDOW_CLASS_NAMES or WINDOW_TITLE_KEYWORD in class_name
        if not title_match and not class_match:
            return

        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        area = max(0, right - left) * max(0, bottom - top)
        candidates.append((area, hwnd))

    win32gui.EnumWindows(_enum_windows, None)
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]


def _capture_dnf_or_screen(hwnd: Optional[int]) -> np.ndarray:
    if hwnd:
        left_top = win32gui.ClientToScreen(hwnd, (0, 0))
        client_rect = win32gui.GetClientRect(hwnd)
        left = int(left_top[0])
        top = int(left_top[1])
        width = int(client_rect[2] - client_rect[0])
        height = int(client_rect[3] - client_rect[1])
        if width > 0 and height > 0:
            image = pyautogui.screenshot(region=(left, top, width, height))
            return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    image = pyautogui.screenshot(region=(0, 0, 800, 600))
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


def _draw_grid(frame_bgr: np.ndarray, navigator: MiniMapNavigator) -> np.ndarray:
    output = frame_bgr.copy()
    height, width = output.shape[:2]
    room_info = navigator.detect_room_markers(frame_bgr)
    crop_rect, room_rect = navigator._scaled_crop_and_room_rect(frame_bgr)
    cx1, cy1, cx2, cy2 = _clamp_rect(crop_rect, width, height)

    if room_rect is None:
        room_rect = crop_rect
    rx1, ry1, rx2, ry2 = _clamp_rect(room_rect, width, height)

    cv2.rectangle(output, (cx1, cy1), (cx2 - 1, cy2 - 1), (0, 255, 0), 1)
    cv2.rectangle(output, (rx1, ry1), (rx2 - 1, ry2 - 1), (255, 255, 255), 1)

    for col in range(1, navigator.spec.cols):
        x = int(round(rx1 + (rx2 - rx1) * col / navigator.spec.cols))
        cv2.line(output, (x, ry1), (x, ry2 - 1), (255, 255, 255), 1)
    for row in range(1, navigator.spec.rows):
        y = int(round(ry1 + (ry2 - ry1) * row / navigator.spec.rows))
        cv2.line(output, (rx1, y), (rx2 - 1, y), (255, 255, 255), 1)

    marker_styles = {
        "current_marker": ((255, 0, 0), "P"),
        "query_marker": ((0, 255, 255), "Q"),
        "boss_marker": ((0, 0, 255), "B"),
        "elite_marker": ((255, 0, 255), "E"),
        "down_marker": ((0, 255, 0), "D"),
    }
    for key, (color, label) in marker_styles.items():
        marker = room_info.get(key)
        if marker is None:
            continue
        x = int(round(cx1 + marker[0]))
        y = int(round(cy1 + marker[1]))
        cv2.circle(output, (x, y), 4, color, -1)
        cv2.putText(output, label, (x + 5, y - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1, cv2.LINE_AA)

    text = (
        f"map={navigator.map_name} current={room_info['current_room']} "
        f"query={room_info['query_room']} boss={room_info['boss_room']}"
    )
    cv2.putText(output, text, (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    return output


def main() -> None:
    map_name = os.getenv("DNF_PREVIEW_MAP_NAME", MAP_NAME)
    navigator = MiniMapNavigator(map_name)
    hwnd = _find_dnf_window()

    while True:
        frame_bgr = _capture_dnf_or_screen(hwnd)
        preview = _draw_grid(frame_bgr, navigator)
        minimap = navigator.draw_debug_minimap(frame_bgr)

        cv2.imshow(PREVIEW_WINDOW_NAME, preview)
        cv2.imshow(ZOOM_WINDOW_NAME, cv2.resize(minimap, (420, 240), interpolation=cv2.INTER_NEAREST))

        key = cv2.waitKey(80) & 0xFF
        if key in (ord("q"), 27):
            break
        time.sleep(0.02)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
