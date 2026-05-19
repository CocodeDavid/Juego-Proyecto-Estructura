# Juego Estructuras de Datos

Proyecto universitario para el curso de Estructuras de Datos. El objetivo es construir un juego 2D en cuadrícula (top-down) para visualizar algoritmos de búsqueda y IA.

## Módulos y responsables

- **Pathfinding (P1):** implementación de A* y BFS en `src/pathfinding.py`.
- **Enemigos (P2):** estados y comportamiento en `src/enemy.py`.
- **Editor de niveles (P3):** creación y guardado de mapas en `src/editor.py`.

## Algoritmos utilizados

- A* con min-heap (priority queue).
- BFS con `deque` para detección por radio.
- FSM (máquina de estados finitos) para enemigos.

## Instalación

```bash
pip install pygame-ce
```

## Ejecución

```bash
python main.py
```

Para abrir el editor de niveles:

```bash
python src/editor.py
```
