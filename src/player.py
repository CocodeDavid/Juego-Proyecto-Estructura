"""Player entity logic."""

from src.pathfinding import astar


class Player:
    """Represents the player-controlled character."""

    def __init__(self, position: tuple[int, int]) -> None:
        """Initialize the player at a pixel position."""
        self.position = position
        self.path: list[tuple[int, int]] = []
        self.open_set: set[tuple[int, int]] = set()
        self.closed_set: set[tuple[int, int]] = set()

    def set_destination(self, grid, goal_cell: tuple[int, int]) -> None:
        """Compute a path to a goal cell and store it."""
        start_cell = grid.pixel_to_cell(*self.position)
        path, open_set, closed_set = astar(grid, start_cell, goal_cell)
        self.path = path
        self.open_set = open_set
        self.closed_set = closed_set

    def update(self, grid) -> None:
        """Move one step along the path each frame."""
        if not self.path:
            return
        next_cell = self.path.pop(0)
        self.position = grid.cell_to_pixel_center(*next_cell)
