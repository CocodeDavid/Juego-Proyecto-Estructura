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
        # --- NUEVO: Constantes de orientación para el enemigo ---
        self.DIR_ABAJO = 0
        self.DIR_DERECHA = 1
        self.DIR_ARRIBA = 2
        self.DIR_IZQUIERDA = 3
        
        self.orientacion_actual = self.DIR_ABAJO
        self.indice_frame_actual = 0
        self.timer_animacion = 0
        self.velocidad_animacion = 150  # Milisegundos por frame
        self.esta_moviendose = False

        # --- NUEVO: Cargar y cortar el spritesheet del enemigo ---
        try:
            spritesheet_original = pygame.image.load("assets/tiles/enemy_spritesheet.png").convert_alpha()
            ancho_pliego, alto_pliego = spritesheet_original.get_size()
            ancho_frame_original = ancho_pliego // 3
            alto_frame_original = alto_pliego // 3
            
            self.animaciones = {
                self.DIR_ABAJO: [],
                self.DIR_DERECHA: [],
                self.DIR_ARRIBA: [],
                self.DIR_IZQUIERDA: []
            }
            
            def recortar_y_escalar(fila, columna):
                area_recorte = pygame.Rect(columna * ancho_frame_original, fila * alto_frame_original, ancho_frame_original, alto_frame_original)
                frame_original = spritesheet_original.subsurface(area_recorte)
                return pygame.transform.scale(frame_original, (TAMANO_CELDA, TAMANO_CELDA))

            for frame_col in range(3):
                # Fila 0: Abajo
                self.animaciones[self.DIR_ABAJO].append(recortar_y_escalar(0, frame_col))
                
                # Fila 1: Izquierda (en tu imagen el policía mira originalmente a la izquierda)
                frame_izq = recortar_y_escalar(1, frame_col)
                self.animaciones[self.DIR_IZQUIERDA].append(frame_izq)
                
                # Espejamos la izquierda para crear la Derecha
                frame_der = pygame.transform.flip(frame_izq, True, False)
                self.animaciones[self.DIR_DERECHA].append(frame_der)
                
                # Fila 2: Arriba
                self.animaciones[self.DIR_ARRIBA].append(recortar_y_escalar(2, frame_col))
                
        except Exception as e:
            print(f"Advertencia: No se pudo cargar assets/tiles/enemy_spritesheet.png. Error: {e}")
            self.animaciones = None

    def actualizar(self, cuadricula, posicion_jugador: tuple[int, int], algoritmo: str) -> None:
        """Actualiza el camino y desplaza al enemigo hacia el jugador."""
        pos_x_anterior = self.x
        pos_y_anterior = self.y
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
        dx = self.x - pos_x_anterior
        dy = self.y - pos_y_anterior
        
        if dx > 0:
            self.orientacion_actual = self.DIR_DERECHA
        elif dx < 0:
            self.orientacion_actual = self.DIR_IZQUIERDA
        elif dy > 0:
            self.orientacion_actual = self.DIR_ABAJO
        elif dy < 0:
            self.orientacion_actual = self.DIR_ARRIBA
            
        self.esta_moviendose = (dx != 0 or dy != 0)

    def dibujar(self, pantalla, offset_x=0) -> None:
        # --- MODIFICACIÓN: Dibujar enemigo animado o usar respaldo ---
        if getattr(self, 'animaciones', None) and self.orientacion_actual in self.animaciones:
            frames_direccion = self.animaciones[self.orientacion_actual]
            
            if self.esta_moviendose:
                # Usamos el reloj interno global de Pygame para controlar los frames del enemigo
                tiempo_actual = pygame.time.get_ticks()
                if tiempo_actual - self.timer_animacion > self.velocidad_animacion:
                    self.indice_frame_actual = (self.indice_frame_actual + 1) % len(frames_direccion)
                    self.timer_animacion = tiempo_actual
            else:
                self.indice_frame_actual = 0 # Frame estático si no camina
                
            imagen_final = frames_direccion[self.indice_frame_actual]
            
            # Centrado perfecto en la celda
            posicion_pantalla = (
                offset_x + self.x - TAMANO_CELDA // 2,
                self.y - TAMANO_CELDA // 2
            )
            pantalla.blit(imagen_final, posicion_pantalla)
        else:
            # --- TU RESPALDO VIEJO ---
            # Deja aquí la línea original que usabas para dibujar el cuadrado/círculo del enemigo
            # Ejemplo: pygame.draw.circle(pantalla, self.color, (offset_x + self.x, self.y), 15)
            pass