"""Game loop and high-level coordination."""

import pygame

from settings import (
    COLOR_BG,
    COLS,
    DEFAULT_PLAYER_SPAWN,
    FPS,
    HEIGHT,
    ROWS,
    TILE_SIZE,
    WIDTH,
    WINDOW_TITLE,
)
from src.enemy import Enemy
from src.grid import Grid
from src.player import Player


class Game:
    """Main game controller for managing entities and rendering."""

    def __init__(self) -> None:
        """Initialize the game state and core objects."""
        self.grid = Grid(ROWS, COLS, TILE_SIZE)
        self.player = Player(
            self.grid.cell_to_pixel_center(
                DEFAULT_PLAYER_SPAWN[0],
                DEFAULT_PLAYER_SPAWN[1],
            )
        )
        self.enemies: list[Enemy] = []

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.running = False

    def run(self) -> None:
        """Run the main game loop with event handling, updates, and rendering."""
        self.running = True
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self) -> None:
        """Handle input events and window controls."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self) -> None:
        """Update game objects each frame."""
        self.player.update(self.grid)
        for enemy in self.enemies:
            enemy.update(self.grid, self.grid.pixel_to_cell(*self.player.position))

    def draw(self) -> None:
        """Draw the game scene to the window."""
        self.screen.fill(COLOR_BG)
        pygame.display.flip()
