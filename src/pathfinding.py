"""Algoritmos de búsqueda para navegación en cuadrículas."""

import heapq
from collections import deque
from itertools import count


def heuristica(celda_a: tuple[int, int], celda_b: tuple[int, int]) -> int:
    """Devuelve la distancia Manhattan entre dos celdas."""
    return abs(celda_a[0] - celda_b[0]) + abs(celda_a[1] - celda_b[1])


def a_estrella(
    cuadricula,
    inicio: tuple[int, int],
    objetivo: tuple[int, int],
) -> tuple[list[tuple[int, int]], set[tuple[int, int]], set[tuple[int, int]]]:
    """Calcula una ruta A* y devuelve ruta, abiertos y cerrados."""
    if not cuadricula.es_transitable(*inicio) or not cuadricula.es_transitable(*objetivo):
        return ([], set(), set())

    frontera: list[tuple[int, int, tuple[int, int]]] = []
    contador = count()
    heapq.heappush(frontera, (0, next(contador), inicio))

    viene_de: dict[tuple[int, int], tuple[int, int] | None] = {inicio: None}
    costo_g = {inicio: 0}
    nodos_abiertos = {inicio}
    nodos_cerrados: set[tuple[int, int]] = set()

    while frontera:
        _, _, actual = heapq.heappop(frontera)
        if actual in nodos_cerrados:
            continue

        nodos_abiertos.discard(actual)
        nodos_cerrados.add(actual)

        if actual == objetivo:
            break

        for vecino in cuadricula.obtener_vecinos(*actual):
            if vecino in nodos_cerrados:
                continue

            costo_tentativo = costo_g[actual] + 1
            if costo_tentativo < costo_g.get(vecino, float("inf")):
                viene_de[vecino] = actual
                costo_g[vecino] = costo_tentativo
                costo_f = costo_tentativo + heuristica(vecino, objetivo)
                heapq.heappush(frontera, (costo_f, next(contador), vecino))
                nodos_abiertos.add(vecino)

    if objetivo not in viene_de:
        return ([], nodos_abiertos, nodos_cerrados)

    ruta: list[tuple[int, int]] = []
    nodo: tuple[int, int] | None = objetivo
    while nodo is not None:
        ruta.append(nodo)
        nodo = viene_de[nodo]
    ruta.reverse()

    return (ruta, nodos_abiertos, nodos_cerrados)


def detectar_bfs(
    cuadricula,
    origen: tuple[int, int],
    objetivo: tuple[int, int],
    radio: int,
) -> bool:
    """Devuelve True si el objetivo es alcanzable en el radio usando BFS."""
    if origen == objetivo:
        return True

    cola = deque([(origen, 0)])
    visitados = {origen}

    while cola:
        actual, pasos = cola.popleft()
        if pasos >= radio:
            continue

        for vecino in cuadricula.obtener_vecinos(*actual):
            if vecino in visitados:
                continue
            if vecino == objetivo:
                return True
            visitados.add(vecino)
            cola.append((vecino, pasos + 1))

    return False
