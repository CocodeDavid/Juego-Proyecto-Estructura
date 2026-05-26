"""Representación de la cuadrícula y utilidades."""

import json

from settings import CELDA_MURO, CELDA_SUELO


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
        self.filas = datos["rows"]
        self.columnas = datos["cols"]
        self.celdas = datos["tiles"]

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
