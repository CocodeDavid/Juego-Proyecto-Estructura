"""Búsqueda en anchura para el jugador; enemigos usan otros algoritmos."""

from collections import deque


def bfs(
    grafo,
    inicio: tuple[int, int],
    destino: tuple[int, int],
) -> list[tuple[int, int]]:
    """Calcula el camino más corto usando BFS desde inicio hasta destino."""
    if inicio == destino:
        return []
    if not grafo.es_nodo_valido(inicio) or not grafo.es_nodo_valido(destino):
        return []

    cola = deque([inicio])
    visitados = {inicio}
    viene_de: dict[tuple[int, int], tuple[int, int] | None] = {inicio: None}

    while cola:
        actual = cola.popleft()
        if actual == destino:
            break
        for vecino in grafo.obtener_vecinos(actual):
            if vecino in visitados:
                continue
            visitados.add(vecino)
            viene_de[vecino] = actual
            cola.append(vecino)

    if destino not in viene_de:
        return []

    camino: list[tuple[int, int]] = []
    nodo = destino
    while nodo is not None and nodo != inicio:
        camino.append(nodo)
        nodo = viene_de[nodo]
    camino.reverse()
    return camino


def bfs_con_debug(
    grafo,
    inicio: tuple[int, int],
    destino: tuple[int, int],
) -> tuple[list[tuple[int, int]], set[tuple[int, int]]]:
    """Devuelve el camino BFS y el conjunto de nodos visitados."""
    if inicio == destino:
        return ([], {inicio})
    if not grafo.es_nodo_valido(inicio) or not grafo.es_nodo_valido(destino):
        return ([], set())

    cola = deque([inicio])
    visitados = {inicio}
    viene_de: dict[tuple[int, int], tuple[int, int] | None] = {inicio: None}

    while cola:
        actual = cola.popleft()
        if actual == destino:
            break
        for vecino in grafo.obtener_vecinos(actual):
            if vecino in visitados:
                continue
            visitados.add(vecino)
            viene_de[vecino] = actual
            cola.append(vecino)

    if destino not in viene_de:
        return ([], visitados)

    camino: list[tuple[int, int]] = []
    nodo = destino
    while nodo is not None and nodo != inicio:
        camino.append(nodo)
        nodo = viene_de[nodo]
    camino.reverse()
    return (camino, visitados)
