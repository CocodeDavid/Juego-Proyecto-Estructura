"""Pathfinding algorithms for grid navigation."""

import heapq
from collections import deque
from itertools import count


def heuristic(a: tuple[int, int], b: tuple[int, int]) -> int:
    """Return the Manhattan distance between two grid cells."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(
    grid,
    start: tuple[int, int],
    goal: tuple[int, int],
) -> tuple[list[tuple[int, int]], set[tuple[int, int]], set[tuple[int, int]]]:
    """Compute an A* path and return path, open set, and closed set."""
    if not grid.is_walkable(*start) or not grid.is_walkable(*goal):
        return ([], set(), set())

    frontier: list[tuple[int, int, tuple[int, int]]] = []
    counter = count()
    heapq.heappush(frontier, (0, next(counter), start))

    came_from: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    g_score = {start: 0}
    open_nodes = {start}
    closed_nodes: set[tuple[int, int]] = set()

    while frontier:
        _, _, current = heapq.heappop(frontier)
        if current in closed_nodes:
            continue

        open_nodes.discard(current)
        closed_nodes.add(current)

        if current == goal:
            break

        for neighbor in grid.get_neighbors(*current):
            if neighbor in closed_nodes:
                continue

            tentative_g = g_score[current] + 1
            if tentative_g < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(frontier, (f_score, next(counter), neighbor))
                open_nodes.add(neighbor)

    if goal not in came_from:
        return ([], open_nodes, closed_nodes)

    path: list[tuple[int, int]] = []
    node: tuple[int, int] | None = goal
    while node is not None:
        path.append(node)
        node = came_from[node]
    path.reverse()

    return (path, open_nodes, closed_nodes)


def bfs_detect(
    grid,
    origin: tuple[int, int],
    target: tuple[int, int],
    radius: int,
) -> bool:
    """Return True if target is reachable within radius steps using BFS."""
    if origin == target:
        return True

    queue = deque([(origin, 0)])
    visited = {origin}

    while queue:
        current, steps = queue.popleft()
        if steps >= radius:
            continue

        for neighbor in grid.get_neighbors(*current):
            if neighbor in visited:
                continue
            if neighbor == target:
                return True
            visited.add(neighbor)
            queue.append((neighbor, steps + 1))

    return False
