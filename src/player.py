"""Lógica de la entidad del jugador."""

from src.pathfinding import a_estrella


class Player:
    """Representa al personaje controlado por el jugador."""

    def __init__(self, posicion: tuple[int, int]) -> None:
        """Inicializa el jugador en una posición de píxeles."""
        self.posicion = posicion
        self.ruta: list[tuple[int, int]] = []
        self.conjunto_abierto: set[tuple[int, int]] = set()
        self.conjunto_cerrado: set[tuple[int, int]] = set()

    def establecer_destino(self, cuadricula, celda_objetivo: tuple[int, int]) -> None:
        """Calcula una ruta hacia la celda objetivo y la almacena."""
        celda_inicio = cuadricula.pixel_a_celda(*self.posicion)
        ruta, conjunto_abierto, conjunto_cerrado = a_estrella(
            cuadricula, celda_inicio, celda_objetivo
        )
        self.ruta = ruta
        self.conjunto_abierto = conjunto_abierto
        self.conjunto_cerrado = conjunto_cerrado

    def actualizar(self, cuadricula) -> None:
        """Avanza un paso por la ruta en cada fotograma."""
        if not self.ruta:
            return
        siguiente_celda = self.ruta.pop(0)
        self.posicion = cuadricula.celda_a_pixel_centro(*siguiente_celda)
