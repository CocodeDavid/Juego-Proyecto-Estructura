"""Lógica de la entidad del jugador."""

from __future__ import annotations

import pygame

from settings import TAMANO_CELDA
from src.busqueda import bfs, bfs_con_debug


class Jugador:
    """Representa al personaje controlado por el jugador."""

    def __init__(self, posicion_inicial: tuple[int, int]) -> None:
        """Inicializa el jugador en una celda de la cuadrícula."""
        self.fila = posicion_inicial[0]
        self.columna = posicion_inicial[1]
        self.x = self.columna * TAMANO_CELDA + TAMANO_CELDA // 2
        self.y = self.fila * TAMANO_CELDA + TAMANO_CELDA // 2
        self.velocidad = 4
        self.moviendose = False
        self.direccion_actual = (0, 0)
        self.color = (50, 180, 80)
        self.destino_celda: tuple[int, int] | None = None
        self.destino_pixel: tuple[int, int] | None = None
        self.ruta_actual: list[tuple[int, int]] = []
        self.nodos_visitados_bfs: set[tuple[int, int]] = set()

    def manejar_teclas(self, teclas, grafo) -> None:
        """Procesa WASD para mover al jugador usando el grafo."""
        if self.moviendose:
            return
        direccion: tuple[int, int] | None = None
        if teclas[pygame.K_w]:
            direccion = (-1, 0)
        elif teclas[pygame.K_s]:
            direccion = (1, 0)
        elif teclas[pygame.K_a]:
            direccion = (0, -1)
        elif teclas[pygame.K_d]:
            direccion = (0, 1)

        if direccion is None:
            return
        nueva_fila = self.fila + direccion[0]
        nueva_columna = self.columna + direccion[1]
        if not grafo.es_nodo_valido((nueva_fila, nueva_columna)):
            return
        self.ruta_actual = []
        self.nodos_visitados_bfs = set()
        self._iniciar_movimiento((nueva_fila, nueva_columna))

    def establecer_destino_click(
        self,
        pos_mouse: tuple[int, int],
        grafo,
        offset_x: int = 0,
    ) -> None:
        """Establece una ruta BFS según el click del mouse."""
        x_relativo = pos_mouse[0] - offset_x
        if x_relativo < 0:
            return
        columna = x_relativo // TAMANO_CELDA
        fila = pos_mouse[1] // TAMANO_CELDA
        destino = (fila, columna)
        if not grafo.es_nodo_valido(destino):
            return
        self.ruta_actual = bfs(grafo, (self.fila, self.columna), destino)
        _, self.nodos_visitados_bfs = bfs_con_debug(
            grafo, (self.fila, self.columna), destino
        )

    def actualizar(self) -> None:
        """Avanza el movimiento por teclado o ruta BFS."""
        if self.moviendose and self.destino_pixel and self.destino_celda:
            destino_x, destino_y = self.destino_pixel
            diferencia_x = destino_x - self.x
            diferencia_y = destino_y - self.y
            if abs(diferencia_x) <= 2 and abs(diferencia_y) <= 2:
                self.x = destino_x
                self.y = destino_y
                self.fila, self.columna = self.destino_celda
                self.moviendose = False
                self.direccion_actual = (0, 0)
                self.destino_celda = None
                self.destino_pixel = None
            else:
                if diferencia_x != 0:
                    paso_x = self.velocidad if diferencia_x > 0 else -self.velocidad
                    if abs(paso_x) > abs(diferencia_x):
                        paso_x = diferencia_x
                    self.x += paso_x
                if diferencia_y != 0:
                    paso_y = self.velocidad if diferencia_y > 0 else -self.velocidad
                    if abs(paso_y) > abs(diferencia_y):
                        paso_y = diferencia_y
                    self.y += paso_y

        if not self.moviendose and self.ruta_actual:
            siguiente = self.ruta_actual.pop(0)
            self._iniciar_movimiento(siguiente)

    def dibujar(self, pantalla: pygame.Surface, offset_x: int = 0) -> None:
        """Dibuja al jugador como un círculo con borde."""
        centro_x = int(self.x + offset_x)
        centro_y = int(self.y)
        radio = (TAMANO_CELDA - 6) // 2
        pygame.draw.circle(pantalla, self.color, (centro_x, centro_y), radio)
        pygame.draw.circle(pantalla, (255, 255, 255), (centro_x, centro_y), radio, 2)

    def _iniciar_movimiento(self, destino: tuple[int, int]) -> None:
        """Configura el movimiento hacia una celda destino."""
        self.destino_celda = destino
        destino_x = destino[1] * TAMANO_CELDA + TAMANO_CELDA // 2
        destino_y = destino[0] * TAMANO_CELDA + TAMANO_CELDA // 2
        self.destino_pixel = (destino_x, destino_y)
        self.direccion_actual = (destino[0] - self.fila, destino[1] - self.columna)
        self.moviendose = True
