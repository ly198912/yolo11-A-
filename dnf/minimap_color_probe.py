from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import cv2
import numpy as np
import pyautogui
import win32gui

from dnf.olaplug import OLAPlugServer


Rect = Tuple[int, int, int, int]
Point = Tuple[int, int]


@dataclass(frozen=True)
class ColorRule:
    name: str
    start_color: str
    end_color: str
    draw_color_bgr: Tuple[int, int, int]
    min_pixels: int = 3


# OLA color ranges are hex strings. If a rule misses, widen the range first.
COLOR_RULES: Tuple[ColorRule, ...] = (
    ColorRule("player_blue", "0095B8", "27D8F2", (255, 160, 0), min_pixels=3),
    ColorRule("query_green", "006000", "90FF70", (0, 255, 0), min_pixels=3),
    ColorRule("boss_red", "700000", "FF7070", (0, 0, 255), min_pixels=3),
    ColorRule("room_cyan", "004040", "80FFFF", (255, 255, 0), min_pixels=8),
)


def _get_client_rect_on_screen(hwnd: int) -> Rect:
    left_top = win32gui.ClientToScreen(hwnd, (0, 0))
    client_rect = win32gui.GetClientRect(hwnd)
    left = int(left_top[0])
    top = int(left_top[1])
    width = int(client_rect[2] - client_rect[0])
    height = int(client_rect[3] - client_rect[1])
    if width <= 0 or height <= 0:
        raise RuntimeError(f"invalid client size: hwnd={hwnd}, width={width}, height={height}")
    return left, top, width, height


def _default_minimap_region(width: int, height: int) -> Rect:
    # A generous top-right probe region. The point of this demo is to avoid tight crop tuning.
    x1 = max(0, width - 220)
    y1 = 35
    x2 = width
    y2 = min(height, 190)
    return x1, y1, x2, y2


def _parse_region(value: Optional[str], width: int, height: int) -> Rect:
    if not value:
        return _default_minimap_region(width, height)
    parts = [int(part.strip()) for part in value.replace(";", ",").split(",")]
    if len(parts) != 4:
        raise ValueError("--region must be x1,y1,x2,y2")
    x1, y1, x2, y2 = parts
    x1 = max(0, min(width - 1, x1))
    y1 = max(0, min(height - 1, y1))
    x2 = max(x1 + 1, min(width, x2))
    y2 = max(y1 + 1, min(height, y2))
    return x1, y1, x2, y2


def _rule_to_ola_json(rule: ColorRule) -> List[dict]:
    return [{"StartColor": rule.start_color, "EndColor": rule.end_color, "Type": 0}]


def _parse_hex_rgb(value: str) -> Tuple[int, int, int]:
    text = value.strip().lstrip("#")
    if len(text) != 6:
        raise ValueError(f"invalid hex color: {value!r}")
    return int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16)


def _hex_rgb(rgb: Tuple[int, int, int]) -> str:
    return "".join(f"{max(0, min(255, channel)):02X}" for channel in rgb)


def _range_from_samples(samples: str, padding: int) -> Tuple[str, str]:
    rgbs = [_parse_hex_rgb(item) for item in samples.replace(";", ",").split(",") if item.strip()]
    if not rgbs:
        raise ValueError("color samples cannot be empty")
    mins = tuple(min(rgb[index] for rgb in rgbs) - padding for index in range(3))
    maxs = tuple(max(rgb[index] for rgb in rgbs) + padding for index in range(3))
    return _hex_rgb(mins), _hex_rgb(maxs)


def _with_sample_override(rules: Iterable[ColorRule], rule_name: str, samples: Optional[str], padding: int) -> Tuple[ColorRule, ...]:
    if not samples:
        return tuple(rules)
    start_color, end_color = _range_from_samples(samples, padding)
    result = []
    for rule in rules:
        if rule.name == rule_name:
            result.append(
                ColorRule(
                    name=rule.name,
                    start_color=start_color,
                    end_color=end_color,
                    draw_color_bgr=rule.draw_color_bgr,
                    min_pixels=rule.min_pixels,
                )
            )
        else:
            result.append(rule)
    return tuple(result)


def _as_int(value: object, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _block_center(block: dict) -> Optional[Point]:
    if "x" in block and "y" in block:
        return _as_int(block["x"]), _as_int(block["y"])
    if "centerX" in block and "centerY" in block:
        return _as_int(block["centerX"]), _as_int(block["centerY"])
    if "cx" in block and "cy" in block:
        return _as_int(block["cx"]), _as_int(block["cy"])

    left = block.get("left", block.get("x1", block.get("l")))
    top = block.get("top", block.get("y1", block.get("t")))
    right = block.get("right", block.get("x2", block.get("r")))
    bottom = block.get("bottom", block.get("y2", block.get("b")))
    if left is not None and top is not None and right is not None and bottom is not None:
        return (_as_int(left) + _as_int(right)) // 2, (_as_int(top) + _as_int(bottom)) // 2

    width = block.get("width", block.get("w"))
    height = block.get("height", block.get("h"))
    if left is not None and top is not None and width is not None and height is not None:
        return _as_int(left) + _as_int(width) // 2, _as_int(top) + _as_int(height) // 2
    return None


def _find_points_with_ola(ola: OLAPlugServer, region: Rect, rule: ColorRule, max_blocks: int) -> Tuple[int, List[Point], List[dict]]:
    x1, y1, x2, y2 = region
    color_json = _rule_to_ola_json(rule)
    pixel_count = ola.GetColorNum(x1, y1, x2, y2, color_json)

    blocks = ola.FindColorBlockList(
        x1,
        y1,
        x2,
        y2,
        color_json,
        max_blocks,
        rule.min_pixels,
        rule.min_pixels,
        0,
    )
    points = [center for center in (_block_center(block) for block in blocks) if center is not None]

    if not points:
        found, px, py = ola.FindColor(x1, y1, x2, y2, rule.start_color, rule.end_color, 0)
        if found:
            points = [(px, py)]

    return pixel_count, points, blocks


def _screenshot_client_region(client_screen_rect: Rect, region: Rect) -> np.ndarray:
    screen_left, screen_top, _, _ = client_screen_rect
    x1, y1, x2, y2 = region
    image = pyautogui.screenshot(region=(screen_left + x1, screen_top + y1, x2 - x1, y2 - y1))
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


def _draw_probe(
    image: np.ndarray,
    region: Rect,
    detections: Dict[str, List[Point]],
    rules: Iterable[ColorRule],
) -> np.ndarray:
    x1, y1, _, _ = region
    output = image.copy()
    rule_by_name = {rule.name: rule for rule in rules}
    for name, points in detections.items():
        rule = rule_by_name[name]
        for point in points:
            local_x = point[0] - x1
            local_y = point[1] - y1
            if local_x < 0 or local_y < 0 or local_x >= output.shape[1] or local_y >= output.shape[0]:
                continue
            cv2.circle(output, (local_x, local_y), 5, rule.draw_color_bgr, 1)
            cv2.putText(output, name, (local_x + 6, local_y - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.35, rule.draw_color_bgr, 1, cv2.LINE_AA)
    return output


def _infer_direction(current: Optional[Point], target: Optional[Point]) -> Optional[str]:
    if current is None or target is None:
        return None
    dx = target[0] - current[0]
    dy = target[1] - current[1]
    margin = 8
    horizontal = None
    vertical = None
    if dx > margin:
        horizontal = "RIGHT"
    elif dx < -margin:
        horizontal = "LEFT"
    if dy > margin:
        vertical = "DOWN"
    elif dy < -margin:
        vertical = "UP"
    if horizontal and vertical:
        return f"{horizontal}_{vertical}"
    return horizontal or vertical


def main() -> None:
    parser = argparse.ArgumentParser(description="Standalone OLA color probe for DNF minimap icons.")
    parser.add_argument("--hwnd", type=lambda value: int(value, 0), help="Window handle. Default: foreground window.")
    parser.add_argument("--region", help="Client-coordinate probe region: x1,y1,x2,y2. Default: generous top-right area.")
    parser.add_argument("--max-blocks", type=int, default=20, help="Maximum color blocks per rule.")
    parser.add_argument("--once", action="store_true", help="Probe once and exit.")
    parser.add_argument("--interval", type=float, default=0.25, help="Probe interval when not using --once.")
    parser.add_argument("--out", default="runs/minimap_color_probe.png", help="Where to save the annotated preview image.")
    parser.add_argument("--player-samples", help="Comma-separated RGB hex samples for player_blue, e.g. 0ab9de,0ac4ce,18a9cc.")
    parser.add_argument("--sample-padding", type=int, default=20, help="RGB channel padding added around sample min/max.")
    args = parser.parse_args()

    hwnd = args.hwnd or win32gui.GetForegroundWindow()
    title = win32gui.GetWindowText(hwnd)
    client_rect = _get_client_rect_on_screen(hwnd)
    _, _, width, height = client_rect
    region = _parse_region(args.region, width, height)

    ola = OLAPlugServer()
    bind_result = ola.BindWindow(hwnd, "normal", "normal", "normal", 0)
    if bind_result != 1:
        raise RuntimeError(f"OLA BindWindow failed: hwnd={hwnd}, result={bind_result}")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rules = _with_sample_override(COLOR_RULES, "player_blue", args.player_samples, args.sample_padding)

    print(f"hwnd={hwnd}, title={title!r}, client={width}x{height}, region={region}")
    print("rules=" + json.dumps([rule.__dict__ for rule in rules], ensure_ascii=False))
    print("press Ctrl+C to stop")

    try:
        while True:
            detections: Dict[str, List[Point]] = {}
            report = []
            for rule in rules:
                pixel_count, points, blocks = _find_points_with_ola(ola, region, rule, args.max_blocks)
                detections[rule.name] = points
                report.append(
                    {
                        "name": rule.name,
                        "pixels": pixel_count,
                        "points": points,
                        "raw_blocks": blocks[:3],
                    }
                )

            current = detections["player_blue"][0] if detections["player_blue"] else None
            query = detections["query_green"][0] if detections["query_green"] else None
            boss = detections["boss_red"][0] if detections["boss_red"] else None
            direction_to_query = _infer_direction(current, query)
            direction_to_boss = _infer_direction(current, boss)

            preview = _screenshot_client_region(client_rect, region)
            preview = _draw_probe(preview, region, detections, rules)
            cv2.imwrite(str(out_path), preview)
            cv2.imshow("minimap-color-probe", cv2.resize(preview, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST))

            print(json.dumps(report, ensure_ascii=False))
            print(f"current={current}, query={query}, boss={boss}, query_dir={direction_to_query}, boss_dir={direction_to_boss}, preview={out_path}")

            if args.once:
                cv2.waitKey(1)
                break
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            time.sleep(args.interval)
    finally:
        ola.UnBindWindow()
        ola.ReleaseObj()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
