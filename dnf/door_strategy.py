from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

Point = tuple[float, float]


@dataclass
class DoorCandidate:
    bbox: Sequence[float]
    center: Point


def opposite_direction(direction: str | None) -> str | None:
    direction = direction.lower() if direction else None
    mapping = {
        "left": "right",
        "right": "left",
        "up": "down",
        "down": "up",
        "left_up": "right_down",
        "left_down": "right_up",
        "right_up": "left_down",
        "right_down": "left_up",
    }
    return mapping.get(direction)


def _axis_offsets(player: Point, door: Point) -> tuple[float, float]:
    dx = door[0] - player[0]
    dy = door[1] - player[1]
    return dx, dy


def _direction_match(expected_direction: str, dx: float, dy: float, margin: float) -> bool:
    expected_direction = expected_direction.lower()
    parts = set(expected_direction.split("_"))
    if "right" in parts and dx <= margin:
        return False
    if "left" in parts and dx >= -margin:
        return False
    if "up" in parts and dy >= -margin:
        return False
    if "down" in parts and dy <= margin:
        return False
    return True


def choose_best_door(
    doors: Sequence[DoorCandidate],
    player_center: Point,
    expected_direction: str | None,
    last_direction: str | None = None,
    margin: float = 16.0,
) -> DoorCandidate | None:
    if not doors:
        return None
    if expected_direction is None:
        return min(
            doors, key=lambda item: abs(item.center[0] - player_center[0]) + abs(item.center[1] - player_center[1])
        )

    expected_direction = expected_direction.lower()
    reverse_direction = opposite_direction(last_direction)
    candidates: list[tuple[tuple[float, float, float], DoorCandidate]] = []
    fallback: list[tuple[tuple[float, float, float], DoorCandidate]] = []

    for door in doors:
        dx, dy = _axis_offsets(player_center, door.center)
        abs_dx = abs(dx)
        abs_dy = abs(dy)
        match = _direction_match(expected_direction, dx, dy, margin)

        parts = set(expected_direction.split("_"))
        forward = 0.0
        if "right" in parts:
            forward += dx
        if "left" in parts:
            forward += -dx
        if "down" in parts:
            forward += dy
        if "up" in parts:
            forward += -dy

        has_horizontal = bool(parts & {"left", "right"})
        has_vertical = bool(parts & {"up", "down"})
        if has_horizontal and has_vertical:
            sideways = abs(abs_dx - abs_dy) * 0.25
        elif has_horizontal:
            sideways = abs_dy
        else:
            sideways = abs_dx

        reverse_penalty = 0.0
        if reverse_direction and expected_direction == reverse_direction:
            reverse_penalty = 2000.0

        score = (-forward + reverse_penalty, sideways, abs_dx + abs_dy)
        if match:
            candidates.append((score, door))
        fallback.append((score, door))

    if candidates:
        candidates.sort(key=lambda item: item[0])
        return candidates[0][1]

    return None
