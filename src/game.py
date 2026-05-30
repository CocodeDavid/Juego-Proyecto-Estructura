"""Bucle de juego y coordinación de alto nivel."""

import sys

import pygame

from settings import (
    ALTO,
    ANCHO,
    COLOR_FONDO,
    COLUMNAS,
    FILAS,
    FOTOGRAMAS_POR_SEGUNDO,
    MODO_DEBUG,
    TAMANO_CELDA,
    TITULO_VENTANA,
)
from src.enemy import Enemy
from src.game_over import GameOverMenu
from src.grid import Grid
from src.pause import PauseMenu
from src.player import Jugador


class Game:
    """Controlador principal del juego para gestionar entidades y renderizado."""

    def __init__(self) -> None:
        """Inicializa el estado del juego y los objetos principales."""
        self.offset_x = 0
        self.cuadricula = Grid(FILAS, COLUMNAS, TAMANO_CELDA)
        self.jugador = Jugador(self.cuadricula.spawn_jugador)
        self.enemigos: list[Enemy] = []
        self.modo_debug = MODO_DEBUG

        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption(TITULO_VENTANA)
        self.reloj = pygame.time.Clock()
        self.en_ejecucion = False
        
        # Atributos para los menús
        self.pausado = False
        self.game_over = False
        self.menu_pausa = PauseMenu(self.pantalla)
        self.menu_game_over = GameOverMenu(self.pantalla)

    def reiniciar_nivel(self) -> None:
        """Reinicia la posición del jugador, los enemigos y los estados de juego."""
        self.jugador = Jugador(self.cuadricula.spawn_jugador)
        self.enemigos = [Enemy(f, c) for f, c in self.cuadricula.spawns_enemigos]
        self.pausado = False
        self.game_over = False

    def cargar_nivel(self, ruta: str) -> None:
        """Carga un nivel y reposiciona entidades."""
        self.cuadricula.cargar_desde_json(ruta)
        self.reiniciar_nivel()

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
                
            elif evento.type == pygame.KEYDOWN:
                # Si el jugador perdió, no permitimos que oprima atajos
                if self.game_over:
                    continue
                    
                if evento.key == pygame.K_ESCAPE:
                    self.pausado = not self.pausado
                elif evento.key == pygame.K_F1:
                    self.modo_debug = not self.modo_debug
                elif not self.pausado and evento.key in (pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d):
                    teclas = pygame.key.get_pressed()
                    self.jugador.manejar_teclas(teclas, self.cuadricula.grafo)
                    
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                # 1. Gestionar clicks en la pantalla Game Over
                if self.game_over:
                    accion = self.menu_game_over.manejar_click(evento.pos)
                    if accion == "reiniciar":
                        self.reiniciar_nivel()
                    elif accion == "menu":
                        self.en_ejecucion = False 
                    elif accion == "salir":
                        pygame.quit()
                        sys.exit()
                
                # 2. Gestionar clicks en el menú de pausa
                elif self.pausado:
                    accion = self.menu_pausa.manejar_click(evento.pos)
                    if accion == "continuar":
                        self.pausado = False
                    elif accion == "menu":
                        self.en_ejecucion = False
                    elif accion == "salir":
                        pygame.quit()
                        sys.exit()
                        
                # 3. Gestionar clicks en el juego
                else:
                    self.jugador.establecer_destino_click(
                        evento.pos,
                        self.cuadricula.grafo,
                        offset_x=self.offset_x,
                    )

    def actualizar(self) -> None:
        """Actualiza los objetos del juego en cada fotograma."""
        # Detener la lógica si está pausado o el jugador murió
        if self.pausado or self.game_over:
            return
            
        self.jugador.actualizar()
        for enemigo in self.enemigos:
            enemigo.actualizar(
                self.cuadricula, (self.jugador.fila, self.jugador.columna)
            )
            # Evaluar colisiones de derrota
            if enemigo.fila == self.jugador.fila and enemigo.columna == self.jugador.columna:
                self.game_over = True

    def dibujar(self) -> None:
        """Dibuja la escena del juego en la ventana."""
        self.pantalla.fill(COLOR_FONDO)
        self.cuadricula.dibujar(self.pantalla, offset_x=self.offset_x)
        self.jugador.dibujar(self.pantalla, offset_x=self.offset_x)
        
        for enemigo in self.enemigos:
            enemigo.dibujar(self.pantalla, offset_x=self.offset_x)
            
        if self.modo_debug:
            self._dibujar_debug_bfs()
            
        # Dibujar interfaces por encima del juego
        if self.game_over:
            self.menu_game_over.dibujar()
        elif self.pausado:
            self.menu_pausa.dibujar()
            
        pygame.display.flip()

    def _dibujar_debug_bfs(self) -> None:
        # (El código del debug_bfs se mantiene igual)
        superficie = pygame.Surface(self.pantalla.get_size(), pygame.SRCALPHA)
        color_visitados = (60, 120, 200, 120)
        color_ruta = (250, 250, 60, 200)

        for nodo in self.jugador.nodos_visitados_bfs:
            rect = pygame.Rect(
                self.offset_x + nodo[1] * TAMANO_CELDA,
                nodo[0] * TAMANO_CELDA,
                TAMANO_CELDA,
                TAMANO_CELDA,
            )
            pygame.draw.rect(superficie, color_visitados, rect)

        for nodo in self.jugador.ruta_actual:
            rect = pygame.Rect(
                self.offset_x + nodo[1] * TAMANO_CELDA,
                nodo[0] * TAMANO_CELDA,
                TAMANO_CELDA,
                TAMANO_CELDA,
            )
            pygame.draw.rect(superficie, color_ruta, rect)

        self.pantalla.blit(superficie, (0, 0))