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
        crop_rect_1067=(790, 25, 1067, 230),
        crop_rect_800=(592, 25, 800, 230),
        minimap_width=208,
        minimap_height=205,
        rows=7,
        cols=8,
        room_grid=_all_walkable(7, 8),
        # Search the full UI box, but map markers against the tighter room graph.
        room_rect_1067=(816, 35, 1055, 156),
        room_rect_800=(612, 35, 791, 156),
    ),
}
