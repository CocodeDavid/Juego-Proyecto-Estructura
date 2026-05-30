"""Menú de Game Over superpuesto al juego tras una derrota."""

import pygame

from settings import ALTO, ANCHO


class GameOverMenu:
    """Representa la pantalla de derrota del jugador."""

    def __init__(self, pantalla: pygame.Surface) -> None:
        """Inicializa las opciones y la interfaz del menú."""
        self.pantalla = pantalla
        pygame.font.init()
        self.fuente_titulo = pygame.font.SysFont(None, 80)
        self.fuente_boton = pygame.font.SysFont(None, 40)

        ancho_boton = 250
        alto_boton = 50
        centro_x = ANCHO // 2 - ancho_boton // 2
        centro_y = ALTO // 2

        self.botones = [
            {
                "texto": "Volver a jugar",
                "accion": "reiniciar",
                "color": (50, 160, 80),
                "rect": pygame.Rect(centro_x, centro_y - 70, ancho_boton, alto_boton),
            },
            {
                "texto": "Volver al menú",
                "accion": "menu",
                "color": (200, 150, 40),
                "rect": pygame.Rect(centro_x, centro_y, ancho_boton, alto_boton),
            },
            {
                "texto": "Salir del juego",
                "accion": "salir",
                "color": (200, 60, 60),
                "rect": pygame.Rect(centro_x, centro_y + 70, ancho_boton, alto_boton),
            },
        ]

    def dibujar(self) -> None:
        """Dibuja el fondo tintado y los botones en pantalla."""
        # Capa roja semitransparente para efecto dramático
        superficie = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        superficie.fill((100, 0, 0, 160)) 
        self.pantalla.blit(superficie, (0, 0))

        # Título
        titulo = self.fuente_titulo.render("GAME OVER", True, (255, 80, 80))
        rect_titulo = titulo.get_rect(center=(ANCHO // 2, ALTO // 2 - 150))
        self.pantalla.blit(titulo, rect_titulo)

        posicion_mouse = pygame.mouse.get_pos()
        for boton in self.botones:
            color_actual = boton["color"]
            if boton["rect"].collidepoint(posicion_mouse):
                color_actual = (
                    min(color_actual[0] + 40, 255),
                    min(color_actual[1] + 40, 255),
                    min(color_actual[2] + 40, 255),
                )

            pygame.draw.rect(self.pantalla, color_actual, boton["rect"], border_radius=8)
            texto = self.fuente_boton.render(boton["texto"], True, (255, 255, 255))
            rect_texto = texto.get_rect(center=boton["rect"].center)
            self.pantalla.blit(texto, rect_texto)

    def manejar_click(self, posicion: tuple[int, int]) -> str | None:
        """Devuelve la acción del botón clickeado, o None si clicó fuera."""
        for boton in self.botones:
            if boton["rect"].collidepoint(posicion):
                return str(boton["accion"])
        return None