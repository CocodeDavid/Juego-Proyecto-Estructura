"""Editor de niveles para mapas en cuadrícula."""

import json

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
    NOMBRE_NIVEL,
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
        self.fuente_barra = pygame.font.SysFont(None, 16)
        self.fuente_botones_barra = pygame.font.SysFont(None, 16)
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
            elif evento.type == pygame.KEYDOWN:
                self._manejar_teclas_barra(evento.key)
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                self.manejar_click_mouse(evento.button, evento.pos)

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
        self._establecer_celda(fila, columna, CELDA_SUELO)

    def _establecer_celda(self, fila: int, columna: int, valor: int) -> None:
        """Asigna el valor de una baldosa en la cuadrícula."""
        self.cuadricula.celdas[fila][columna] = valor

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
        pygame.display.flip()

    def guardar_a_json(self, ruta: str) -> None:
        """Guarda la cuadrícula y apariciones en un archivo JSON."""
        aparicion_jugador, apariciones_enemigo = self._buscar_apariciones()
        datos_nivel = {
            "name": NOMBRE_NIVEL,
            "rows": self.cuadricula.filas,
            "cols": self.cuadricula.columnas,
            "tiles": self.cuadricula.celdas,
            "player_spawn": aparicion_jugador,
            "enemy_spawns": apariciones_enemigo,
        }
        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(datos_nivel, archivo, indent=2, ensure_ascii=False)

    def guardar(self) -> None:
        """Muestra un mensaje de guardado pendiente."""
        print("Guardar: funcionalidad pendiente")

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
            pygame.draw.rect(self.pantalla, boton["color"], rect)
            texto = self.fuente_botones_barra.render(
                boton["texto"], True, COLOR_TEXTO_BARRA
            )
            rect_texto = texto.get_rect(center=rect.center)
            self.pantalla.blit(texto, rect_texto)

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
