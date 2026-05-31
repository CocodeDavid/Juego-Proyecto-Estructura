"""Algoritmos de búsqueda para navegación en cuadrículas."""

import heapq
from collections import deque
from itertools import count


def heuristica(celda_a: tuple[int, int], celda_b: tuple[int, int]) -> int:
    """Devuelve la distancia Manhattan entre dos celdas (movimiento ortogonal)."""
    return abs(celda_a[0] - celda_b[0]) + abs(celda_a[1] - celda_b[1])


def dfs(
    grafo,
    inicio: tuple[int, int],
    destino: tuple[int, int],
) -> list[tuple[int, int]]:
    """Calcula una ruta usando Búsqueda en Profundidad (DFS) de forma estable."""
    if not grafo.es_nodo_valido(inicio) or not grafo.es_nodo_valido(destino):
        return []

    # Guardamos en la pila una tupla: (nodo_actual, camino_hasta_este_nodo)
    pila = [(inicio, [])]
    visitados = set()

    while pila:
        actual, camino = pila.pop()

        if actual == destino:
            return camino  # Retorna la ruta directa encontrada

        if actual not in visitados:
            visitados.add(actual)

            for vecino in grafo.obtener_vecinos(actual):
                if vecino not in visitados:
                    # Clonamos el camino actual y le sumamos el vecino
                    pila.append((vecino, camino + [vecino]))

    return []


def dijkstra(
    grafo,
    inicio: tuple[int, int],
    destino: tuple[int, int],
) -> list[tuple[int, int]]:
    """Calcula la ruta más corta usando el algoritmo de Dijkstra."""
    if not grafo.es_nodo_valido(inicio) or not grafo.es_nodo_valido(destino):
        return []

    frontera: list[tuple[int, int, tuple[int, int]]] = []
    contador = count()
    heapq.heappush(frontera, (0, next(contador), inicio))

    viene_de: dict[tuple[int, int], tuple[int, int] | None] = {inicio: None}
    costo_acumulado = {inicio: 0}

    while frontera:
        costo_actual, _, actual = heapq.heappop(frontera)

        if actual == destino:
            break

        if costo_actual > costo_acumulado[actual]:
            continue

        for vecino in grafo.obtener_vecinos(actual):
            # Costo uniforme de movimiento = 1 por celda transitable
            nuevo_costo = costo_actual + 1
            if vecino not in costo_acumulado or nuevo_costo < costo_acumulado[vecino]:
                costo_acumulado[vecino] = nuevo_costo
                viene_de[vecino] = actual
                heapq.heappush(frontera, (nuevo_costo, next(contador), vecino))

    if destino not in viene_de:
        return []

    # Reconstrucción del camino
    camino: list[tuple[int, int]] = []
    nodo = destino
    while nodo is not None and nodo != inicio:
        camino.append(nodo)
        nodo = viene_de[nodo]
    camino.reverse()
    return camino


def a_estrella(
    grafo,
    inicio: tuple[int, int],
    destino: tuple[int, int],
) -> list[tuple[int, int]]:
    """Calcula una ruta óptima usando el algoritmo A* con Heurística Manhattan."""
    if not grafo.es_nodo_valido(inicio) or not grafo.es_nodo_valido(destino):
        return []

    frontera: list[tuple[int, int, tuple[int, int]]] = []
    contador = count()
    heapq.heappush(frontera, (0, next(contador), inicio))

    viene_de: dict[tuple[int, int], tuple[int, int] | None] = {inicio: None}
    costo_g = {inicio: 0}

    while frontera:
        _, _, actual = heapq.heappop(frontera)

        if actual == destino:
            break

        for vecino in grafo.obtener_vecinos(actual):
            posible_g = costo_g[actual] + 1
            if vecino not in costo_g or posible_g < costo_g[vecino]:
                costo_g[vecino] = posible_g
                f_score = posible_g + heuristica(vecino, destino)
                viene_de[vecino] = actual
                heapq.heappush(frontera, (f_score, next(contador), vecino))

    if destino not in viene_de:
        return []

    # Reconstrucción del camino
    camino: list[tuple[int, int]] = []
    nodo = destino
    while nodo is not None and nodo != inicio:
        camino.append(nodo)
        nodo = viene_de[nodo]
    camino.reverse()
    return camino


def detectar_bfs(
    grafo,
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

        for vecino in grafo.obtener_vecinos(actual):
            if vecino in visitados:
                continue
            if vecino == objetivo:
                return True
            visitados.add(vecino)
            cola.append((vecino, pasos + 1))

    return False
