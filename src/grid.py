"""Representación de la cuadrícula y utilidades."""

import json

import pygame

from settings import (
    CELDA_APARICION_ENEMIGO,
    CELDA_APARICION_JUGADOR,
    CELDA_MURO,
    CELDA_SUELO,
)


class Grid:
    """Representa una cuadrícula 2D de baldosas para el mundo del juego."""

    def __init__(self, filas: int, columnas: int, tamano_celda: int) -> None:
        """Inicializa la cuadrícula con baldosas de suelo."""
        self.filas = filas
        self.columnas = columnas
        self.tamano_celda = tamano_celda
        self.celdas = [[CELDA_SUELO for _ in range(columnas)] for _ in range(filas)]

    def cargar_desde_json(self, ruta: str) -> None:
        """Carga las baldosas desde un archivo JSON de nivel."""
        with open(ruta, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        filas = datos.get("rows")
        columnas = datos.get("cols")
        if (
            not isinstance(filas, int)
            or not isinstance(columnas, int)
            or filas <= 0
            or columnas <= 0
        ):
            print(
                "Error al cargar nivel: dimensiones inválidas. Se generó un perímetro de muros."
            )
            self._rellenar_perimetro_muros()
            return
        self.filas = filas
        self.columnas = columnas
        baldosas = datos.get("tiles")
        if not self._validar_baldosas(baldosas):
            print(
                "Error al cargar nivel: la cuadrícula no coincide con las dimensiones o está vacía. Se generó un perímetro de muros."
            )
            self._rellenar_perimetro_muros()
            return
        self.celdas = baldosas

    def _validar_baldosas(self, baldosas: object) -> bool:
        """Valida la estructura y el contenido de las baldosas cargadas."""
        if not isinstance(baldosas, list) or len(baldosas) != self.filas:
            return False
        tiene_valor = False
        for fila in baldosas:
            if not isinstance(fila, list) or len(fila) != self.columnas:
                return False
            for valor in fila:
                if not isinstance(valor, int):
                    return False
                if valor != 0:
                    tiene_valor = True
        return tiene_valor

    def _rellenar_perimetro_muros(self) -> None:
        """Rellena la cuadrícula con suelo y muros en el perímetro."""
        self.celdas = [
            [CELDA_SUELO for _ in range(self.columnas)] for _ in range(self.filas)
        ]
        if self.filas == 0 or self.columnas == 0:
            return
        for columna in range(self.columnas):
            self.celdas[0][columna] = CELDA_MURO
            self.celdas[self.filas - 1][columna] = CELDA_MURO
        for fila in range(self.filas):
            self.celdas[fila][0] = CELDA_MURO
            self.celdas[fila][self.columnas - 1] = CELDA_MURO

    def dibujar(self, pantalla: pygame.Surface) -> None:
        """Dibuja la cuadrícula en la superficie indicada."""
        colores = {
            CELDA_SUELO: (50, 50, 50),
            CELDA_MURO: (100, 80, 60),
            CELDA_APARICION_JUGADOR: (50, 180, 80),
            CELDA_APARICION_ENEMIGO: (180, 60, 60),
        }
        for fila in range(self.filas):
            for columna in range(self.columnas):
                valor = self.celdas[fila][columna]
                color = colores.get(valor, colores[CELDA_SUELO])
                rectangulo = pygame.Rect(
                    columna * self.tamano_celda,
                    fila * self.tamano_celda,
                    self.tamano_celda,
                    self.tamano_celda,
                )
                pygame.draw.rect(pantalla, color, rectangulo)

    def es_transitable(self, fila: int, columna: int) -> bool:
        """Devuelve True si la celda está dentro de los límites y no es muro."""
        if fila < 0 or columna < 0 or fila >= self.filas or columna >= self.columnas:
            return False
        return self.celdas[fila][columna] != CELDA_MURO

    def obtener_vecinos(self, fila: int, columna: int) -> list[tuple[int, int]]:
        """Devuelve vecinos transitables en las 4 direcciones."""
        vecinos: list[tuple[int, int]] = []
        for delta_fila, delta_columna in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            fila_siguiente = fila + delta_fila
            columna_siguiente = columna + delta_columna
            if self.es_transitable(fila_siguiente, columna_siguiente):
                vecinos.append((fila_siguiente, columna_siguiente))
        return vecinos

    def pixel_a_celda(self, x: int, y: int) -> tuple[int, int]:
        """Convierte coordenadas de píxeles a coordenadas de celda."""
        return (y // self.tamano_celda, x // self.tamano_celda)

    def celda_a_pixel_centro(self, fila: int, columna: int) -> tuple[int, int]:
        """Devuelve las coordenadas del centro de una celda en píxeles."""
        centro_x = columna * self.tamano_celda + self.tamano_celda // 2
        centro_y = fila * self.tamano_celda + self.tamano_celda // 2
        return (centro_x, centro_y)
