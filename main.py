"""Punto de entrada principal del juego."""

from src.menu import Menu


def principal() -> None:
    """Inicia la aplicación mostrando el menú principal."""
    menu = Menu()
    menu.ejecutar()


if __name__ == "__main__":
    principal()
