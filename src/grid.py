"""Grid representation and helpers."""

import json

from settings import TILE_FLOOR, TILE_WALL


class Grid:
    """Represents a 2D grid of tiles for the game world."""

    def __init__(self, rows: int, cols: int, tile_size: int) -> None:
        """Initialize the grid with floor tiles."""
        self.rows = rows
        self.cols = cols
        self.tile_size = tile_size
        self.tiles = [[TILE_FLOOR for _ in range(cols)] for _ in range(rows)]

    def load_from_json(self, path: str) -> None:
        """Load grid tiles from a JSON level file."""
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
        self.rows = data["rows"]
        self.cols = data["cols"]
        self.tiles = data["tiles"]

    def is_walkable(self, row: int, col: int) -> bool:
        """Return True if a cell is inside bounds and not a wall."""
        if row < 0 or col < 0 or row >= self.rows or col >= self.cols:
            return False
        return self.tiles[row][col] != TILE_WALL

    def get_neighbors(self, row: int, col: int) -> list[tuple[int, int]]:
        """Return walkable 4-directional neighbors for a cell."""
        neighbors: list[tuple[int, int]] = []
        for delta_row, delta_col in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            next_row = row + delta_row
            next_col = col + delta_col
            if self.is_walkable(next_row, next_col):
                neighbors.append((next_row, next_col))
        return neighbors

    def pixel_to_cell(self, x: int, y: int) -> tuple[int, int]:
        """Convert pixel coordinates to grid cell coordinates."""
        return (y // self.tile_size, x // self.tile_size)

    def cell_to_pixel_center(self, row: int, col: int) -> tuple[int, int]:
        """Return pixel coordinates for the center of a cell."""
        center_x = col * self.tile_size + self.tile_size // 2
        center_y = row * self.tile_size + self.tile_size // 2
        return (center_x, center_y)
