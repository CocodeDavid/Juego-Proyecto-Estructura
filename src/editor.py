"""Simple level editor for grid-based maps."""

import json

import pygame

from settings import (
    COLOR_BG,
    COLOR_FLOOR,
    COLOR_GRID,
    COLOR_SPAWN_ENEMY,
    COLOR_SPAWN_PLAYER,
    COLOR_WALL,
    COLS,
    DEFAULT_PLAYER_SPAWN,
    EDITOR_TITLE,
    ENEMY_TYPE_BASIC,
    FPS,
    HEIGHT,
    LEVEL_NAME,
    ROWS,
    TILE_FLOOR,
    TILE_SIZE,
    TILE_SPAWN_ENEMY,
    TILE_SPAWN_PLAYER,
    TILE_WALL,
    WIDTH,
)
from src.grid import Grid


class LevelEditor:
    
    "EN python no existe el private, public o proteted"
    "No es necesario la definicion de los atributos"
    "Para declarar un atributo hacemos self.nombreatributo"
    def __init__(self) -> None:
        """Iconstructor y sus atributos"""
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(EDITOR_TITLE)
        self.clock = pygame.time.Clock()
        self.grid = Grid(ROWS, COLS, TILE_SIZE)
        self.selected_tile = TILE_WALL
        self.running = False
        self.player_spawn = {"row": DEFAULT_PLAYER_SPAWN[0], "col": DEFAULT_PLAYER_SPAWN[1]}

        self._set_tile(
            self.player_spawn["row"],
            self.player_spawn["col"],
            TILE_SPAWN_PLAYER,
        )

    def arranque(self) -> None:
        """Pantalla del editor"""
        self.running = True
        while self.running:
            self.InteraccionesdelUsuario()
            self._draw()
            self.clock.tick(FPS)
        pygame.quit()

    def InteraccionesdelUsuario(self) -> None:
        """Aca se manejan o manejaran que pasa si el usuario hace click o tecla algo"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_toolbar_keys(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.InteracciondeClickdeMouse(event.button, event.pos)

    def _handle_toolbar_keys(self, key: int) -> None:
        """Update the selected tile based on toolbar key presses."""
        if key == pygame.K_1:
            self.selected_tile = TILE_FLOOR
        elif key == pygame.K_2:
            self.selected_tile = TILE_WALL
        elif key == pygame.K_3:
            self.selected_tile = TILE_SPAWN_PLAYER
        elif key == pygame.K_4:
            self.selected_tile = TILE_SPAWN_ENEMY

    def InteracciondeClickdeMouse(self, button: int, pos: tuple[int, int]) -> None:
        """Paint or erase tiles based on mouse clicks."""
        row = pos[1] // TILE_SIZE
        col = pos[0] // TILE_SIZE
        if row < 0 or col < 0 or row >= self.grid.rows or col >= self.grid.cols:
            return
        if button == 1:
            self._paint_tile(row, col)
        elif button == 3:
            self._erase_tile(row, col)

    def _paint_tile(self, row: int, col: int) -> None:
        """Paint the selected tile onto the grid."""
        if self.selected_tile == TILE_SPAWN_PLAYER:
            self._set_tile(self.player_spawn["row"], self.player_spawn["col"], TILE_FLOOR)
            self.player_spawn = {"row": row, "col": col}
        self._set_tile(row, col, self.selected_tile)

    def _erase_tile(self, row: int, col: int) -> None:
        """Erase a tile and reset spawn data when needed."""
        if self.grid.tiles[row][col] == TILE_SPAWN_PLAYER:
            self.player_spawn = {"row": DEFAULT_PLAYER_SPAWN[0], "col": DEFAULT_PLAYER_SPAWN[1]}
        self._set_tile(row, col, TILE_FLOOR)

    def _set_tile(self, row: int, col: int, value: int) -> None:
        """Set the value of a grid tile."""
        self.grid.tiles[row][col] = value

    def _scan_spawns(self) -> tuple[dict[str, int], list[dict[str, int | str]]]:
        """Scan the grid to find player and enemy spawn tiles."""
        player_spawn = self.player_spawn
        enemy_spawns: list[dict[str, int | str]] = []
        for row in range(self.grid.rows):
            for col in range(self.grid.cols):
                tile = self.grid.tiles[row][col]
                if tile == TILE_SPAWN_PLAYER:
                    player_spawn = {"row": row, "col": col}
                elif tile == TILE_SPAWN_ENEMY:
                    enemy_spawns.append({"row": row, "col": col, "type": ENEMY_TYPE_BASIC})
        return player_spawn, enemy_spawns

    def _draw(self) -> None:
        """Draw the editor grid and tiles."""
        self.screen.fill(COLOR_BG)
        for row, row_tiles in enumerate(self.grid.tiles):
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
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, COLOR_GRID, rect, 1)
        pygame.display.flip()

    def save_to_json(self, path: str) -> None:
        """Save the current grid and spawns to a JSON file."""
        player_spawn, enemy_spawns = self._scan_spawns()
        level_data = {
            "name": LEVEL_NAME,
            "rows": self.grid.rows,
            "cols": self.grid.cols,
            "tiles": self.grid.tiles,
            "player_spawn": player_spawn,
            "enemy_spawns": enemy_spawns,
        }
        with open(path, "w", encoding="utf-8") as file:
            json.dump(level_data, file, indent=2, ensure_ascii=False)


def main() -> None:
    """Launch the level editor."""
    editor = LevelEditor()
    editor.arranque()


if __name__ == "__main__":
    main()
