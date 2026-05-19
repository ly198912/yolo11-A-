from __future__ import annotations

from dataclasses import dataclass

Rect = tuple[int, int, int, int]


@dataclass
class MapSpec:
    name: str
    crop_rect_1067: Rect
    crop_rect_800: Rect | None
    minimap_width: int
    minimap_height: int
    rows: int
    cols: int
    room_grid: list[list[int]]
    room_rect_1067: Rect | None = None
    room_rect_800: Rect | None = None


def _all_walkable(rows: int, cols: int) -> list[list[int]]:
    return [[0 for _ in range(cols)] for _ in range(rows)]


UNIVERSAL_MINIMAP_SPEC = MapSpec(
    name="universal",
    # Large top-right search box matching the red frame in 800x600 captures.
    # It intentionally contains the full minimap plus surrounding UI so small
    # minimap layout shifts do not require per-map rectangle tuning.
    crop_rect_1067=(797, 23, 1066, 192),
    crop_rect_800=(598, 23, 799, 192),
    minimap_width=201,
    minimap_height=169,
    # The logical room grid should cover the minimap panel, not the full
    # oversized search box. 5x6 is the broad common room lattice used as a
    # fallback; marker-to-marker routing remains the primary universal path.
    rows=5,
    cols=6,
    room_grid=_all_walkable(5, 6),
    room_rect_1067=(899, 29, 1059, 123),
    room_rect_800=(674, 29, 794, 123),
)


MAP_SPECS: dict[str, MapSpec] = {
    "universal": UNIVERSAL_MINIMAP_SPEC,
}
