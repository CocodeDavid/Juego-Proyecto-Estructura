"""Estructura de grafo basada en listas de adyacencia para navegación."""

from __future__ import annotations

import pygame

from settings import CELDA_MURO


class Grafo:
    """Representa la cuadrícula como grafo para búsquedas de pathfinding.

    La grilla se mantiene como matriz para el dibujo, pero los algoritmos de
    búsqueda operan sobre esta lista de adyacencia. Esta separación es clave
    para el curso porque permite razonar sobre estructuras de datos sin
    depender directamente de la representación visual.
    """

    def __init__(self) -> None:
        """Inicializa un grafo vacío."""
        self.lista_adyacencia: dict[tuple[int, int], list[tuple[int, int]]] = {}

    def construir_desde_grilla(self, grilla) -> None:
        """Construye la lista de adyacencia a partir de la grilla."""
        self.lista_adyacencia = {}
        for fila in range(grilla.filas):
            for columna in range(grilla.columnas):
                if grilla.celdas[fila][columna] == CELDA_MURO:
                    continue
                nodo = (fila, columna)
                vecinos: list[tuple[int, int]] = []
                for delta_fila, delta_columna in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nueva_fila = fila + delta_fila
                    nueva_columna = columna + delta_columna
                    if (
                        0 <= nueva_fila < grilla.filas
                        and 0 <= nueva_columna < grilla.columnas
                        and grilla.celdas[nueva_fila][nueva_columna] != CELDA_MURO
                    ):
                        vecinos.append((nueva_fila, nueva_columna))
                self.lista_adyacencia[nodo] = vecinos

    def obtener_vecinos(self, nodo: tuple[int, int]) -> list[tuple[int, int]]:
        """Devuelve la lista de vecinos del nodo solicitado."""
        return list(self.lista_adyacencia.get(nodo, []))

    def es_nodo_valido(self, nodo: tuple[int, int]) -> bool:
        """Indica si un nodo existe dentro del grafo."""
        return nodo in self.lista_adyacencia

    def total_nodos(self) -> int:
        """Devuelve la cantidad de nodos almacenados."""
        return len(self.lista_adyacencia)

    def dibujar_debug(
        self, pantalla: pygame.Surface, tam_tile: int, offset_x: int = 0
    ) -> None:
        """Dibuja líneas de depuración para visualizar la lista de adyacencia."""
        superficie = pygame.Surface(pantalla.get_size(), pygame.SRCALPHA)
        color_linea = (60, 80, 120, 102)
        for nodo, vecinos in self.lista_adyacencia.items():
            centro_x = offset_x + nodo[1] * tam_tile + tam_tile // 2
            centro_y = nodo[0] * tam_tile + tam_tile // 2
            for vecino in vecinos:
                vecino_x = offset_x + vecino[1] * tam_tile + tam_tile // 2
                vecino_y = vecino[0] * tam_tile + tam_tile // 2
                pygame.draw.line(
                    superficie,
                    color_linea,
                    (centro_x, centro_y),
                    (vecino_x, vecino_y),
                    1,
                )
        pantalla.blit(superficie, (0, 0))
