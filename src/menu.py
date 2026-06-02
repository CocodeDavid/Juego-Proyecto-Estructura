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
        config = self._cargar_configuracion()
        self.algoritmo_enemigo = config.get("algoritmo_enemigo", "a_estrella")
        self.visualizar_recorrido = config.get("visualizar_recorrido", False)

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
            self.desplazamiento_niveles += evento.y * VELOCIDAD_DESPLAZAMIENTO_MENU
            self._ajustar_desplazamiento_niveles()
            return
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button in (4, 5):
            direccion = 1 if evento.button == 4 else -1
            self.desplazamiento_niveles += direccion * VELOCIDAD_DESPLAZAMIENTO_MENU
            self._ajustar_desplazamiento_niveles()
            return
        if evento.type != pygame.MOUSEBUTTONDOWN or evento.button != 1:
            return

        # 1. Comprobar PRIMERO el botón de volver (así evitamos el bug del solapamiento)
        boton_volver = self._obtener_boton_volver()
        if boton_volver["rect"].collidepoint(evento.pos):
            self._ir_a_principal()
            return

        # 2. Comprobar los botones de nivel y eliminación
        for boton in self._obtener_botones_nivel():
            # Solo interactuar con los botones si están actualmente en la zona visible
            if self._rectangulo_visible(boton["rect"]):
                
                # ¿Hizo clic en la X roja?
                if boton["rect_eliminar"].collidepoint(evento.pos):
                    self._eliminar_nivel(boton["nivel"])
                    return
                
                # ¿Hizo clic en el botón para jugar el nivel?
                if boton["rect"].collidepoint(evento.pos):
                    self._iniciar_juego(boton["nivel"])
                    return

    def _eliminar_nivel(self, ruta_str: str) -> None:
        """Elimina físicamente el archivo del nivel y lo quita de la lista visual sin recargar el disco."""
        try:
            archivo_nivel = Path(ruta_str)
            if archivo_nivel.exists():
                archivo_nivel.unlink()  # Borra el archivo .json del disco físico
                
            # Filtrar la lista actual en memoria (borrado suave sin desaparecer los demás)
            niveles_restantes = []
            for item in self.niveles:
                # Extraer la ruta de forma segura sin importar si es Diccionario o Path
                if isinstance(item, dict):
                    ruta_item = str(item.get("ruta", item.get("archivo", item.get("nivel", ""))))
                else:
                    ruta_item = str(item)
                    
                # Conservar solo los niveles que NO son el que acabamos de borrar
                if ruta_item != ruta_str:
                    niveles_restantes.append(item)
                    
            # Actualizamos la lista de niveles que dibuja la pantalla
            self.niveles = niveles_restantes
            
            # Reajustar el scroll por si borramos el último y queda espacio vacío
            if hasattr(self, "_ajustar_desplazamiento_niveles"):
                self._ajustar_desplazamiento_niveles()
                
        except Exception as error:
            print(f"Error al eliminar el nivel: {error}")

    def _manejar_eventos_configuracion(self, evento: pygame.event.Event) -> None:
        """Procesa eventos en la pantalla de configuración."""
        if evento.type != pygame.MOUSEBUTTONDOWN or evento.button != 1:
            return

        # Comprobar click en algoritmos
        for opcion in self._obtener_opciones_algoritmo():
            if opcion["rect"].collidepoint(evento.pos):
                self._establecer_algoritmo(opcion["valor"])
                return
                
        # NUEVO: Comprobar click en el checkbox de visualizar
        rect_visualizar = self._obtener_rect_checkbox_visualizar()
        if rect_visualizar.collidepoint(evento.pos):
            self.visualizar_recorrido = not self.visualizar_recorrido
            self._guardar_configuracion_actual()
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
        """Renderiza la pantalla de selección de nivel."""
        self.pantalla.fill(COLOR_FONDO_MENU)

        # Título de la pantalla
        titulo = self.fuente_titulo.render("Seleccionar Nivel", True, COLOR_TEXTO)
        self.pantalla.blit(titulo, titulo.get_rect(center=(ANCHO // 2, 50)))

        posicion_mouse = pygame.mouse.get_pos()

        # Dibujar botones de niveles
        for boton in self._obtener_botones_nivel():
            # SOLO dibujar si el botón cae en el área visible de la pantalla (evita bugs visuales)
            if self._rectangulo_visible(boton["rect"]):
                # --- 1. Dibujar botón del nivel ---
                color_actual = COLOR_BOTON
                if boton["rect"].collidepoint(posicion_mouse):
                    color_actual = COLOR_BOTON_HOVER
                
                pygame.draw.rect(self.pantalla, color_actual, boton["rect"], border_radius=RADIO_BOTON_MENU)
                texto = self.fuente_boton.render(boton["nombre"], True, COLOR_TEXTO)
                self.pantalla.blit(texto, texto.get_rect(center=boton["rect"].center))

                # --- 2. Dibujar botón de eliminar (X roja) ---
                color_eliminar = (180, 50, 50)  # Rojo oscuro por defecto
                if boton["rect_eliminar"].collidepoint(posicion_mouse):
                    color_eliminar = (235, 60, 60)  # Rojo brillante si el cursor está encima
                
                pygame.draw.rect(self.pantalla, color_eliminar, boton["rect_eliminar"], border_radius=RADIO_BOTON_MENU)
                texto_x = self.fuente_boton.render("X", True, (255, 255, 255))
                self.pantalla.blit(texto_x, texto_x.get_rect(center=boton["rect_eliminar"].center))

        # Dibujar botón Volver
        boton_volver = self._obtener_boton_volver()
        color_volver = COLOR_BOTON
        if boton_volver["rect"].collidepoint(posicion_mouse):
            color_volver = COLOR_BOTON_HOVER
        pygame.draw.rect(self.pantalla, color_volver, boton_volver["rect"], border_radius=RADIO_BOTON_MENU)
        texto_volver = self.fuente_boton.render(boton_volver["texto"], True, COLOR_TEXTO)
        self.pantalla.blit(texto_volver, texto_volver.get_rect(center=boton_volver["rect"].center))

    def _dibujar_configuracion(self) -> None:
        """Renderiza la pantalla de configuración del algoritmo."""
        self._dibujar_titulo("Configuración")
        subtitulo = self.fuente_boton.render(
            "Algoritmo de búsqueda del enemigo", True, COLOR_TEXTO
        )
        rect_subtitulo = subtitulo.get_rect(
            midtop=(
                ANCHO // 2,
                MARGEN_SUPERIOR_TITULO_MENU + TAMANO_FUENTE_TITULO_MENU + ESPACIADO_BOTONES_MENU,
            )
        )
        self.pantalla.blit(subtitulo, rect_subtitulo)

        for opcion in self._obtener_opciones_algoritmo():
            seleccionado = opcion["valor"] == self.algoritmo_enemigo
            self._dibujar_opcion_algoritmo(
                opcion["rect"], opcion["texto"], seleccionado
            )
            
        # NUEVO: Dibujar checkbox de visualización
        rect_visualizar = self._obtener_rect_checkbox_visualizar()
        self._dibujar_checkbox(rect_visualizar, "Visualizar recorrido enemigos", self.visualizar_recorrido)

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

    def _obtener_botones_nivel(self) -> list[dict]:
        """Calcula la geometría de los botones de nivel basados en el desplazamiento."""
        botones = []
        ancho_boton = ANCHO_BOTON_MENU
        alto_boton = ALTO_BOTON_MENU
        espaciado = ESPACIADO_BOTONES_MENU
        
        # Tamaño para el botón de eliminar (un cuadrado rojo alineado con la altura del nivel)
        tamano_eliminar = alto_boton 
        espacio_entre_botones = 10
        
        # Ancho total combinado (Botón del nivel + separación + Botón X)
        ancho_total_bloque = ancho_boton + espacio_entre_botones + tamano_eliminar
        
        x_inicio = ANCHO // 2 - ancho_total_bloque // 2
        y_inicio = MARGEN_SUPERIOR_LISTA_MENU + self.desplazamiento_niveles

        for indice, item in enumerate(self.niveles):
            y_boton = y_inicio + indice * (alto_boton + espaciado)
            
            # --- CORRECCIÓN: Compatibilidad entre Diccionarios y objetos Path ---
            if isinstance(item, dict):
                # Si viene como diccionario (carga inicial del menú)
                ruta_str = str(item.get("ruta", item.get("archivo", item.get("nivel", ""))))
                nombre_nivel = str(item.get("nombre", "Nivel"))
            else:
                # Si viene como objeto Path (cuando recargamos la lista tras eliminar)
                ruta_str = str(item)
                nombre_nivel = item.stem
            # --------------------------------------------------------------------
            
            rect_nivel = pygame.Rect(x_inicio, y_boton, ancho_boton, alto_boton)
            rect_eliminar = pygame.Rect(
                x_inicio + ancho_boton + espacio_entre_botones, 
                y_boton, 
                tamano_eliminar, 
                alto_boton
            )
            
            botones.append({
                "nivel": ruta_str,
                "nombre": nombre_nivel,
                "rect": rect_nivel,
                "rect_eliminar": rect_eliminar
            })
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
        """Devuelve las opciones del algoritmo de búsqueda actualizado."""
        opciones = [
            {"texto": "A* (A estrella)", "valor": "a_estrella"},
            {"texto": "DFS (Búsqueda en profundidad)", "valor": "dfs"},
            {"texto": "Dijkstra", "valor": "dijkstra"},
        ]
        lista: list[dict[str, object]] = []
        inicio_y = MARGEN_SUPERIOR_LISTA_MENU
        for indice, opcion in enumerate(opciones):
            y = inicio_y + indice * (ALTO_BOTON_MENU + ESPACIADO_ALGORITMOS_MENU)
            rect = pygame.Rect((ANCHO - ANCHO_BOTON_MENU) // 2, y, ANCHO_BOTON_MENU, ALTO_BOTON_MENU)
            lista.append({"texto": opcion["texto"], "valor": opcion["valor"], "rect": rect})
        return lista

    
    def _obtener_rect_checkbox_visualizar(self) -> pygame.Rect:
        """Obtiene la posición para el botón de visualizar recorrido."""
        opciones = self._obtener_opciones_algoritmo()
        y = opciones[-1]["rect"].bottom + ESPACIADO_ALGORITMOS_MENU * 2
        return pygame.Rect((ANCHO - ANCHO_BOTON_MENU) // 2, y, ANCHO_BOTON_MENU, ALTO_BOTON_MENU)

    def _dibujar_checkbox(
        self, rectangulo: pygame.Rect, texto: str, seleccionado: bool
    ) -> None:
        """Dibuja una opción de casilla de verificación (checkbox)."""
        posicion_mouse = pygame.mouse.get_pos()
        hover = rectangulo.collidepoint(posicion_mouse)
        color = COLOR_BOTON_HOVER if hover else COLOR_BOTON
            
        pygame.draw.rect(self.pantalla, color, rectangulo, border_radius=RADIO_BOTON_MENU)

        lado_checkbox = 20
        rect_cuadro = pygame.Rect(
            rectangulo.left + MARGEN_SELECTOR_ALGORITMO,
            rectangulo.centery - lado_checkbox // 2,
            lado_checkbox,
            lado_checkbox
        )
        pygame.draw.rect(self.pantalla, COLOR_TEXTO, rect_cuadro, ANCHO_BORDE_SELECTOR, border_radius=4)
        
        if seleccionado:
            rect_relleno = rect_cuadro.inflate(-8, -8)
            pygame.draw.rect(self.pantalla, COLOR_TEXTO, rect_relleno, border_radius=2)

        superficie = self.fuente_boton.render(texto, True, COLOR_TEXTO)
        rect_texto = superficie.get_rect()
        rect_texto.midleft = (
            rect_cuadro.right + ESPACIADO_TEXTO_SELECTOR,
            rectangulo.centery,
        )
        self.pantalla.blit(superficie, rect_texto)












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
        permitidos = ["a_estrella", "dfs", "dijkstra"]
        if algoritmo not in permitidos:
            return
        self.algoritmo_enemigo = algoritmo
        self._guardar_configuracion_actual()

    def _iniciar_juego(self, nivel) -> None:
        """Inicia el juego cargando el nivel seleccionado de forma segura."""
        try:
            # --- CORRECCIÓN DE TIPO ---
            # Si el nivel ya es un string (lo común con los nuevos botones), lo usamos directamente.
            # Si viene como diccionario, extraemos su ruta de forma segura.
            if isinstance(nivel, dict):
                ruta_final = str(nivel.get("ruta", nivel.get("archivo", nivel.get("nivel", ""))))
            else:
                ruta_final = str(nivel)
            # ---------------------------

            # Aquí va tu lógica original para lanzar el juego. 
            # Asegúrate de pasar 'ruta_final' al constructor de tu clase Game o al cargador del nivel.
            from src.game import Game
            instancia_juego = Game()
            
            # Cargamos el nivel usando la ruta limpia en string
            instancia_juego.cargar_nivel(ruta_final) 
            instancia_juego.ejecutar()
            
            # Al regresar del juego, reajustamos la pantalla del menú por si acaso
            pygame.display.set_mode((ANCHO, ALTO))
            pygame.display.set_caption(TITULO_VENTANA)
            
        except Exception as e:
            print(f"Error al iniciar el juego con el nivel {nivel}: {e}")

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

    def _cargar_configuracion(self) -> dict:
        """Carga la configuración completa desde el archivo json."""
        config_default = {"algoritmo_enemigo": "a_estrella", "visualizar_recorrido": False}
        if self.ruta_configuracion.exists():
            try:
                with open(self.ruta_configuracion, "r", encoding="utf-8") as archivo:
                    datos = json.load(archivo)
                    config_default["algoritmo_enemigo"] = datos.get("algoritmo_enemigo", "a_estrella")
                    config_default["visualizar_recorrido"] = datos.get("visualizar_recorrido", False)
            except Exception:
                pass
        return config_default

    def _guardar_configuracion_actual(self) -> None:
        """Guarda la configuración actual en config.json."""
        datos = {
            "algoritmo_enemigo": self.algoritmo_enemigo,
            "visualizar_recorrido": self.visualizar_recorrido
        }
        try:
            with open(self.ruta_configuracion, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, ensure_ascii=False)
        except OSError:
            pass

    def _salir(self) -> None:
        """Cierra la aplicación por completo."""
        pygame.quit()
        sys.exit()
