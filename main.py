"""Main entry point for the grid-based game."""

import pygame

from settings import (
    COLOR_BG,
    COLOR_FLOOR,
    COLOR_GRID,
    COLOR_SPAWN_ENEMY,
    COLOR_SPAWN_PLAYER,
    COLOR_WALL,
    COLS,
    DEFAULT_ENEMY_SPAWN,
    DEFAULT_PLAYER_SPAWN,
    FPS,
    HEIGHT,
    ROWS,
    TILE_FLOOR,
    TILE_SIZE,
    TILE_SPAWN_ENEMY,
    TILE_SPAWN_PLAYER,
    TILE_WALL,
    WIDTH,
    WINDOW_TITLE,
)


def generadordegrilla(rows: int, cols: int) -> list[list[int]]:
    """Create a simple grid with border walls and spawn markers."""
    grid = []
    for _ in range(rows):
        fila_actual = [] 
    
        for _ in range(cols):
            fila_actual.append(TILE_FLOOR) 

        grid.append(fila_actual)

    for row in range(rows):
        for col in range(cols):
            if row in (0, rows - 1) or col in (0, cols - 1):
                grid[row][col] = TILE_WALL
    player_row, player_col = DEFAULT_PLAYER_SPAWN
    enemy_row, enemy_col = DEFAULT_ENEMY_SPAWN
    grid[player_row][player_col] = TILE_SPAWN_PLAYER
    grid[enemy_row][enemy_col] = TILE_SPAWN_ENEMY
    return grid


def draw_grid(screen: pygame.Surface, grid: list[list[int]]) -> None:
    """Draw the placeholder grid tiles to the screen."""
    for row, row_tiles in enumerate(grid):
        for col, tile in enumerate(row_tiles):
            if tile == TILE_WALL:
                color = COLOR_WALL
            elif tile == TILE_SPAWN_PLAYER:
                color = COLOR_SPAWN_PLAYER
            elif tile == TILE_SPAWN_ENEMY:
                color = COLOR_SPAWN_ENEMY
            else:
                color = COLOR_FLOOR
            rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, COLOR_GRID, rect, 1)


def main() -> None:
    """Run the placeholder game loop with a visible grid."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()
    grid = generadordegrilla(ROWS, COLS)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(COLOR_BG)
        draw_grid(screen, grid)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
