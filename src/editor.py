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
)
from src.grid import Grid


class LevelEditor:
    """Editor de niveles basado en cuadrícula."""

    def __init__(self) -> None:
        """Inicializa el editor y sus atributos principales."""
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption(TITULO_EDITOR)
        self.reloj = pygame.time.Clock()
        self.cuadricula = Grid(FILAS, COLUMNAS, TAMANO_CELDA)
        self.baldosa_seleccionada = CELDA_MURO
        self.en_ejecucion = False
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
        pygame.quit()

    def manejar_eventos(self) -> None:
        """Maneja clicks y teclas del usuario dentro del editor."""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.en_ejecucion = False
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
        fila = posicion[1] // TAMANO_CELDA
        columna = posicion[0] // TAMANO_CELDA
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
                    columna * TAMANO_CELDA,
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


def principal() -> None:
    """Lanza el editor de niveles."""
    editor = LevelEditor()
    editor.ejecutar()


if __name__ == "__main__":
    principal()
