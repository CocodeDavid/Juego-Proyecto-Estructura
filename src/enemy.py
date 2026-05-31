"""Definiciones de enemigos y manejo de navegación por IA."""

import pygame

from settings import TAMANO_CELDA
from src.pathfinding import a_estrella, dfs, dijkstra


class Enemy:
    """Representa un enemigo que persigue activamente al jugador en 4 direcciones."""

    def __init__(self, fila: int, columna: int) -> None:
        """Inicializa el enemigo en una coordenada específica."""
        self.fila = fila
        self.columna = columna
        # Posicionamiento inicial centrado en píxeles
        self.x = self.columna * TAMANO_CELDA + TAMANO_CELDA // 2
        self.y = self.fila * TAMANO_CELDA + TAMANO_CELDA // 2
        self.velocidad = 2  
        self.moviendose = False
        self.color = (200, 70, 70)
        self.ruta: list[tuple[int, int]] = []
        self.destino_celda: tuple[int, int] | None = None
        
        # NUEVO: Memoria para saber si el jugador se movió desde el último cálculo
        self.ultima_posicion_jugador: tuple[int, int] | None = None

    def actualizar(self, cuadricula, posicion_jugador: tuple[int, int], algoritmo: str) -> None:
        """Actualiza el camino y desplaza al enemigo hacia el jugador."""
        if not self.moviendose:
            inicio = (self.fila, self.columna)
            
            if inicio != posicion_jugador:
                if algoritmo == "dfs":
                    # LÓGICA AAA: Solo recalcula DFS si se quedó sin ruta O 
                    # si el jugador se movió a una celda diferente.
                    # Esto evita los bucles infinitos y asegura la persecución.
                    if not self.ruta or self.ultima_posicion_jugador != posicion_jugador:
                        self.ruta = dfs(cuadricula.grafo, inicio, posicion_jugador)
                        self.ultima_posicion_jugador = posicion_jugador
                        
                elif algoritmo == "dijkstra":
                    # Los algoritmos óptimos sí pueden recalcularse en cada baldosa
                    self.ruta = dijkstra(cuadricula.grafo, inicio, posicion_jugador)
                else:
                    self.ruta = a_estrella(cuadricula.grafo, inicio, posicion_jugador)

            if self.ruta:
                self.destino_celda = self.ruta.pop(0)
                self.moviendose = True

        # Ejecución del movimiento fluido por píxeles
        if self.moviendose and self.destino_celda:
            target_x = self.destino_celda[1] * TAMANO_CELDA + TAMANO_CELDA // 2
            target_y = self.destino_celda[0] * TAMANO_CELDA + TAMANO_CELDA // 2

            diferencia_x = target_x - self.x
            diferencia_y = target_y - self.y

            if diferencia_x != 0:
                self.x += self.velocidad if diferencia_x > 0 else -self.velocidad
            elif diferencia_y != 0:
                self.y += self.velocidad if diferencia_y > 0 else -self.velocidad

            # Verificar llegada al centro de la celda destino
            if abs(self.x - target_x) < self.velocidad and abs(self.y - target_y) < self.velocidad:
                self.x = target_x
                self.y = target_y
                self.fila = self.destino_celda[0]
                self.columna = self.destino_celda[1]
                self.moviendose = False

    def dibujar(self, pantalla: pygame.Surface, offset_x: int = 0) -> None:
        """Dibuja al enemigo en pantalla."""
        centro_x = int(self.x + offset_x)
        centro_y = int(self.y)
        radio = (TAMANO_CELDA - 6) // 2
        pygame.draw.circle(pantalla, self.color, (centro_x, centro_y), radio)
        pygame.draw.circle(pantalla, (255, 255, 255), (centro_x, centro_y), radio, 1)