"""Bucle de juego y coordinación de alto nivel."""

import json
import sys
from pathlib import Path

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
    CELDA_APARICION_ENEMIGO,
)
from src.enemy import Enemy
from src.game_over import GameOverMenu
from src.grid import Grid
from src.pause import PauseMenu
from src.player import Jugador


class Game:
    """Controlador principal del juego para gestionar entidades y renderizado."""

    def __init__(self) -> None:
        """Inicializa el estado del juego y los objetos principales.lo que esta aca es lo que unicamente se usa aca y por eso no esta en settings"""
        self.DIR_ABAJO = 0
        self.DIR_DERECHA = 1
        self.DIR_ARRIBA = 2
        self.DIR_IZQUIERDA = 3
        self.offset_x = 0
        self.cuadricula = Grid(FILAS, COLUMNAS, TAMANO_CELDA)
        self.jugador = Jugador(self.cuadricula.spawn_jugador)
        self.enemigos: list[Enemy] = []
        self.modo_debug = MODO_DEBUG

        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption(TITULO_VENTANA)
        self.reloj = pygame.time.Clock()
        self.en_ejecucion = False
        self.estado = "jugando"
        self.ruta_nivel_actual: str | None = None
        
        # Cargar configuración (algoritmo y visualizar ruta)
        self.algoritmo_enemigo, self.visualizar_recorrido = self._cargar_configuracion()

        # Atributos para los menús y estados
        self.pausado = False
        self.game_over = False
        self.menu_pausa = PauseMenu(self.pantalla)
        self.menu_game_over = GameOverMenu(self.pantalla)
        self.fuente_ganaste_titulo = pygame.font.SysFont(None, 64)
        self.fuente_ganaste_boton = pygame.font.SysFont(None, 40)
        self.botones_ganaste = [
            {"texto": "Volver a jugar", "accion": "reiniciar", "color": (50, 160, 80), "rect": pygame.Rect(0, 0, 0, 0)},
            {"texto": "Volver al menú", "accion": "menu", "color": (200, 150, 40), "rect": pygame.Rect(0, 0, 0, 0)},
            {"texto": "Salir", "accion": "salir", "color": (200, 60, 60), "rect": pygame.Rect(0, 0, 0, 0)},
        ]
        # Reemplaza tu bloque de carga de textura player por este:
        try:
            # 1. Cargamos el pliego de sprites completo
            spritesheet_original = pygame.image.load("assets/tiles/player.png").convert_alpha()
            
            # Calculamos el tamaño de cada "cuadradito" individual dentro del pliego (es 3x3)
            ancho_pliego, alto_pliego = spritesheet_original.get_size()
            ancho_frame_original = ancho_pliego // 3
            alto_frame_original = alto_pliego // 3
            
            # 2. Creamos un diccionario para organizar nuestras animaciones
            self.animaciones = {
                self.DIR_ABAJO: [],
                self.DIR_DERECHA: [],
                self.DIR_ARRIBA: [],
                self.DIR_IZQUIERDA: []
            }
            
            # Función auxiliar para recortar y reescalar cada frame al tamaño de tu juego
            def recortar_y_escalar(fila, columna):
                # Recortamos el frame original (área exacta en píxeles)
                area_recorte = pygame.Rect(columna * ancho_frame_original, fila * alto_frame_original, ancho_frame_original, alto_frame_original)
                frame_original = spritesheet_original.subsurface(area_recorte)
                
                # Lo reescalamos para que encaje perfecto en tu TAMANO_CELDA
                return pygame.transform.scale(frame_original, (TAMANO_CELDA, TAMANO_CELDA))

            # 3. "Cortamos" el spritesheet y llenamos el diccionario
            for frame_col in range(3):
                # Recortamos la fila de ABAJO (Row 0)
                frame_abajo = recortar_y_escalar(0, frame_col)
                self.animaciones[self.DIR_ABAJO].append(frame_abajo)
                
                frame_izquierda = recortar_y_escalar(1, frame_col)
                self.animaciones[self.DIR_IZQUIERDA].append(frame_izquierda)
                
                # Espejamos el frame de la izquierda para obtener la caminata a la DERECHA
                frame_derecha = pygame.transform.flip(frame_izquierda, True, False)
                self.animaciones[self.DIR_DERECHA].append(frame_derecha)
                
                # Recortamos la fila de ARRIBA (Row 2)
                frame_arriba = recortar_y_escalar(2, frame_col)
                self.animaciones[self.DIR_ARRIBA].append(frame_arriba)
                
                
            # 4. Variables de estado para el player
            self.orientacion_actual = self.DIR_ABAJO # Empieza mirando hacia abajo
            self.indice_frame_actual = 0           # Empieza en el primer frame (estático)
            self.timer_animacion = 0               # Temporizador para cambiar frames
            self.velocidad_animacion = 150         # Milisegundos entre cada cambio de frame
            self.esta_moviendose = False           # Solo animamos si el player se mueve
            
        except Exception as e:
            print(f"Advertencia: No se pudo cargar el spritesheet de player. Error: {e}")
            self.animaciones = None

    def _cargar_configuracion(self) -> tuple[str, bool]:
        """Carga la configuración guardada del enemigo y la visualización."""
        ruta = Path(__file__).resolve().parents[1] / "config.json"
        algoritmo = "a_estrella"
        visualizar = False
        if ruta.exists():
            try:
                with open(ruta, "r", encoding="utf-8") as archivo:
                    datos = json.load(archivo)
                    algoritmo = datos.get("algoritmo_enemigo", "a_estrella")
                    visualizar = datos.get("visualizar_recorrido", False)
            except Exception:
                pass
        return algoritmo, visualizar

    def reiniciar_nivel(self) -> None:
        """Reinicia la posición del jugador, los enemigos y los estados de juego."""
        self.jugador = Jugador(self.cuadricula.spawn_jugador)
        self.enemigos = []
        # Escanear mapa para reubicar enemigos
        for fila in range(self.cuadricula.filas):
            for columna in range(self.cuadricula.columnas):
                if self.cuadricula.celdas[fila][columna] == CELDA_APARICION_ENEMIGO:
                    self.enemigos.append(Enemy(fila, columna))
                    
        self.pausado = False
        self.game_over = False
        self.estado = "jugando"

    def cargar_nivel(self, ruta: str) -> None:
        """Carga un nivel y reposiciona entidades."""
        self.ruta_nivel_actual = ruta
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
                if self.game_over or self.estado == "ganaste":
                    continue
                    
                if evento.key == pygame.K_ESCAPE or evento.key == pygame.K_p:
                    self.pausado = not self.pausado
                elif evento.key == pygame.K_F1:
                    self.modo_debug = not self.modo_debug
                elif not self.pausado and evento.key in (pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d):
                    teclas = pygame.key.get_pressed()
                    self.jugador.manejar_teclas(teclas, self.cuadricula.grafo)
                    
            elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                # 1. Gestionar clicks en la pantalla Game Over
                if self.estado == "ganaste":
                    accion = self._manejar_click_ganaste(evento.pos)
                    if accion == "reiniciar":
                        if self.ruta_nivel_actual:
                            self.cargar_nivel(self.ruta_nivel_actual)
                        else:
                            self.reiniciar_nivel()
                    elif accion == "menu":
                        self.en_ejecucion = False
                    elif accion == "salir":
                        pygame.quit()
                        sys.exit()
                elif self.game_over:
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
                        
                # 3. Gestionar clicks en el juego (Movimiento)
                else:
                    self.jugador.establecer_destino_click(
                        evento.pos,
                        self.cuadricula.grafo,
                        offset_x=self.offset_x,
                    )

    def actualizar(self) -> None:
        """Actualiza los objetos del juego en cada fotograma."""
        # Detener la lógica si está pausado o el jugador murió
        if self.pausado or self.game_over or self.estado == "ganaste":
            return
            
        # --- NUEVO: Guardar la posición antes de mover ---
        pos_x_anterior = self.jugador.x
        pos_y_anterior = self.jugador.y
        # ------------------------------------------------

        self.jugador.actualizar()

        # --- NUEVO: Detectar dirección y movimiento según el cambio de coordenadas ---
        dx = self.jugador.x - pos_x_anterior
        dy = self.jugador.y - pos_y_anterior
        
        if dx > 0:
            self.orientacion_actual = self.DIR_DERECHA
        elif dx < 0:
            self.orientacion_actual = self.DIR_IZQUIERDA
        elif dy > 0:
            self.orientacion_actual = self.DIR_ABAJO
        elif dy < 0:
            self.orientacion_actual = self.DIR_ARRIBA
            
        # Si la posición cambió en X o Y, significa que se está moviendo
        self.esta_moviendose = (dx != 0 or dy != 0)
        # -----------------------------------------------------------------------------

        if (
            self.cuadricula.spawn_meta
            and (self.jugador.fila, self.jugador.columna) == self.cuadricula.spawn_meta
        ):
            self.estado = "ganaste"
            return
            
        for enemigo in self.enemigos:
            enemigo.actualizar(
                self.cuadricula, 
                (self.jugador.fila, self.jugador.columna),
                self.algoritmo_enemigo
            )
            # Evaluar colisiones de derrota (Si están a menos de media celda)
            distancia_x = abs(self.jugador.x - enemigo.x)
            distancia_y = abs(self.jugador.y - enemigo.y)
            if distancia_x < (TAMANO_CELDA // 2) and distancia_y < (TAMANO_CELDA // 2):
                self.game_over = True

    def _dibujar_rutas_enemigos(self) -> None:
        """Dibuja una línea simple indicando el camino del enemigo hacia el jugador."""
        for enemigo in self.enemigos:
            if not enemigo.ruta:
                continue
            
            # 1. Crear una lista de puntos (en coordenadas de píxeles)
            puntos = []
            
            # El primer punto es el centro actual del enemigo
            punto_inicial_x = enemigo.x + self.offset_x
            punto_inicial_y = enemigo.y
            puntos.append((punto_inicial_x, punto_inicial_y))
            
            # 2. Añadir los centros de todas las celdas de la ruta pendiente
            for fila, columna in enemigo.ruta:
                centro_x = (columna * TAMANO_CELDA) + (TAMANO_CELDA // 2) + self.offset_x
                centro_y = (fila * TAMANO_CELDA) + (TAMANO_CELDA // 2)
                puntos.append((centro_x, centro_y))
                
            # 3. Dibujar la línea (solo si hay al menos 2 puntos)
            if len(puntos) >= 2:
                # Dibuja líneas continuas. False indica que no se debe cerrar el polígono.
                # El "3" al final es el grosor de la línea.
                pygame.draw.lines(self.pantalla, enemigo.color, False, puntos, 3)



    def dibujar(self) -> None:
        """Dibuja la escena del juego en la ventana."""
        self.pantalla.fill(COLOR_FONDO)
        self.cuadricula.dibujar(self.pantalla, offset_x=self.offset_x)
        
        # --- MODIFICACIÓN: Renderizar Sprite Animado en lugar de la bolita ---
        if getattr(self, 'animaciones', None) and self.orientacion_actual in self.animaciones:
            frames_direccion = self.animaciones[self.orientacion_actual]
            
            if self.esta_moviendose:
                # El reloj de pygame nos da el tiempo exacto en milisegundos desde el último frame
                self.timer_animacion += self.reloj.get_time() 
                if self.timer_animacion > self.velocidad_animacion:
                    self.indice_frame_actual = (self.indice_frame_actual + 1) % len(frames_direccion)
                    self.timer_animacion = 0
            else:
                self.indice_frame_actual = 0 # Volver al frame 0 (quieto) si no hay movimiento
                
            imagen_final = frames_direccion[self.indice_frame_actual]
            posicion_pantalla = (
                self.offset_x + self.jugador.x - TAMANO_CELDA // 2,
                self.jugador.y - TAMANO_CELDA // 2
            )
            self.pantalla.blit(imagen_final, posicion_pantalla)
        else:
            # Respaldo de seguridad por si el archivo .png no se encontró
            self.jugador.dibujar(self.pantalla, offset_x=self.offset_x)
        # ----------------------------------------------------------------------
        
        # Dibujar los enemigos actuales en pantalla
        for enemigo in self.enemigos:
            enemigo.dibujar(self.pantalla, offset_x=self.offset_x)
            
        if self.modo_debug:
            self._dibujar_debug_bfs()
            
        if self.visualizar_recorrido:
            self._dibujar_rutas_enemigos()
            
        # Dibujar interfaces por encima del juego
        if self.estado == "ganaste":
            self._dibujar_pantalla_ganaste()
        elif self.game_over:
            self.menu_game_over.dibujar()
        elif self.pausado:
            self.menu_pausa.dibujar()
            
        pygame.display.flip()

    def _dibujar_debug_bfs(self) -> None:
        """Dibuja los nodos visitados y la ruta BFS."""
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

    def _dibujar_pantalla_ganaste(self) -> None:
        """Dibuja la pantalla de victoria con botones interactivos."""
        superficie = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        superficie.fill((255, 220, 80, 160))
        self.pantalla.blit(superficie, (0, 0))

        texto = self.fuente_ganaste_titulo.render("¡Ganaste!", True, (80, 60, 10))
        rect_texto = texto.get_rect()
        ancho_boton = 260
        alto_boton = 50
        espaciado_boton = 12
        alto_botones = alto_boton * 3 + espaciado_boton * 2
        alto_grupo = rect_texto.height + 24 + alto_botones
        inicio_y = (ALTO - alto_grupo) // 2
        rect_texto.centerx = ANCHO // 2
        rect_texto.top = inicio_y
        self.pantalla.blit(texto, rect_texto)

        x_botones = ANCHO // 2 - ancho_boton // 2
        y_botones = rect_texto.bottom + 24
        for indice, boton in enumerate(self.botones_ganaste):
            rect_boton = pygame.Rect(
                x_botones,
                y_botones + indice * (alto_boton + espaciado_boton),
                ancho_boton,
                alto_boton,
            )
            boton["rect"] = rect_boton

        posicion_mouse = pygame.mouse.get_pos()
        for boton in self.botones_ganaste:
            color_actual = boton["color"]
            if boton["rect"].collidepoint(posicion_mouse):
                color_actual = (
                    min(color_actual[0] + 40, 255),
                    min(color_actual[1] + 40, 255),
                    min(color_actual[2] + 40, 255),
                )
            pygame.draw.rect(self.pantalla, color_actual, boton["rect"], border_radius=8)
            texto_boton = self.fuente_ganaste_boton.render(
                boton["texto"], True, (255, 255, 255)
            )
            rect_texto_boton = texto_boton.get_rect(center=boton["rect"].center)
            self.pantalla.blit(texto_boton, rect_texto_boton)

    def _manejar_click_ganaste(self, posicion: tuple[int, int]) -> str | None:
        """Devuelve la acción del botón clickeado en la victoria."""
        for boton in self.botones_ganaste:
            if boton["rect"].collidepoint(posicion):
                return str(boton["accion"])
        return None