from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


Rect = Tuple[int, int, int, int]


@dataclass
class MapSpec:
    name: str
    crop_rect_1067: Rect
    crop_rect_800: Optional[Rect]
    minimap_width: int
    minimap_height: int
    rows: int
    cols: int
    room_grid: List[List[int]]
    room_rect_1067: Optional[Rect] = None
    room_rect_800: Optional[Rect] = None


def _all_walkable(rows: int, cols: int) -> List[List[int]]:
    return [[0 for _ in range(cols)] for _ in range(rows)]


MAP_SPECS: Dict[str, MapSpec] = {
    "generic": MapSpec(
        name="generic",
        crop_rect_1067=(893, 52, 1055, 142),
        crop_rect_800=(680, 57, 780, 155),
        minimap_width=162,
        minimap_height=90,
        rows=5,
        cols=9,
        room_grid=_all_walkable(5, 9),
        room_rect_800=(686, 82, 776, 151),
    ),
    "haibolun": MapSpec(
        name="haibolun",
        crop_rect_1067=(966, 52, 1056, 124),
        crop_rect_800=None,
        minimap_width=90,
        minimap_height=72,
        rows=4,
        cols=5,
        room_grid=_all_walkable(4, 5),
    ),
}
