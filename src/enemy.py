"""Definiciones de enemigos y manejo de estados de IA."""

from enum import Enum, auto

from settings import RADIO_DETECCION


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
        self.estado = EnemyState.PATRULLA
        self.radio_deteccion = RADIO_DETECCION
        self.ruta: list[tuple[int, int]] = []

    def actualizar(self, cuadricula, posicion_jugador: tuple[int, int]) -> None:
        """Actualiza el comportamiento del enemigo según la cuadrícula y el jugador."""
        pass

    def _patrullar(self, cuadricula) -> None:
        """Maneja la patrulla seleccionando puntos de recorrido."""
        pass

    def _perseguir(self, cuadricula, posicion_jugador: tuple[int, int]) -> None:
        """Maneja la persecución siguiendo una ruta hacia el jugador."""
        pass
