"""Editor de niveles para mapas en cuadrícula."""

import json
import string
from pathlib import Path

import pygame

from settings import (
    ALTO,
    ANCHO,
    APARICION_JUGADOR_POR_DEFECTO,
    CELDA_APARICION_ENEMIGO,
    CELDA_APARICION_JUGADOR,
    CELDA_MURO,
    CELDA_SUELO,
    COLOR_APARICION_ENEMIGO,
    COLOR_APARICION_JUGADOR,
    COLOR_FONDO,
    COLOR_MURO,
    COLOR_REJILLA,
    COLOR_SUELO,
    COLUMNAS,
    FILAS,
    FOTOGRAMAS_POR_SEGUNDO,
    TAMANO_CELDA,
    TIPO_ENEMIGO_BASICO,
    TITULO_EDITOR,
    TITULO_VENTANA,
)
from src.grid import Grid

ANCHO_BARRA_HERRAMIENTAS = 160
ANCHO_BOTON_MATERIAL = 140
ALTO_BOTON_MATERIAL = 48
ESPACIADO_BOTONES_MATERIAL = 8
ALTO_BOTON_ACCION = 44
ESPACIADO_BOTONES_ACCION = 8
MARGEN_SUPERIOR_BARRA = 12
MARGEN_INFERIOR_ACCIONES = 16
MARGEN_LATERAL_BOTON = (ANCHO_BARRA_HERRAMIENTAS - ANCHO_BOTON_MATERIAL) // 2
TAMANO_COLOR_MATERIAL = 24

COLOR_BARRA_HERRAMIENTAS = (30, 30, 40)
COLOR_TEXTO_BARRA = (255, 255, 255)
COLOR_BOTON_MATERIAL = (45, 45, 60)
COLOR_BORDE_SELECCION = (255, 255, 255)
COLOR_BOTON_GUARDAR = (60, 100, 160)
COLOR_BOTON_VOLVER = (80, 60, 60)


class LevelEditor:
    """Editor de niveles basado en cuadrícula."""

    def __init__(self) -> None:
        """Inicializa el editor y sus atributos principales."""
        pygame.init()
        self.pantalla = pygame.display.set_mode(
            (ANCHO + ANCHO_BARRA_HERRAMIENTAS, ALTO)
        )
        pygame.display.set_caption(TITULO_EDITOR)
        self.reloj = pygame.time.Clock()
        self.cuadricula = Grid(FILAS, COLUMNAS, TAMANO_CELDA)
        self.baldosa_seleccionada = CELDA_MURO
        self.en_ejecucion = False
        self.ancho_barra_herramientas = ANCHO_BARRA_HERRAMIENTAS
        self.fuente_barra = pygame.font.SysFont(None, 18)
        self.fuente_botones_barra = pygame.font.SysFont(None, 18)
        self.materiales = [
            {"valor": CELDA_SUELO, "nombre": "Suelo", "color": (50, 50, 50)},
            {"valor": CELDA_MURO, "nombre": "Pared", "color": (100, 80, 60)},
            {
                "valor": CELDA_APARICION_JUGADOR,
                "nombre": "Spawn Jugador",
                "color": (50, 180, 80),
            },
            {
                "valor": CELDA_APARICION_ENEMIGO,
                "nombre": "Spawn Enemigo",
                "color": (180, 60, 60),
            },
        ]
        
        self.aparicion_jugador = {
            "fila": APARICION_JUGADOR_POR_DEFECTO[0],
            "columna": APARICION_JUGADOR_POR_DEFECTO[1],
        }

        self._establecer_celda(
            self.aparicion_jugador["fila"],
            self.aparicion_jugador["columna"],
            CELDA_APARICION_JUGADOR,
        )

        # Atributos para el diálogo de guardado
        self.mostrando_dialogo_guardar = False
        self.nombre_nivel_input = ""
        self.btn_dialogo_guardar = pygame.Rect(0, 0, 0, 0)
        self.btn_dialogo_cancelar = pygame.Rect(0, 0, 0, 0)

    def ejecutar(self) -> None:
        """Ejecuta la pantalla del editor."""
        self.en_ejecucion = True
        while self.en_ejecucion:
            self.manejar_eventos()
            self._dibujar()
            self.reloj.tick(FOTOGRAMAS_POR_SEGUNDO)
        self._restablecer_ventana_menu()

    def manejar_eventos(self) -> None:
        """Maneja clicks y teclas del usuario dentro del editor."""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self._volver_al_menu()
            # Si el diálogo de guardado está abierto, bloqueamos el resto de acciones
            elif self.mostrando_dialogo_guardar:
                self._manejar_eventos_dialogo(evento)
            elif evento.type == pygame.KEYDOWN:
                self._manejar_teclas_barra(evento.key)
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                self.manejar_click_mouse(evento.button, evento.pos)
                
    def _manejar_eventos_dialogo(self, evento: pygame.event.Event) -> None:
        """Procesa eventos cuando la mini ventana de guardado está activa."""
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                self.mostrando_dialogo_guardar = False
            elif evento.key == pygame.K_RETURN:
                if self.nombre_nivel_input.strip():
                    self._ejecutar_guardado()
            elif evento.key == pygame.K_BACKSPACE:
                self.nombre_nivel_input = self.nombre_nivel_input[:-1]
            else:
                # Escribir solo caracteres imprimibles (hasta 20 caracteres)
                if len(self.nombre_nivel_input) < 20 and evento.unicode.isprintable():
                    self.nombre_nivel_input += evento.unicode
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.btn_dialogo_guardar.collidepoint(evento.pos):
                if self.nombre_nivel_input.strip():
                    self._ejecutar_guardado()
            elif self.btn_dialogo_cancelar.collidepoint(evento.pos):
                self.mostrando_dialogo_guardar = False

    def _manejar_teclas_barra(self, tecla: int) -> None:
        """Actualiza la baldosa seleccionada según el teclado."""
        if tecla == pygame.K_1:
            self.baldosa_seleccionada = CELDA_SUELO
        elif tecla == pygame.K_2:
            self.baldosa_seleccionada = CELDA_MURO
        elif tecla == pygame.K_3:
            self.baldosa_seleccionada = CELDA_APARICION_JUGADOR
        elif tecla == pygame.K_4:
            self.baldosa_seleccionada = CELDA_APARICION_ENEMIGO

    def manejar_click_mouse(self, boton: int, posicion: tuple[int, int]) -> None:
        """Pinta o borra baldosas según el botón presionado."""
        if posicion[0] < self.ancho_barra_herramientas:
            self._manejar_click_barra(posicion)
            return
            
        fila = posicion[1] // TAMANO_CELDA
        columna = (posicion[0] - self.ancho_barra_herramientas) // TAMANO_CELDA
        
        if (
            fila < 0
            or columna < 0
            or fila >= self.cuadricula.filas
            or columna >= self.cuadricula.columnas
        ):
            return
            
        # Click izquierdo pinta. Click derecho borra
        if boton == 1:
            self._pintar_celda(fila, columna)
        elif boton == 3:
            self._borrar_celda(fila, columna)

    def _pintar_celda(self, fila: int, columna: int) -> None:
        """Pinta la baldosa seleccionada en la cuadrícula."""
        if self.baldosa_seleccionada == CELDA_APARICION_JUGADOR:
            self._establecer_celda(
                self.aparicion_jugador["fila"],
                self.aparicion_jugador["columna"],
                CELDA_SUELO,
            )
            self.aparicion_jugador = {"fila": fila, "columna": columna}
        self._establecer_celda(fila, columna, self.baldosa_seleccionada)

    def _borrar_celda(self, fila: int, columna: int) -> None:
        """Borra una baldosa y reinicia apariciones si corresponde."""
        if self.cuadricula.celdas[fila][columna] == CELDA_APARICION_JUGADOR:
            self.aparicion_jugador = {
                "fila": APARICION_JUGADOR_POR_DEFECTO[0],
                "columna": APARICION_JUGADOR_POR_DEFECTO[1],
            }
            # Restaurar el spawn default
            self._establecer_celda(
                self.aparicion_jugador["fila"],
                self.aparicion_jugador["columna"],
                CELDA_APARICION_JUGADOR,
            )
        self._establecer_celda(fila, columna, CELDA_SUELO)

    def _establecer_celda(self, fila: int, columna: int, valor: int) -> None:
        """Asigna el valor de una baldosa en la cuadrícula."""
        self.cuadricula.celdas[fila][columna] = valor

    def borrar_todo(self) -> None:
        """Borra toda la cuadrícula y restaura las apariciones."""
        for fila in range(self.cuadricula.filas):
            for columna in range(self.cuadricula.columnas):
                self.cuadricula.celdas[fila][columna] = CELDA_SUELO
                
        self.aparicion_jugador = {
            "fila": APARICION_JUGADOR_POR_DEFECTO[0],
            "columna": APARICION_JUGADOR_POR_DEFECTO[1],
        }
        self._establecer_celda(
            self.aparicion_jugador["fila"],
            self.aparicion_jugador["columna"],
            CELDA_APARICION_JUGADOR,
        )

    def _buscar_apariciones(
        self,
    ) -> tuple[dict[str, int], list[dict[str, int | str]]]:
        """Escanea la cuadrícula para localizar apariciones."""
        aparicion_jugador = self.aparicion_jugador
        apariciones_enemigo: list[dict[str, int | str]] = []
        for fila in range(self.cuadricula.filas):
            for columna in range(self.cuadricula.columnas):
                baldosa = self.cuadricula.celdas[fila][columna]
                if baldosa == CELDA_APARICION_JUGADOR:
                    aparicion_jugador = {"fila": fila, "columna": columna}
                elif baldosa == CELDA_APARICION_ENEMIGO:
                    apariciones_enemigo.append(
                        {"fila": fila, "columna": columna, "tipo": TIPO_ENEMIGO_BASICO}
                    )
        return aparicion_jugador, apariciones_enemigo

    def _dibujar(self) -> None:
        """Dibuja la cuadrícula y las baldosas del editor."""
        self.pantalla.fill(COLOR_FONDO)
        self._dibujar_barra_herramientas()
        
        for fila, fila_baldosas in enumerate(self.cuadricula.celdas):
            for columna, baldosa in enumerate(fila_baldosas):
                if baldosa == CELDA_MURO:
                    color = COLOR_MURO
                elif baldosa == CELDA_APARICION_JUGADOR:
                    color = COLOR_APARICION_JUGADOR
                elif baldosa == CELDA_APARICION_ENEMIGO:
                    color = COLOR_APARICION_ENEMIGO
                else:
                    color = COLOR_SUELO
                    
                rectangulo = pygame.Rect(
                    self.ancho_barra_herramientas + columna * TAMANO_CELDA,
                    fila * TAMANO_CELDA,
                    TAMANO_CELDA,
                    TAMANO_CELDA,
                )
                pygame.draw.rect(self.pantalla, color, rectangulo)
                pygame.draw.rect(self.pantalla, COLOR_REJILLA, rectangulo, 1)
                
        # Dibuja la mini-ventana superpuesta si corresponde
        if self.mostrando_dialogo_guardar:
            self._dibujar_dialogo_guardar()
            
        pygame.display.flip()

    def guardar(self) -> None:
        """Abre la interfaz de guardado."""
        self.mostrando_dialogo_guardar = True
        self.nombre_nivel_input = ""

    def _ejecutar_guardado(self) -> None:
        """Escribe el nivel en un archivo .json y limpia la grilla."""
        nombre_original = self.nombre_nivel_input.strip()
        if not nombre_original:
            nombre_original = "Nivel Nuevo"
            
        # Sanitizar el nombre para convertirlo en un archivo válido
        caracteres_validos = "-_.() %s%s" % (string.ascii_letters, string.digits)
        nombre_archivo = "".join(c for c in nombre_original if c in caracteres_validos)
        nombre_archivo = nombre_archivo.replace(" ", "_").lower()
        if not nombre_archivo:
            nombre_archivo = "nivel_nuevo"
            
        nombre_archivo += ".json"
        
        # Encontrar la carpeta de niveles
        ruta_base = Path(__file__).resolve().parents[1]
        ruta_niveles = ruta_base / "levels"
        ruta_niveles.mkdir(exist_ok=True)
        ruta_completa = ruta_niveles / nombre_archivo

        aparicion_jugador, apariciones_enemigo = self._buscar_apariciones()
        
        datos_nivel = {
            "name": nombre_original,
            "rows": self.cuadricula.filas,
            "cols": self.cuadricula.columnas,
            "tiles": self.cuadricula.celdas,
            "player_spawn": aparicion_jugador,
            "enemy_spawns": apariciones_enemigo,
        }
        
        # Guardado en disco
        with open(ruta_completa, "w", encoding="utf-8") as archivo:
            json.dump(datos_nivel, archivo, indent=2, ensure_ascii=False)
            
        # Ocultar el diálogo y borrar todo para seguir editando
        self.mostrando_dialogo_guardar = False
        self.borrar_todo()

    def _volver_al_menu(self) -> None:
        """Solicita el cierre del editor y regreso al menú."""
        self.en_ejecucion = False

    def _restablecer_ventana_menu(self) -> None:
        """Restablece la ventana principal antes de volver al menú."""
        pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption(TITULO_VENTANA)

    def _obtener_botones_materiales(self) -> list[dict[str, object]]:
        """Devuelve la configuración visual de los botones de materiales."""
        botones: list[dict[str, object]] = []
        titulo = self.fuente_barra.render("Materiales", True, COLOR_TEXTO_BARRA)
        inicio_y = titulo.get_rect().height + MARGEN_SUPERIOR_BARRA + 16
        for indice, material in enumerate(self.materiales):
            y = inicio_y + indice * (ALTO_BOTON_MATERIAL + ESPACIADO_BOTONES_MATERIAL)
            rect = pygame.Rect(
                MARGEN_LATERAL_BOTON,
                y,
                ANCHO_BOTON_MATERIAL,
                ALTO_BOTON_MATERIAL,
            )
            botones.append({"rect": rect, **material})
        return botones

    def _obtener_botones_accion(self) -> list[dict[str, object]]:
        """Devuelve los botones de acción de la barra de herramientas."""
        botones: list[dict[str, object]] = []
        
        y_volver = ALTO - MARGEN_INFERIOR_ACCIONES - ALTO_BOTON_ACCION
        y_guardar = y_volver - ESPACIADO_BOTONES_ACCION - ALTO_BOTON_ACCION
        y_borrar = y_guardar - ESPACIADO_BOTONES_ACCION - ALTO_BOTON_ACCION
        
        botones.append(
            {
                "rect": pygame.Rect(
                    MARGEN_LATERAL_BOTON,
                    y_borrar,
                    ANCHO_BOTON_MATERIAL,
                    ALTO_BOTON_ACCION,
                ),
                "texto": "Borrar todo",
                "color": (160, 60, 60),
                "accion": self.borrar_todo,
            }
        )
        botones.append(
            {
                "rect": pygame.Rect(
                    MARGEN_LATERAL_BOTON,
                    y_guardar,
                    ANCHO_BOTON_MATERIAL,
                    ALTO_BOTON_ACCION,
                ),
                "texto": "Guardar",
                "color": COLOR_BOTON_GUARDAR,
                "accion": self.guardar,
            }
        )
        botones.append(
            {
                "rect": pygame.Rect(
                    MARGEN_LATERAL_BOTON,
                    y_volver,
                    ANCHO_BOTON_MATERIAL,
                    ALTO_BOTON_ACCION,
                ),
                "texto": "Volver al menú",
                "color": COLOR_BOTON_VOLVER,
                "accion": self._volver_al_menu,
            }
        )
        return botones

    def _dibujar_barra_herramientas(self) -> None:
        """Dibuja la barra lateral del editor con botones y acciones."""
        pygame.draw.rect(
            self.pantalla,
            COLOR_BARRA_HERRAMIENTAS,
            pygame.Rect(0, 0, self.ancho_barra_herramientas, ALTO),
        )
        titulo = self.fuente_barra.render("Materiales", True, COLOR_TEXTO_BARRA)
        rect_titulo = titulo.get_rect(
            midtop=(self.ancho_barra_herramientas // 2, MARGEN_SUPERIOR_BARRA)
        )
        self.pantalla.blit(titulo, rect_titulo)

        for boton in self._obtener_botones_materiales():
            rect = boton["rect"]
            pygame.draw.rect(self.pantalla, COLOR_BOTON_MATERIAL, rect)
            if boton["valor"] == self.baldosa_seleccionada:
                pygame.draw.rect(self.pantalla, COLOR_BORDE_SELECCION, rect, 2)

            cuadrado_color = pygame.Rect(
                rect.left + 8,
                rect.centery - TAMANO_COLOR_MATERIAL // 2,
                TAMANO_COLOR_MATERIAL,
                TAMANO_COLOR_MATERIAL,
            )
            pygame.draw.rect(self.pantalla, boton["color"], cuadrado_color)
            texto = self.fuente_botones_barra.render(
                boton["nombre"], True, COLOR_TEXTO_BARRA
            )
            rect_texto = texto.get_rect()
            rect_texto.midleft = (
                cuadrado_color.right + 8,
                rect.centery,
            )
            self.pantalla.blit(texto, rect_texto)

        for boton in self._obtener_botones_accion():
            rect = boton["rect"]
            pygame.draw.rect(self.pantalla, boton["color"], rect, border_radius=4)
            texto = self.fuente_botones_barra.render(
                boton["texto"], True, COLOR_TEXTO_BARRA
            )
            rect_texto = texto.get_rect(center=rect.center)
            self.pantalla.blit(texto, rect_texto)

    def _dibujar_dialogo_guardar(self) -> None:
        """Dibuja la mini ventana emergente para pedir el nombre del nivel."""
        ancho_dialogo = 400
        alto_dialogo = 200
        x = (ANCHO + self.ancho_barra_herramientas - ancho_dialogo) // 2
        y = (ALTO - alto_dialogo) // 2
        rect_dialogo = pygame.Rect(x, y, ancho_dialogo, alto_dialogo)
        
        # Fondo oscuro semi-transparente
        superficie_oscura = pygame.Surface((ANCHO + self.ancho_barra_herramientas, ALTO), pygame.SRCALPHA)
        superficie_oscura.fill((0, 0, 0, 160))
        self.pantalla.blit(superficie_oscura, (0, 0))
        
        # Fondo diálogo
        pygame.draw.rect(self.pantalla, (45, 45, 55), rect_dialogo, border_radius=8)
        pygame.draw.rect(self.pantalla, (200, 200, 200), rect_dialogo, 2, border_radius=8)
        
        # Texto Título
        fuente_titulo = pygame.font.SysFont(None, 36)
        titulo = fuente_titulo.render("Guardar Nivel", True, (255, 255, 255))
        self.pantalla.blit(titulo, (x + 20, y + 20))
        
        # Input Text
        rect_input = pygame.Rect(x + 20, y + 70, ancho_dialogo - 40, 40)
        pygame.draw.rect(self.pantalla, (20, 20, 25), rect_input)
        pygame.draw.rect(self.pantalla, (100, 100, 120), rect_input, 2)
        
        fuente_input = pygame.font.SysFont(None, 28)
        # Efecto de guion parpadeante simulando cursor
        texto_render = self.nombre_nivel_input + ("_" if pygame.time.get_ticks() % 1000 < 500 else "")
        texto_input = fuente_input.render(texto_render, True, (255, 255, 255))
        self.pantalla.blit(texto_input, (rect_input.x + 10, rect_input.y + 10))
        
        # Botones de la mini ventana
        self.btn_dialogo_cancelar = pygame.Rect(x + 30, y + 135, 140, 40)
        self.btn_dialogo_guardar = pygame.Rect(x + 230, y + 135, 140, 40)
        
        pygame.draw.rect(self.pantalla, (180, 60, 60), self.btn_dialogo_cancelar, border_radius=5)
        pygame.draw.rect(self.pantalla, (60, 160, 80), self.btn_dialogo_guardar, border_radius=5)
        
        texto_cancelar = fuente_input.render("Cancelar", True, (255, 255, 255))
        texto_guardar = fuente_input.render("Guardar", True, (255, 255, 255))
        
        self.pantalla.blit(texto_cancelar, texto_cancelar.get_rect(center=self.btn_dialogo_cancelar.center))
        self.pantalla.blit(texto_guardar, texto_guardar.get_rect(center=self.btn_dialogo_guardar.center))

    def _manejar_click_barra(self, posicion: tuple[int, int]) -> None:
        """Gestiona los clicks dentro de la barra de herramientas."""
        for boton in self._obtener_botones_materiales():
            if boton["rect"].collidepoint(posicion):
                self.baldosa_seleccionada = int(boton["valor"])
                return
        for boton in self._obtener_botones_accion():
            if boton["rect"].collidepoint(posicion):
                boton["accion"]()
                return

def principal() -> None:
    """Lanza el editor de niveles."""
    editor = LevelEditor()
    editor.ejecutar()


if __name__ == "__main__":
    principal()