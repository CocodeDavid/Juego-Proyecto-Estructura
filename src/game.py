"""Bucle de juego y coordinación de alto nivel."""

import pygame

from settings import (
    ANCHO,
    APARICION_JUGADOR_POR_DEFECTO,
    COLOR_FONDO,
    COLUMNAS,
    FILAS,
    FOTOGRAMAS_POR_SEGUNDO,
    TAMANO_CELDA,
    TITULO_VENTANA,
    ALTO,
)
from src.enemy import Enemy
from src.grid import Grid
from src.player import Player


class Game:
    """Controlador principal del juego para gestionar entidades y renderizado."""

    def __init__(self) -> None:
        """Inicializa el estado del juego y los objetos principales."""
        self.cuadricula = Grid(FILAS, COLUMNAS, TAMANO_CELDA)
        self.jugador = Player(
            self.cuadricula.celda_a_pixel_centro(
                APARICION_JUGADOR_POR_DEFECTO[0],
                APARICION_JUGADOR_POR_DEFECTO[1],
            )
        )
        self.enemigos: list[Enemy] = []

        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption(TITULO_VENTANA)
        self.reloj = pygame.time.Clock()
        self.en_ejecucion = False

    def ejecutar(self) -> None:
        """Ejecuta el bucle principal con eventos, actualización y renderizado."""
        self.en_ejecucion = True
        while self.en_ejecucion:
            self.manejar_eventos()
            self.actualizar()
            self.dibujar()
            self.reloj.tick(FOTOGRAMAS_POR_SEGUNDO)

    def manejar_eventos(self) -> None:
        """Maneja eventos de entrada y cierre de ventana."""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.en_ejecucion = False

    def actualizar(self) -> None:
        """Actualiza los objetos del juego en cada fotograma."""
        self.jugador.actualizar(self.cuadricula)
        for enemigo in self.enemigos:
            enemigo.actualizar(
                self.cuadricula, self.cuadricula.pixel_a_celda(*self.jugador.posicion)
            )

    def dibujar(self) -> None:
        """Dibuja la escena del juego en la ventana."""
        self.pantalla.fill(COLOR_FONDO)
        pygame.display.flip()
