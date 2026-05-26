"""Sistema de menú principal y navegación de pantallas."""

import json
import sys
from pathlib import Path

import pygame

from settings import (
    ALGORITMOS_DISPONIBLES,
    ALTO,
    ANCHO,
    ANCHO_BORDE_SELECTOR,
    ANCHO_BOTON_MENU,
    ALTO_BOTON_MENU,
    APARICION_JUGADOR_POR_DEFECTO,
    COLOR_BOTON,
    COLOR_BOTON_ACTIVO,
    COLOR_BOTON_HOVER,
    COLOR_FONDO_MENU,
    COLOR_TEXTO,
    ESPACIADO_ALGORITMOS_MENU,
    ESPACIADO_BOTONES_MENU,
    ESPACIADO_TEXTO_SELECTOR,
    FOTOGRAMAS_POR_SEGUNDO,
    MARGEN_INFERIOR_MENU,
    MARGEN_SELECTOR_ALGORITMO,
    MARGEN_SUPERIOR_LISTA_MENU,
    MARGEN_SUPERIOR_TITULO_MENU,
    RADIO_BOTON_MENU,
    RADIO_SELECTOR_ALGORITMO,
    TAMANO_FUENTE_BOTON_MENU,
    TAMANO_FUENTE_TITULO_MENU,
    TITULO_VENTANA,
    VELOCIDAD_DESPLAZAMIENTO_MENU,
)

PANTALLA_PRINCIPAL = "PRINCIPAL"
PANTALLA_SELECCION_NIVEL = "SELECCION_NIVEL"
PANTALLA_CONFIGURACION = "CONFIGURACION"
PANTALLA_EDITOR = "EDITOR"


class Menu:
    """Gestiona el menú principal, configuración y selección de nivel."""

    def __init__(self) -> None:
        """Inicializa el menú, recursos y configuración persistente."""
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption(TITULO_VENTANA)
        self.reloj = pygame.time.Clock()
        self.fuente_titulo = pygame.font.SysFont(None, TAMANO_FUENTE_TITULO_MENU)
        self.fuente_boton = pygame.font.SysFont(None, TAMANO_FUENTE_BOTON_MENU)

        self.pantalla_actual = PANTALLA_PRINCIPAL
        self.en_ejecucion = False

        self.ruta_base = Path(__file__).resolve().parents[1]
        self.ruta_configuracion = self.ruta_base / "config.json"
        self.algoritmo_enemigo = self._cargar_configuracion()

        self.niveles: list[dict[str, object]] = []
        self.desplazamiento_niveles = 0

    def ejecutar(self) -> None:
        """Ejecuta el bucle principal del menú."""
        self.en_ejecucion = True
        while self.en_ejecucion:
            self._manejar_eventos()
            self._dibujar()
            self.reloj.tick(FOTOGRAMAS_POR_SEGUNDO)
        pygame.quit()

    def _manejar_eventos(self) -> None:
        """Maneja eventos globales y delega según la pantalla actual."""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self._salir()
            elif self.pantalla_actual == PANTALLA_PRINCIPAL:
                self._manejar_eventos_principal(evento)
            elif self.pantalla_actual == PANTALLA_SELECCION_NIVEL:
                self._manejar_eventos_seleccion(evento)
            elif self.pantalla_actual == PANTALLA_CONFIGURACION:
                self._manejar_eventos_configuracion(evento)

    def _manejar_eventos_principal(self, evento: pygame.event.Event) -> None:
        """Procesa eventos de la pantalla principal."""
        if evento.type != pygame.MOUSEBUTTONDOWN or evento.button != 1:
            return
        for boton in self._obtener_botones_principal():
            if boton["rect"].collidepoint(evento.pos):
                boton["accion"]()
                break

    def _manejar_eventos_seleccion(self, evento: pygame.event.Event) -> None:
        """Procesa eventos en la selección de nivel."""
        if evento.type == pygame.MOUSEWHEEL:
            self.desplazamiento_niveles += (
                evento.y * VELOCIDAD_DESPLAZAMIENTO_MENU
            )
            self._ajustar_desplazamiento_niveles()
            return
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button in (4, 5):
            direccion = 1 if evento.button == 4 else -1
            self.desplazamiento_niveles += (
                direccion * VELOCIDAD_DESPLAZAMIENTO_MENU
            )
            self._ajustar_desplazamiento_niveles()
            return
        if evento.type != pygame.MOUSEBUTTONDOWN or evento.button != 1:
            return

        for boton in self._obtener_botones_nivel():
            if boton["rect"].collidepoint(evento.pos):
                self._iniciar_juego(boton["nivel"])
                return

        boton_volver = self._obtener_boton_volver()
        if boton_volver["rect"].collidepoint(evento.pos):
            self._ir_a_principal()

    def _manejar_eventos_configuracion(self, evento: pygame.event.Event) -> None:
        """Procesa eventos en la pantalla de configuración."""
        if evento.type != pygame.MOUSEBUTTONDOWN or evento.button != 1:
            return

        for opcion in self._obtener_opciones_algoritmo():
            if opcion["rect"].collidepoint(evento.pos):
                self._establecer_algoritmo(opcion["valor"])
                return

        boton_volver = self._obtener_boton_volver()
        if boton_volver["rect"].collidepoint(evento.pos):
            self._ir_a_principal()

    def _dibujar(self) -> None:
        """Dibuja la pantalla actual del menú."""
        self.pantalla.fill(COLOR_FONDO_MENU)
        if self.pantalla_actual == PANTALLA_PRINCIPAL:
            self._dibujar_principal()
        elif self.pantalla_actual == PANTALLA_SELECCION_NIVEL:
            self._dibujar_seleccion_nivel()
        elif self.pantalla_actual == PANTALLA_CONFIGURACION:
            self._dibujar_configuracion()
        pygame.display.flip()

    def _dibujar_principal(self) -> None:
        """Renderiza la pantalla principal del menú."""
        self._dibujar_titulo(TITULO_VENTANA)
        for boton in self._obtener_botones_principal():
            self._dibujar_boton(boton["rect"], boton["texto"], False)

    def _dibujar_seleccion_nivel(self) -> None:
        """Renderiza la selección de nivel y la lista desplazable."""
        self._dibujar_titulo("Seleccionar nivel")
        for boton in self._obtener_botones_nivel():
            if self._rectangulo_visible(boton["rect"]):
                self._dibujar_boton(boton["rect"], boton["texto"], False)
        boton_volver = self._obtener_boton_volver()
        self._dibujar_boton(boton_volver["rect"], boton_volver["texto"], False)

    def _dibujar_configuracion(self) -> None:
        """Renderiza la pantalla de configuración del algoritmo."""
        self._dibujar_titulo("Configuración")
        subtitulo = self.fuente_boton.render(
            "Algoritmo de búsqueda del enemigo", True, COLOR_TEXTO
        )
        rect_subtitulo = subtitulo.get_rect(
            midtop=(
                ANCHO // 2,
                MARGEN_SUPERIOR_TITULO_MENU
                + TAMANO_FUENTE_TITULO_MENU
                + ESPACIADO_BOTONES_MENU,
            )
        )
        self.pantalla.blit(subtitulo, rect_subtitulo)

        for opcion in self._obtener_opciones_algoritmo():
            seleccionado = opcion["valor"] == self.algoritmo_enemigo
            self._dibujar_opcion_algoritmo(
                opcion["rect"], opcion["texto"], seleccionado
            )

        boton_volver = self._obtener_boton_volver()
        self._dibujar_boton(boton_volver["rect"], boton_volver["texto"], False)

    def _dibujar_titulo(self, texto: str) -> None:
        """Dibuja el título principal centrado en la parte superior."""
        superficie = self.fuente_titulo.render(texto, True, COLOR_TEXTO)
        rect = superficie.get_rect(midtop=(ANCHO // 2, MARGEN_SUPERIOR_TITULO_MENU))
        self.pantalla.blit(superficie, rect)

    def _dibujar_boton(self, rectangulo: pygame.Rect, texto: str, activo: bool) -> None:
        """Dibuja un botón con estados hover y activo."""
        posicion_mouse = pygame.mouse.get_pos()
        hover = rectangulo.collidepoint(posicion_mouse)
        if activo:
            color = COLOR_BOTON_ACTIVO
        elif hover:
            color = COLOR_BOTON_HOVER
        else:
            color = COLOR_BOTON
        pygame.draw.rect(self.pantalla, color, rectangulo, border_radius=RADIO_BOTON_MENU)
        superficie = self.fuente_boton.render(texto, True, COLOR_TEXTO)
        rect_texto = superficie.get_rect(center=rectangulo.center)
        self.pantalla.blit(superficie, rect_texto)

    def _dibujar_opcion_algoritmo(
        self, rectangulo: pygame.Rect, texto: str, seleccionado: bool
    ) -> None:
        """Dibuja una opción con selector tipo radio."""
        posicion_mouse = pygame.mouse.get_pos()
        hover = rectangulo.collidepoint(posicion_mouse)
        if seleccionado:
            color = COLOR_BOTON_ACTIVO
        elif hover:
            color = COLOR_BOTON_HOVER
        else:
            color = COLOR_BOTON
        pygame.draw.rect(self.pantalla, color, rectangulo, border_radius=RADIO_BOTON_MENU)

        centro_selector = (
            rectangulo.left + MARGEN_SELECTOR_ALGORITMO,
            rectangulo.centery,
        )
        pygame.draw.circle(
            self.pantalla,
            COLOR_TEXTO,
            centro_selector,
            RADIO_SELECTOR_ALGORITMO,
            ANCHO_BORDE_SELECTOR,
        )
        if seleccionado:
            pygame.draw.circle(
                self.pantalla,
                COLOR_TEXTO,
                centro_selector,
                RADIO_SELECTOR_ALGORITMO // 2,
            )

        superficie = self.fuente_boton.render(texto, True, COLOR_TEXTO)
        rect_texto = superficie.get_rect()
        rect_texto.midleft = (
            rectangulo.left
            + MARGEN_SELECTOR_ALGORITMO
            + RADIO_SELECTOR_ALGORITMO * 2
            + ESPACIADO_TEXTO_SELECTOR,
            rectangulo.centery,
        )
        self.pantalla.blit(superficie, rect_texto)

    def _obtener_botones_principal(self) -> list[dict[str, object]]:
        """Genera los botones de la pantalla principal."""
        opciones = [
            {"texto": "Jugar", "accion": self._ir_a_seleccion},
            {"texto": "Configuración", "accion": self._ir_a_configuracion},
            {"texto": "Editor de Niveles", "accion": self._abrir_editor},
            {"texto": "Salir", "accion": self._salir},
        ]
        total_altura = len(opciones) * ALTO_BOTON_MENU + (
            len(opciones) - 1
        ) * ESPACIADO_BOTONES_MENU
        inicio_y = (ALTO - total_altura) // 2
        botones: list[dict[str, object]] = []
        for indice, opcion in enumerate(opciones):
            y = inicio_y + indice * (ALTO_BOTON_MENU + ESPACIADO_BOTONES_MENU)
            rect = pygame.Rect(
                (ANCHO - ANCHO_BOTON_MENU) // 2,
                y,
                ANCHO_BOTON_MENU,
                ALTO_BOTON_MENU,
            )
            botones.append({"texto": opcion["texto"], "accion": opcion["accion"], "rect": rect})
        return botones

    def _obtener_botones_nivel(self) -> list[dict[str, object]]:
        """Genera los botones de niveles disponibles."""
        botones: list[dict[str, object]] = []
        inicio_y = MARGEN_SUPERIOR_LISTA_MENU + self.desplazamiento_niveles
        for indice, nivel in enumerate(self.niveles):
            y = inicio_y + indice * (ALTO_BOTON_MENU + ESPACIADO_BOTONES_MENU)
            rect = pygame.Rect(
                (ANCHO - ANCHO_BOTON_MENU) // 2,
                y,
                ANCHO_BOTON_MENU,
                ALTO_BOTON_MENU,
            )
            botones.append({"texto": nivel["nombre"], "nivel": nivel, "rect": rect})
        return botones

    def _obtener_boton_volver(self) -> dict[str, object]:
        """Devuelve el botón de volver para submenús."""
        y = ALTO - MARGEN_INFERIOR_MENU - ALTO_BOTON_MENU
        rect = pygame.Rect(
            (ANCHO - ANCHO_BOTON_MENU) // 2,
            y,
            ANCHO_BOTON_MENU,
            ALTO_BOTON_MENU,
        )
        return {"texto": "Volver", "rect": rect}

    def _obtener_opciones_algoritmo(self) -> list[dict[str, object]]:
        """Devuelve las opciones del algoritmo de búsqueda."""
        opciones = [
            {"texto": "A* (A-estrella)", "valor": "astar"},
            {"texto": "BFS (Búsqueda en anchura)", "valor": "bfs"},
            {"texto": "Patrulla aleatoria", "valor": "patrulla"},
        ]
        lista: list[dict[str, object]] = []
        inicio_y = MARGEN_SUPERIOR_LISTA_MENU
        for indice, opcion in enumerate(opciones):
            y = inicio_y + indice * (ALTO_BOTON_MENU + ESPACIADO_ALGORITMOS_MENU)
            rect = pygame.Rect(
                (ANCHO - ANCHO_BOTON_MENU) // 2,
                y,
                ANCHO_BOTON_MENU,
                ALTO_BOTON_MENU,
            )
            lista.append({"texto": opcion["texto"], "valor": opcion["valor"], "rect": rect})
        return lista

    def _cargar_niveles(self) -> None:
        """Carga los niveles disponibles desde la carpeta levels."""
        self.niveles = []
        ruta_niveles = self.ruta_base / "levels"
        if not ruta_niveles.exists():
            self._ajustar_desplazamiento_niveles()
            return

        for ruta in sorted(ruta_niveles.glob("*.json")):
            datos = {}
            try:
                with open(ruta, "r", encoding="utf-8") as archivo:
                    datos = json.load(archivo)
            except (OSError, json.JSONDecodeError):
                datos = {}
            nombre = ruta.stem
            if isinstance(datos, dict):
                nombre = str(datos.get("name", ruta.stem))
            self.niveles.append({"ruta": ruta, "nombre": nombre, "datos": datos})

        self._ajustar_desplazamiento_niveles()

    def _ajustar_desplazamiento_niveles(self) -> None:
        """Ajusta el desplazamiento para mantener la lista dentro de límites."""
        altura_total = len(self.niveles) * ALTO_BOTON_MENU + max(
            0, len(self.niveles) - 1
        ) * ESPACIADO_BOTONES_MENU
        altura_visible = ALTO - MARGEN_SUPERIOR_LISTA_MENU - (
            ALTO_BOTON_MENU + MARGEN_INFERIOR_MENU
        )
        if altura_total <= altura_visible:
            self.desplazamiento_niveles = 0
            return
        max_desplazamiento = 0
        min_desplazamiento = altura_visible - altura_total
        self.desplazamiento_niveles = max(
            min(self.desplazamiento_niveles, max_desplazamiento), min_desplazamiento
        )

    def _rectangulo_visible(self, rectangulo: pygame.Rect) -> bool:
        """Determina si el rectángulo está dentro del área visible."""
        limite_superior = MARGEN_SUPERIOR_LISTA_MENU
        limite_inferior = ALTO - (ALTO_BOTON_MENU + MARGEN_INFERIOR_MENU)
        return rectangulo.bottom >= limite_superior and rectangulo.top <= limite_inferior

    def _ir_a_principal(self) -> None:
        """Regresa a la pantalla principal."""
        self.pantalla_actual = PANTALLA_PRINCIPAL

    def _ir_a_seleccion(self) -> None:
        """Abre la pantalla de selección de niveles."""
        self._cargar_niveles()
        self.desplazamiento_niveles = 0
        self.pantalla_actual = PANTALLA_SELECCION_NIVEL

    def _ir_a_configuracion(self) -> None:
        """Abre la pantalla de configuración."""
        self.pantalla_actual = PANTALLA_CONFIGURACION

    def _establecer_algoritmo(self, algoritmo: str) -> None:
        """Actualiza el algoritmo seleccionado y lo guarda en disco."""
        if algoritmo not in ALGORITMOS_DISPONIBLES:
            return
        self.algoritmo_enemigo = algoritmo
        self._guardar_configuracion(algoritmo)

    def _iniciar_juego(self, nivel: dict[str, object]) -> None:
        """Carga el nivel seleccionado e inicia el juego."""
        from src.game import Game

        ruta = nivel.get("ruta")
        datos = nivel.get("datos") if isinstance(nivel.get("datos"), dict) else {}
        juego = Game()
        if isinstance(ruta, Path):
            juego.cuadricula.cargar_desde_json(str(ruta))

        aparicion = {}
        if isinstance(datos, dict):
            aparicion = datos.get("player_spawn", {})
        fila = APARICION_JUGADOR_POR_DEFECTO[0]
        columna = APARICION_JUGADOR_POR_DEFECTO[1]
        if isinstance(aparicion, dict):
            fila = int(aparicion.get("row", fila))
            columna = int(aparicion.get("col", columna))
        juego.jugador.posicion = juego.cuadricula.celda_a_pixel_centro(fila, columna)
        juego.ejecutar()

        self._restablecer_menu()
        self.pantalla_actual = PANTALLA_PRINCIPAL

    def _abrir_editor(self) -> None:
        """Abre el editor de niveles y regresa al menú."""
        from src.editor import LevelEditor

        self.pantalla_actual = PANTALLA_EDITOR
        editor = LevelEditor()
        editor.ejecutar()
        self._restablecer_menu()
        self.pantalla_actual = PANTALLA_PRINCIPAL

    def _restablecer_menu(self) -> None:
        """Restablece la ventana para el menú después de cerrar subpantallas."""
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption(TITULO_VENTANA)
        pygame.font.init()
        self.fuente_titulo = pygame.font.SysFont(None, TAMANO_FUENTE_TITULO_MENU)
        self.fuente_boton = pygame.font.SysFont(None, TAMANO_FUENTE_BOTON_MENU)

    def _cargar_configuracion(self) -> str:
        """Carga la configuración del algoritmo desde disco."""
        algoritmo = ALGORITMOS_DISPONIBLES[0]
        if self.ruta_configuracion.exists():
            try:
                with open(self.ruta_configuracion, "r", encoding="utf-8") as archivo:
                    datos = json.load(archivo)
                algoritmo = str(datos.get("algoritmo_enemigo", algoritmo))
            except (OSError, json.JSONDecodeError, AttributeError):
                algoritmo = ALGORITMOS_DISPONIBLES[0]
        if algoritmo not in ALGORITMOS_DISPONIBLES:
            algoritmo = ALGORITMOS_DISPONIBLES[0]
        self._guardar_configuracion(algoritmo)
        return algoritmo

    def _guardar_configuracion(self, algoritmo: str) -> None:
        """Guarda la configuración actual en config.json."""
        datos = {"algoritmo_enemigo": algoritmo}
        try:
            with open(self.ruta_configuracion, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, ensure_ascii=False)
        except OSError:
            return

    def _salir(self) -> None:
        """Cierra la aplicación por completo."""
        pygame.quit()
        sys.exit()
