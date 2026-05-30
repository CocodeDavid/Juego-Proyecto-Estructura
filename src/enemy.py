"""Definiciones de enemigos y manejo de estados de IA."""

from enum import Enum, auto

import pygame

from settings import RADIO_DETECCION, TAMANO_CELDA


class EnemyState(Enum):
    """Estados finitos para el comportamiento del enemigo."""

    PATRULLA = auto()
    ALERTA = auto()
    PERSECUCION = auto()
    ATAQUE = auto()


class Enemy:
    """Representa un enemigo con un comportamiento básico de estados."""

    def __init__(self, fila: int, columna: int) -> None:
        """Inicializa el enemigo en una celda de la cuadrícula."""
        self.fila = fila
        self.columna = columna
        self.x = self.columna * TAMANO_CELDA + TAMANO_CELDA // 2
        self.y = self.fila * TAMANO_CELDA + TAMANO_CELDA // 2
        self.estado = EnemyState.PATRULLA
        self.radio_deteccion = RADIO_DETECCION
        self.ruta: list[tuple[int, int]] = []
        self.color = (200, 60, 60) # Color rojo para diferenciarlos del jugador

    def actualizar(self, cuadricula, posicion_jugador: tuple[int, int]) -> None:
        """Actualiza el comportamiento del enemigo según la cuadrícula y el jugador."""
        # Por ahora se quedan quietos esperando la implementación futura de búsqueda
        pass

    def dibujar(self, pantalla: pygame.Surface, offset_x: int = 0) -> None:
        """Dibuja al enemigo como un círculo rojo con borde blanco."""
        centro_x = int(self.x + offset_x)
        centro_y = int(self.y)
        radio = (TAMANO_CELDA - 6) // 2
        pygame.draw.circle(pantalla, self.color, (centro_x, centro_y), radio)
        pygame.draw.circle(pantalla, (255, 255, 255), (centro_x, centro_y), radio, 2)

    def _patrullar(self, cuadricula) -> None:
        """Maneja la patrulla seleccionando puntos de recorrido."""
        pass

    def _perseguir(self, cuadricula, posicion_jugador: tuple[int, int]) -> None:
        """Maneja la persecución siguiendo una ruta hacia el jugador."""
        pass