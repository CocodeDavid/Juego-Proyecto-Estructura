"""Enemy entity definitions and AI state management."""

from enum import Enum, auto

from settings import DETECTION_RADIUS


class EnemyState(Enum):
    """Finite states for enemy behavior."""

    PATROL = auto()
    ALERT = auto()
    CHASE = auto()
    ATTACK = auto()


class Enemy:
    """Represents an enemy with basic finite-state behavior."""

    def __init__(self, row: int, col: int) -> None:
        """Initialize the enemy at a grid cell position."""
        self.row = row
        self.col = col
        self.state = EnemyState.PATROL
        self.detection_radius = DETECTION_RADIUS
        self.path: list[tuple[int, int]] = []

    def update(self, grid, player_pos: tuple[int, int]) -> None:
        """Update the enemy behavior based on grid and player position."""
        pass

    def _patrol(self, grid) -> None:
        """Handle patrol behavior by selecting waypoints and wandering."""
        pass

    def _chase(self, grid, player_pos: tuple[int, int]) -> None:
        """Handle chasing behavior by following a path toward the player."""
        pass
