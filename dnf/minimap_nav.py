from __future__ import annotations

import os
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import cv2
import numpy as np
from loguru import logger

from dnf.door_strategy import DoorCandidate, choose_best_door
from dnf.map_specs import MAP_SPECS, MapSpec, Rect
from dnf.minimap_astar import next_direction


Point = Tuple[int, int]
ScoredMatch = Tuple[float, float, float, str]
VariantKey = Tuple[str, bool, Tuple[float, ...]]


QUERY_TEMPLATE_FILES = {
    "query": "map_query.png",

}

MARKER_THRESHOLDS = {
    "hero": 0.58,
    "boss": 0.68,
    "query": 0.70,
    "elite": 0.68,
    "special": 0.64,
    "down": 0.58,
}

ROBUST_TEMPLATE_SCALES = (0.88, 0.94, 1.0, 1.06, 1.12)
AUTO_MAP_SWITCH_MARGIN = 0.08
AUTO_MAP_MIN_SCORE = 0.55
AUTO_MAP_CONFIRM_FRAMES = 2
LAYOUT_TEMPLATE_THRESHOLD = float(os.getenv("DNF_LAYOUT_TEMPLATE_THRESHOLD", "0.72"))
QUERY_COLOR_FALLBACK_ENABLED = os.getenv("DNF_QUERY_COLOR_FALLBACK", "0") == "1"


@dataclass
class RouteSnapshot:
    current_room: Optional[Point]
    boss_room: Optional[Point]
    query_room: Optional[Point]
    elite_room: Optional[Point]
    down_room: Optional[Point]
    target_kind: Optional[str]
    target_room: Optional[Point]
    next_room_direction: Optional[str]
    selected_door_center: Optional[Tuple[float, float]]
    debug_scores: Optional[Dict[str, float]] = None


def _parse_rect_env(name: str) -> Optional[Rect]:
    value = os.getenv(name)
    if not value:
        return None
    parts = [part.strip() for part in value.replace(";", ",").split(",")]
    if len(parts) != 4:
        raise ValueError(f"{name} must be x1,y1,x2,y2")
    x1, y1, x2, y2 = (int(part) for part in parts)
    if x2 <= x1 or y2 <= y1:
        raise ValueError(f"{name} must satisfy x2 > x1 and y2 > y1")
    return x1, y1, x2, y2


def _scale_rect(rect: Rect, scale_x: float, scale_y: float) -> Rect:
    x1, y1, x2, y2 = rect
    return (
        int(round(x1 * scale_x)),
        int(round(y1 * scale_y)),
        int(round(x2 * scale_x)),
        int(round(y2 * scale_y)),
    )


def _clamp_rect(rect: Rect, width: int, height: int) -> Rect:
    x1, y1, x2, y2 = rect
    x1 = max(0, min(width - 1, x1))
    y1 = max(0, min(height - 1, y1))
    x2 = max(x1 + 1, min(width, x2))
    y2 = max(y1 + 1, min(height, y2))
    return x1, y1, x2, y2


class MiniMapNavigator:
    def __init__(self, map_name: str = "auto", assets_dir: Optional[Path] = None, threshold: float = 0.7):
        self.auto_map = map_name == "auto"
        if self.auto_map or map_name not in MAP_SPECS:
            map_name = "universal"
        self.threshold = threshold
        self._set_active_map(map_name)
        self.assets_dir = assets_dir or (Path(__file__).resolve().parent / "res")
        self.layout_templates = self._load_layout_templates()
        self.templates = {
            "hero": self._load_template("map_hero.png"),
            "boss": self._load_template("map_query2.png"),
            "elite": self._load_template("map_elite.png"),
            "special": self._load_template("map_special_room.png"),
        }
        for name, filename in QUERY_TEMPLATE_FILES.items():
            query_template = self._load_template_optional(filename)
            if query_template is not None:
                self.templates[name] = query_template
        down_template = self._load_template_optional("map_down.png")
        if down_template is not None:
            self.templates["down"] = down_template
        self.last_direction: Optional[str] = None
        self._variant_cache: Dict[VariantKey, List[np.ndarray]] = {}
        self._debug_scores_cache: Dict[str, float] = {}
        self._debug_scores_frame = 0
        self._debug_scores_interval = 5
        self._last_room_rect: Optional[Rect] = None
        self._auto_scores_cache: Dict[str, float] = {}
        self._auto_candidate_map: Optional[str] = None
        self._auto_candidate_count = 0

    def _set_active_map(self, map_name: str) -> None:
        self.map_name = map_name
        self.spec = MAP_SPECS[map_name]
        env_prefix = f"DNF_MINIMAP_{self.map_name.upper()}"
        self.crop_rect_1067 = (
            _parse_rect_env(f"{env_prefix}_CROP_1067")
            or _parse_rect_env("DNF_MINIMAP_CROP_1067")
            or self.spec.crop_rect_1067
        )
        self.crop_rect_800 = (
            _parse_rect_env(f"{env_prefix}_CROP_800")
            or _parse_rect_env("DNF_MINIMAP_CROP_800")
            or self.spec.crop_rect_800
        )
        self.room_rect_1067 = (
            _parse_rect_env(f"{env_prefix}_ROOM_1067")
            or _parse_rect_env("DNF_MINIMAP_ROOM_1067")
            or self.spec.room_rect_1067
        )
        self.room_rect_800 = (
            _parse_rect_env(f"{env_prefix}_ROOM_800")
            or _parse_rect_env("DNF_MINIMAP_ROOM_800")
            or self.spec.room_rect_800
        )

    def _uses_universal_map(self) -> bool:
        return getattr(self, "map_name", "") == "universal"

    def _load_template(self, filename: str) -> np.ndarray:
        path = self.assets_dir / filename
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image is None:
            raise FileNotFoundError(f"template not found: {path}")
        return image

    def _load_template_optional(self, filename: str) -> Optional[np.ndarray]:
        path = self.assets_dir / filename
        if not path.exists():
            return None
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        return image

    def _load_layout_templates(self) -> Dict[str, np.ndarray]:
        return {}

    def _scaled_rects_for_spec(self, frame: np.ndarray, spec: MapSpec) -> Tuple[Rect, Optional[Rect]]:
        frame_h, frame_w = frame.shape[:2]
        if spec.crop_rect_800 is not None and frame_w <= 900:
            scale_x = frame_w / 800.0
            scale_y = frame_h / 600.0
            crop_rect = _scale_rect(spec.crop_rect_800, scale_x, scale_y)
            room_rect = _scale_rect(spec.room_rect_800, scale_x, scale_y) if spec.room_rect_800 else None
            return crop_rect, room_rect

        scale_x = frame_w / 1067.0
        scale_y = frame_h / 600.0
        crop_rect = _scale_rect(spec.crop_rect_1067, scale_x, scale_y)
        room_rect = _scale_rect(spec.room_rect_1067, scale_x, scale_y) if spec.room_rect_1067 else None
        return crop_rect, room_rect

    def _template_score(self, image: np.ndarray, template: np.ndarray) -> float:
        image_h, image_w = image.shape[:2]
        template_h, template_w = template.shape[:2]
        if template_h > image_h or template_w > image_w:
            return 0.0
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(image_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)
        return float(max_val)

    def _score_layout_templates(self, frame: np.ndarray) -> Dict[str, float]:
        if not self.layout_templates:
            return {}

        frame_h, frame_w = frame.shape[:2]
        search_region = frame[:, max(0, int(frame_w * 0.45)):frame_w]
        scores: Dict[str, float] = {}
        for map_name, template in self.layout_templates.items():
            if template.shape[0] > search_region.shape[0] or template.shape[1] > search_region.shape[1]:
                scores[map_name] = 0.0
                continue
            scores[map_name] = self._template_score(search_region, template)
        return scores

    def _score_map_spec(self, frame: np.ndarray, spec: MapSpec) -> float:
        frame_h, frame_w = frame.shape[:2]
        x1, y1, x2, y2 = _clamp_rect(self._scaled_rects_for_spec(frame, spec)[0], frame_w, frame_h)
        minimap = frame[y1:y2, x1:x2]
        if minimap.size == 0:
            return 0.0

        scores = []
        for name in ("hero", "boss", "query", "query1", "elite", "down"):
            template = self.templates.get(name)
            if template is not None:
                scores.append(self._template_score(minimap, template))
        if not scores:
            return 0.0
        scores.sort(reverse=True)
        return float(sum(scores[:3]) / min(3, len(scores)))

    def _select_auto_map(self, frame: np.ndarray) -> None:
        if not self.auto_map or self._uses_universal_map():
            return

        layout_scores = self._score_layout_templates(frame)
        if layout_scores:
            best_layout_map = max(layout_scores, key=layout_scores.get)
            best_layout_score = layout_scores[best_layout_map]
            self._auto_scores_cache = layout_scores
            if best_layout_score >= LAYOUT_TEMPLATE_THRESHOLD:
                if best_layout_map == self.map_name:
                    self._auto_candidate_map = None
                    self._auto_candidate_count = 0
                    return
                if best_layout_map == self._auto_candidate_map:
                    self._auto_candidate_count += 1
                else:
                    self._auto_candidate_map = best_layout_map
                    self._auto_candidate_count = 1

                if self._auto_candidate_count >= AUTO_MAP_CONFIRM_FRAMES:
                    logger.info("auto minimap layout switched: {} -> {}, scores={}", self.map_name, best_layout_map, layout_scores)
                    self._set_active_map(best_layout_map)
                    self._auto_candidate_map = None
                    self._auto_candidate_count = 0
                return

        scores = {name: self._score_map_spec(frame, spec) for name, spec in MAP_SPECS.items()}
        self._auto_scores_cache = scores
        best_map = max(scores, key=scores.get)
        current_score = scores.get(self.map_name, 0.0)
        best_score = scores[best_map]

        if best_score < AUTO_MAP_MIN_SCORE or best_map == self.map_name:
            self._auto_candidate_map = None
            self._auto_candidate_count = 0
            return

        if best_score < current_score + AUTO_MAP_SWITCH_MARGIN:
            self._auto_candidate_map = None
            self._auto_candidate_count = 0
            return

        if best_map == self._auto_candidate_map:
            self._auto_candidate_count += 1
        else:
            self._auto_candidate_map = best_map
            self._auto_candidate_count = 1

        if self._auto_candidate_count >= AUTO_MAP_CONFIRM_FRAMES:
            logger.info("auto minimap switched: {} -> {}, scores={}", self.map_name, best_map, scores)
            self._set_active_map(best_map)
            self._auto_candidate_map = None
            self._auto_candidate_count = 0

    def _scaled_crop_and_room_rect(self, frame: np.ndarray) -> Tuple[Rect, Optional[Rect]]:
        frame_h, frame_w = frame.shape[:2]
        if self.crop_rect_800 is not None and frame_w <= 900:
            x1, y1, x2, y2 = self.crop_rect_800
            scale_x = frame_w / 800.0
            scale_y = frame_h / 600.0
            crop_rect = _scale_rect((x1, y1, x2, y2), scale_x, scale_y)
            room_rect = _scale_rect(self.room_rect_800, scale_x, scale_y) if self.room_rect_800 else None
            return crop_rect, room_rect

        x1, y1, x2, y2 = self.crop_rect_1067
        scale_x = frame_w / 1067.0
        scale_y = frame_h / 600.0
        crop_rect = _scale_rect((x1, y1, x2, y2), scale_x, scale_y)
        room_rect = _scale_rect(self.room_rect_1067, scale_x, scale_y) if self.room_rect_1067 else None
        return crop_rect, room_rect

    def _scaled_crop_rect(self, frame: np.ndarray) -> Rect:
        crop_rect, _ = self._scaled_crop_and_room_rect(frame)
        return crop_rect

    def extract_minimap(self, frame: np.ndarray) -> np.ndarray:
        self._select_auto_map(frame)
        crop_rect, room_rect = self._scaled_crop_and_room_rect(frame)
        frame_h, frame_w = frame.shape[:2]
        x1, y1, x2, y2 = _clamp_rect(crop_rect, frame_w, frame_h)
        minimap = frame[y1:y2, x1:x2]
        if room_rect is not None:
            rx1, ry1, rx2, ry2 = room_rect
            self._last_room_rect = _clamp_rect((rx1 - x1, ry1 - y1, rx2 - x1, ry2 - y1), minimap.shape[1], minimap.shape[0])
        else:
            self._last_room_rect = (0, 0, minimap.shape[1], minimap.shape[0])
        return minimap

    def _match_template(self, image: np.ndarray, template: np.ndarray, threshold: Optional[float] = None) -> List[Tuple[float, float]]:
        threshold = self.threshold if threshold is None else threshold
        return [(x, y) for _, x, y, _ in self._match_template_scored(image, template, threshold=threshold)]

    def _match_template_scored(
        self,
        image: np.ndarray,
        template: np.ndarray,
        threshold: Optional[float] = None,
        scales: Sequence[float] = (1.0,),
        name: str = "",
        use_color: bool = False,
    ) -> List[ScoredMatch]:
        threshold = self.threshold if threshold is None else threshold
        if use_color:
            match_image = image
            match_template = template
        else:
            match_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            match_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        scored_matches: List[ScoredMatch] = []
        scaled_templates = self._get_scaled_templates(name, match_template, scales, use_color)
        for scaled_template in scaled_templates:
            h, w = scaled_template.shape[:2]
            if h <= 1 or w <= 1 or h > match_image.shape[0] or w > match_image.shape[1]:
                continue
            result = cv2.matchTemplate(match_image, scaled_template, cv2.TM_CCOEFF_NORMED)
            ys, xs = np.where(result >= threshold)
            for y, x in zip(ys, xs):
                scored_matches.append((float(result[y, x]), x + w / 2.0, y + h / 2.0, name))
        scored_matches.sort(key=lambda item: item[0], reverse=True)
        return scored_matches

    def _get_scaled_templates(
        self,
        name: str,
        template: np.ndarray,
        scales: Sequence[float],
        use_color: bool,
    ) -> List[np.ndarray]:
        scale_key = tuple(scales)
        if not name:
            return [
                template if scale == 1.0 else cv2.resize(template, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
                for scale in scale_key
            ]

        key = (name, use_color, scale_key)
        cached = self._variant_cache.get(key)
        if cached is not None:
            return cached

        variants = [
            template if scale == 1.0 else cv2.resize(template, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
            for scale in scale_key
        ]
        self._variant_cache[key] = variants
        return variants

    def _match_template_debug(self, image: np.ndarray, template: np.ndarray) -> Tuple[List[Tuple[float, float]], float]:
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(image_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)
        ys, xs = np.where(result >= self.threshold)
        scored_matches: List[Tuple[float, float, float]] = []
        h, w = template_gray.shape[:2]
        for y, x in zip(ys, xs):
            scored_matches.append((float(result[y, x]), x + w / 2.0, y + h / 2.0))
        scored_matches.sort(key=lambda item: item[0], reverse=True)
        return [(x, y) for _, x, y in scored_matches], float(max_val)

    def _match_marker(self, minimap: np.ndarray, names: Sequence[str], threshold_key: str) -> List[ScoredMatch]:
        threshold = MARKER_THRESHOLDS.get(threshold_key, self.threshold)
        scales = ROBUST_TEMPLATE_SCALES if threshold_key in {"hero", "query"} else (1.0,)
        use_color = threshold_key == "query"
        matches: List[ScoredMatch] = []
        for name in names:
            template = self.templates.get(name)
            if template is None:
                continue
            matches.extend(
                self._match_template_scored(
                    minimap,
                    template,
                    threshold=threshold,
                    scales=scales,
                    name=name,
                    use_color=use_color,
                )
            )
        matches.sort(key=lambda item: item[0], reverse=True)
        return matches

    def _first_room_from_matches(
        self,
        matches: Sequence[ScoredMatch],
        minimap: np.ndarray,
        excluded_rooms: Sequence[Optional[Point]] = (),
    ) -> Optional[Point]:
        room, _ = self._first_room_and_center_from_matches(matches, minimap, excluded_rooms)
        return room

    def _first_room_and_center_from_matches(
        self,
        matches: Sequence[ScoredMatch],
        minimap: np.ndarray,
        excluded_rooms: Sequence[Optional[Point]] = (),
    ) -> Tuple[Optional[Point], Optional[Tuple[float, float]]]:
        excluded = {room for room in excluded_rooms if room is not None}
        for _, x, y, _ in matches:
            room = self.compute_room_id(x, y, minimap)
            if room not in excluded:
                return room, (x, y)
        return None, None

    def _first_marker_room_and_center_from_matches(
        self,
        matches: Sequence[ScoredMatch],
        minimap: np.ndarray,
        excluded_markers: Sequence[Optional[Tuple[float, float]]] = (),
        min_distance: float = 8.0,
    ) -> Tuple[Optional[Point], Optional[Tuple[float, float]]]:
        excluded = [marker for marker in excluded_markers if marker is not None]
        min_distance_sq = min_distance * min_distance
        for _, x, y, _ in matches:
            if any((x - ex) * (x - ex) + (y - ey) * (y - ey) < min_distance_sq for ex, ey in excluded):
                continue
            return self.compute_room_id(x, y, minimap), (x, y)
        return None, None

    def _match_query_by_color(self, minimap: np.ndarray, current_room: Optional[Point]) -> List[ScoredMatch]:
        if current_room is None:
            return []

        hsv = cv2.cvtColor(minimap, cv2.COLOR_BGR2HSV)
        yellow_mask = cv2.inRange(hsv, np.array([18, 70, 70]), np.array([45, 255, 255]))
        yellow_mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_OPEN, np.ones((2, 2), dtype=np.uint8))
        count, labels, stats, centroids = cv2.connectedComponentsWithStats(yellow_mask, connectivity=8)

        matches: List[ScoredMatch] = []
        for index in range(1, count):
            area = int(stats[index, cv2.CC_STAT_AREA])
            width = int(stats[index, cv2.CC_STAT_WIDTH])
            height = int(stats[index, cv2.CC_STAT_HEIGHT])
            if area < 3 or area > 80 or width > 16 or height > 16:
                continue
            x, y = centroids[index]
            room = self.compute_room_id(float(x), float(y), minimap)
            room_distance = abs(room[0] - current_room[0]) + abs(room[1] - current_room[1])
            if room_distance > 2:
                continue
            score = min(0.62, 0.48 + area / 120.0)
            matches.append((score, float(x), float(y), "query_color"))
        matches.sort(key=lambda item: item[0], reverse=True)
        return matches

    def compute_room_id(self, x: float, y: float, minimap_image: np.ndarray) -> Point:
        height, width = minimap_image.shape[:2]
        rx1, ry1, rx2, ry2 = self._last_room_rect or (0, 0, width, height)
        rx1, ry1, rx2, ry2 = _clamp_rect((rx1, ry1, rx2, ry2), width, height)
        room_w = max(1, rx2 - rx1)
        room_h = max(1, ry2 - ry1)
        cell_w = room_w / self.spec.cols
        cell_h = room_h / self.spec.rows
        local_x = max(0.0, min(float(room_w - 1), float(x) - rx1))
        local_y = max(0.0, min(float(room_h - 1), float(y) - ry1))
        row = int(local_y // cell_h)
        col = int(local_x // cell_w)
        row = max(0, min(self.spec.rows - 1, row))
        col = max(0, min(self.spec.cols - 1, col))
        return row, col

    def draw_debug_minimap(self, frame: np.ndarray) -> np.ndarray:
        info = self.detect_room_markers(frame)
        minimap = self.extract_minimap(frame).copy()
        height, width = minimap.shape[:2]
        rx1, ry1, rx2, ry2 = self._last_room_rect or (0, 0, width, height)
        rx1, ry1, rx2, ry2 = _clamp_rect((rx1, ry1, rx2, ry2), width, height)

        cv2.rectangle(minimap, (rx1, ry1), (rx2 - 1, ry2 - 1), (255, 255, 255), 1)
        for col in range(1, self.spec.cols):
            x = int(round(rx1 + (rx2 - rx1) * col / self.spec.cols))
            cv2.line(minimap, (x, ry1), (x, ry2 - 1), (180, 180, 180), 1)
        for row in range(1, self.spec.rows):
            y = int(round(ry1 + (ry2 - ry1) * row / self.spec.rows))
            cv2.line(minimap, (rx1, y), (rx2 - 1, y), (180, 180, 180), 1)

        marker_styles = {
            "current_marker": ((255, 0, 0), "P"),
            "boss_marker": ((0, 0, 255), "B"),
            "query_marker": ((0, 255, 255), "Q"),
            "elite_marker": ((255, 0, 255), "E"),
            "down_marker": ((0, 255, 0), "D"),
        }
        for key, (color, label) in marker_styles.items():
            marker = info.get(key)
            if marker is None:
                continue
            x, y = int(round(marker[0])), int(round(marker[1]))
            cv2.circle(minimap, (x, y), 4, color, -1)
            cv2.putText(minimap, label, (x + 5, y - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1, cv2.LINE_AA)
        return minimap

    def detect_room_markers(self, frame: np.ndarray) -> Dict[str, Optional[Point]]:
        minimap = self.extract_minimap(frame)
        current_room = None
        boss_room = None
        query_room = None
        elite_room = None
        down_room = None
        current_marker = None
        boss_marker = None
        query_marker = None
        elite_marker = None
        down_marker = None

        hero_matches = self._match_marker(minimap, ["hero"], "hero")
        if hero_matches:
            _, x, y, _ = hero_matches[0]
            current_marker = (x, y)
            current_room = self.compute_room_id(x, y, minimap)

        elite_matches = self._match_template(minimap, self.templates["elite"], threshold=MARKER_THRESHOLDS["elite"])
        if elite_matches:
            elite_marker = elite_matches[0]
            elite_room = self.compute_room_id(*elite_marker, minimap)

        special_matches = self._match_template(minimap, self.templates["special"], threshold=MARKER_THRESHOLDS["special"])
        if special_matches and elite_room is None:
            elite_marker = special_matches[0]
            elite_room = self.compute_room_id(*elite_marker, minimap)

        down_template = self.templates.get("down")
        if down_template is not None:
            down_matches = self._match_template(minimap, down_template, threshold=MARKER_THRESHOLDS["down"])
            if down_matches:
                down_marker = down_matches[0]
                down_room = self.compute_room_id(*down_marker, minimap)

        query_names = [name for name in QUERY_TEMPLATE_FILES if name in self.templates]
        query_matches = self._match_marker(minimap, query_names, "query")
        if query_matches:
            if self._uses_universal_map():
                query_room, query_marker = self._first_marker_room_and_center_from_matches(
                    query_matches,
                    minimap,
                    excluded_markers=(current_marker, elite_marker, down_marker),
                )
            else:
                query_room, query_marker = self._first_room_and_center_from_matches(
                    query_matches,
                    minimap,
                    excluded_rooms=(current_room, elite_room, down_room),
                )

        boss_matches = self._match_template(minimap, self.templates["boss"], threshold=MARKER_THRESHOLDS["boss"])
        if boss_matches:
            boss_marker = boss_matches[0]
            boss_room = self.compute_room_id(*boss_marker, minimap)

        if query_room is None and boss_room is None and QUERY_COLOR_FALLBACK_ENABLED:
            query_color_matches = self._match_query_by_color(minimap, current_room)
            if self._uses_universal_map():
                query_room, query_marker = self._first_marker_room_and_center_from_matches(
                    query_color_matches,
                    minimap,
                    excluded_markers=(current_marker, boss_marker, elite_marker, down_marker),
                )
            else:
                query_room, query_marker = self._first_room_and_center_from_matches(
                    query_color_matches,
                    minimap,
                    excluded_rooms=(current_room, boss_room, elite_room, down_room),
                )

        return {
            "current_room": current_room,
            "boss_room": boss_room,
            "query_room": query_room,
            "elite_room": elite_room,
            "down_room": down_room,
            "current_marker": current_marker,
            "boss_marker": boss_marker,
            "query_marker": query_marker,
            "elite_marker": elite_marker,
            "down_marker": down_marker,
        }

    def get_debug_scores(self, frame: np.ndarray) -> Dict[str, float]:
        self._debug_scores_frame += 1
        if self._debug_scores_cache and self._debug_scores_frame % self._debug_scores_interval != 0:
            return self._debug_scores_cache

        minimap = self.extract_minimap(frame)
        scores: Dict[str, float] = {}
        for name, template in self.templates.items():
            _, max_val = self._match_template_debug(minimap, template)
            scores[name] = round(max_val, 4)
        self._debug_scores_cache = scores
        return scores

    def _door_candidates_from_objects(self, objects: Sequence[dict]) -> List[DoorCandidate]:
        doors: List[DoorCandidate] = []
        for item in objects:
            if "door" not in item:
                continue
            xywh = item["door"]["xywh"]
            if len(xywh) != 4:
                continue
            x, y, w, h = xywh
            if w <= 0 or h <= 0:
                continue
            center = (x + w / 2.0, y + h / 2.0)
            doors.append(DoorCandidate(bbox=xywh, center=center))
        return doors

    def _pick_target_room(
        self,
        current_room: Optional[Point],
        query_room: Optional[Point],
        down_room: Optional[Point],
        elite_room: Optional[Point],
        boss_room: Optional[Point],
        prefer_special_room: bool,
    ) -> Optional[Point]:
        return self._pick_target(current_room, query_room, down_room, elite_room, boss_room, prefer_special_room)[1]

    def _pick_target(
        self,
        current_room: Optional[Point],
        query_room: Optional[Point],
        down_room: Optional[Point],
        elite_room: Optional[Point],
        boss_room: Optional[Point],
        prefer_special_room: bool,
    ) -> Tuple[Optional[str], Optional[Point]]:
        candidates: List[Tuple[str, Optional[Point]]] = []
        if prefer_special_room:
            candidates.append(("query", query_room))
            candidates.append(("boss", boss_room))
            candidates.append(("elite", elite_room))
            candidates.append(("down", down_room))

        for kind, room in candidates:
            if room is None:
                continue
            if current_room is not None and room == current_room:
                continue
            return kind, room
        return None, None

    def _route_priority(self, current_room: Point, target_room: Point) -> str:
        row_delta = target_room[0] - current_room[0]
        col_delta = target_room[1] - current_room[1]
        if abs(col_delta) >= abs(row_delta) and col_delta != 0:
            return "right" if col_delta > 0 else "left"
        if row_delta != 0:
            return "down" if row_delta > 0 else "up"
        return "right"

    def _marker_direction(self, current_marker: Tuple[float, float], target_marker: Tuple[float, float]) -> Optional[str]:
        dx = target_marker[0] - current_marker[0]
        dy = target_marker[1] - current_marker[1]
        margin = 6.0
        horizontal = None
        vertical = None
        if dx > margin:
            horizontal = "right"
        elif dx < -margin:
            horizontal = "left"
        if dy > margin:
            vertical = "down"
        elif dy < -margin:
            vertical = "up"
        if horizontal and vertical:
            return f"{horizontal}_{vertical}"
        return horizontal or vertical

    def _marker_step_direction(
        self,
        current_marker: Tuple[float, float],
        target_marker: Tuple[float, float],
    ) -> Optional[str]:
        dx = target_marker[0] - current_marker[0]
        dy = target_marker[1] - current_marker[1]
        direction = self._marker_direction(current_marker, target_marker)
        if direction is None or "_" not in direction:
            return direction

        horizontal, vertical = direction.split("_", 1)
        if abs(dx) >= abs(dy):
            return horizontal
        return vertical

    def _target_marker_for_kind(
        self,
        target_kind: Optional[str],
        room_info: Dict[str, object],
    ) -> Optional[Tuple[float, float]]:
        marker_by_kind = {
            "query": room_info.get("query_marker"),
            "boss": room_info.get("boss_marker"),
            "elite": room_info.get("elite_marker"),
            "down": room_info.get("down_marker"),
        }
        marker = marker_by_kind.get(target_kind or "")
        if marker is None:
            return None
        x, y = marker  # type: ignore[misc]
        return float(x), float(y)

    def build_route_snapshot(
        self,
        frame_bgr: np.ndarray,
        detection_objects: Sequence[dict],
        prefer_special_room: bool = True,
        include_debug_scores: bool = True,
    ) -> RouteSnapshot:
        room_info = self.detect_room_markers(frame_bgr)
        current_room = room_info["current_room"]
        boss_room = room_info["boss_room"]
        query_room = room_info["query_room"]
        elite_room = room_info["elite_room"]
        down_room = room_info["down_room"]
        current_marker = room_info.get("current_marker")
        query_marker = room_info.get("query_marker")

        target_kind, target_room = self._pick_target(
            current_room=current_room,
            query_room=query_room,
            down_room=down_room,
            elite_room=elite_room,
            boss_room=boss_room,
            prefer_special_room=prefer_special_room,
        )
        if target_kind is None and prefer_special_room and current_marker is not None:
            marker_targets = (
                ("query", query_room, query_marker),
                ("boss", boss_room, room_info.get("boss_marker")),
                ("elite", elite_room, room_info.get("elite_marker")),
                ("down", down_room, room_info.get("down_marker")),
            )
            for kind, room, marker in marker_targets:
                if marker is None:
                    continue
                if self._marker_direction(current_marker, marker) is None:  # type: ignore[arg-type]
                    continue
                target_kind = kind
                target_room = room
                break

        next_room_direction = None
        target_marker = self._target_marker_for_kind(target_kind, room_info)
        if current_marker is not None and target_marker is not None:
            next_room_direction = self._marker_step_direction(current_marker, target_marker)
        elif current_room is not None and query_room is None and target_room is None:
            target_kind = "query_missing"
            target_room = None
        elif current_room is not None and target_room is not None:
            route_priority = self._route_priority(current_room, target_room)
            next_room_direction = next_direction(deepcopy(self.spec.room_grid), current_room, target_room, priority=route_priority)

        selected_door_center = None
        player_center = None
        for item in detection_objects:
            if "player" in item:
                x, y, w, h = item["player"]["xywh"]
                player_center = (x + w / 2.0, y + h / 2.0)
                break
        door_candidates = self._door_candidates_from_objects(detection_objects)

        def select_door(direction: Optional[str]) -> Optional[DoorCandidate]:
            if direction is None or player_center is None:
                return None
            return choose_best_door(
                door_candidates,
                player_center=player_center,
                expected_direction=direction,
                last_direction=getattr(self, "last_direction", None),
            )

        selected_door = select_door(next_room_direction)
        if selected_door is not None:
            selected_door_center = selected_door.center
            self.last_direction = next_room_direction

        debug_scores = self.get_debug_scores(frame_bgr) if include_debug_scores else None
        return RouteSnapshot(
            current_room=current_room,
            boss_room=boss_room,
            query_room=query_room,
            elite_room=elite_room,
            down_room=down_room,
            target_kind=target_kind,
            target_room=target_room,
            next_room_direction=next_room_direction,
            selected_door_center=selected_door_center,
            debug_scores=debug_scores,
        )
