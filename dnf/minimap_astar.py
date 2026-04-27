from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Sequence, Tuple


GridPoint = Tuple[int, int]


@dataclass(order=True)
class _Node:
    f: int
    order: int
    position: GridPoint = field(compare=False)
    g: int = field(default=0, compare=False)
    h: int = field(default=0, compare=False)
    parent: Optional["_Node"] = field(default=None, compare=False)


def heuristic(a: GridPoint, b: GridPoint) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _neighbors(position: GridPoint, grid: Sequence[Sequence[int]], priority: str) -> Iterable[GridPoint]:
    x, y = position
    directions = {
        "right": ((0, 1), (1, 0), (-1, 0), (0, -1)),
        "left": ((0, -1), (-1, 0), (1, 0), (0, 1)),
        "up": ((-1, 0), (0, -1), (0, 1), (1, 0)),
        "down": ((1, 0), (0, 1), (0, -1), (-1, 0)),
        "default": ((0, 1), (1, 0), (-1, 0), (0, -1)),
    }
    candidates = directions.get(priority, directions["default"])
    for dx, dy in candidates:
        nx = x + dx
        ny = y + dy
        if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and grid[nx][ny] == 0:
            yield (nx, ny)


def a_star(grid: Sequence[Sequence[int]], start: GridPoint, end: GridPoint, priority: str = "right") -> Optional[List[GridPoint]]:
    if start == end:
        return [start]

    open_list: List[_Node] = []
    push_order = 0
    start_node = _Node(f=0, order=push_order, position=start, g=0, h=heuristic(start, end), parent=None)
    start_node.f = start_node.g + start_node.h
    heapq.heappush(open_list, start_node)
    closed = set()
    best_g = {start: 0}

    while open_list:
        current = heapq.heappop(open_list)
        if current.position in closed:
            continue
        closed.add(current.position)

        if current.position == end:
            path: List[GridPoint] = []
            node: Optional[_Node] = current
            while node is not None:
                path.append(node.position)
                node = node.parent
            return list(reversed(path))

        for next_pos in _neighbors(current.position, grid, priority):
            next_g = current.g + 1
            if next_g >= best_g.get(next_pos, 10 ** 9):
                continue
            best_g[next_pos] = next_g
            next_h = heuristic(next_pos, end)
            push_order += 1
            heapq.heappush(
                open_list,
                _Node(
                    f=next_g + next_h,
                    order=push_order,
                    position=next_pos,
                    g=next_g,
                    h=next_h,
                    parent=current,
                ),
            )
    return None


def judge_direction(starting_point: GridPoint, end_point: GridPoint) -> Optional[str]:
    x1, y1 = starting_point
    x2, y2 = end_point
    if x2 > x1:
        return "down"
    if x2 < x1:
        return "up"
    if y2 > y1:
        return "right"
    if y2 < y1:
        return "left"
    return None


def next_direction(grid: Sequence[Sequence[int]], start: GridPoint, end: GridPoint, priority: str = "right") -> Optional[str]:
    path = a_star(grid, start, end, priority=priority)
    if not path or len(path) < 2:
        return None
    return judge_direction(path[0], path[1])
