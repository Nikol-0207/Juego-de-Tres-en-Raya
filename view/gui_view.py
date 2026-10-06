import pygame
 
# ----------------------------------------------------------------------
# Constantes 
# ----------------------------------------------------------------------

BOARD_SIZE = 480                  
CELL_SIZE = BOARD_SIZE // 3       
PANEL_WIDTH = 280
WINDOW_SIZE = (BOARD_SIZE + PANEL_WIDTH, BOARD_SIZE)
FPS = 60
 
# Paleta de colores
BG = (24, 28, 38)
BOARD_BG = (34, 40, 54)
GRID = (90, 100, 125)
X_GLOW = (30, 110, 255)        
O_GLOW = (255, 45, 85)            
NEON_CORE = (255, 255, 255)      
HOVER = (46, 54, 72)
WIN_BG = (52, 82, 62)
WIN_LINE = (120, 230, 150)
PANEL_BG = (28, 33, 45)
TEXT = (230, 233, 240)
TEXT_DIM = (140, 148, 166)
BTN = (50, 58, 78)
BTN_HOVER = (68, 78, 104)
BTN_ACTIVE = (70, 110, 190)
 
# Anuncio del ganador 
WINNER_BG = (22, 191, 173)
WINNER_FG = (85, 85, 85)
WINNER_HINT = (12, 120, 108)
WINNER_DELAY_MS = 900             
 
# Botones del panel
MODE_BUTTONS = [
    ("human_vs_human", "Humano vs Humano"),
    ("human_vs_minimax", "Humano vs --"),
    ("human_vs_ml", "Humano vs IA"),
]
RESET_BUTTON = ("reset", "Reiniciar partida")
 

_PX = BOARD_SIZE + 20
_PW = PANEL_WIDTH - 40
BUTTON_RECTS = {
    name: (_PX, 150 + i * 54, _PW, 44) for i, (name, _) in enumerate(MODE_BUTTONS)
}
BUTTON_RECTS[RESET_BUTTON[0]] = (_PX, BOARD_SIZE - 64, _PW, 44)
BUTTON_LABELS = dict(MODE_BUTTONS + [RESET_BUTTON])
 
 
def _inside(pos, rect):
    """True si el punto (x, y) está dentro del rectángulo (x, y, w, h)."""
    x, y = pos
    rx, ry, rw, rh = rect
    return rx <= x < rx + rw and ry <= y < ry + rh
 
 
class GUIView:
    def __init__(self, title="Tres en Raya"):
        pygame.init()
        pygame.display.set_caption(title)
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.SysFont("arial", 26, bold=True)
        self.font_text = pygame.font.SysFont("arial", 18)
        self.font_small = pygame.font.SysFont("arial", 15)
        self.font_btn = pygame.font.SysFont("arial", 17, bold=True)
        self.font_winner = pygame.font.SysFont("arial", 56, bold=True)
        self._sprites = {'X': self._neon_sprite('X'), 'O': self._neon_sprite('O')}
        self._win_since = None          
        self._overlay_visible = False   
 
    # ------------------------------------------------------------------
    # Entrada
    # ------------------------------------------------------------------
    @staticmethod
    def cell_at(pos):
        """Índice 0-8 de la casilla bajo el punto `pos`, o None si está fuera."""
        x, y = pos
        if not (0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE):
            return None
        return (y // CELL_SIZE) * 3 + (x // CELL_SIZE)
 
    @staticmethod
    def button_at(pos):
        """Nombre del botón bajo el punto `pos`, o None."""
        for name, rect in BUTTON_RECTS.items():
            if _inside(pos, rect):
                return name
        return None
 
    def poll_events(self):
        """Lee la cola de Pygame y devuelve una lista de eventos simples."""
        events = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                events.append(("quit",))
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                cell = self.cell_at(event.pos)
                if cell is not None:
                    if self._overlay_visible:
                        events.append(("dismiss",))
                    else:
                        events.append(("cell", cell))
                    continue
                button = self.button_at(event.pos)
                if button is not None:
                    events.append(("button", button))
        return events
 
    # ------------------------------------------------------------------
    # Dibujar
    # ------------------------------------------------------------------
    def render(self, board_state, status_text="", winning_line=None,
               mode=None, metrics=None, winner=None):
        """
        Dibuja un cuadro completo
        """
        mouse = pygame.mouse.get_pos()
        self.screen.fill(BG)
        self._draw_board(board_state, winning_line, mouse)
        self._update_winner_overlay(winner)
        self._draw_panel(status_text, mode, metrics or {}, mouse)
        pygame.display.flip()
        self.clock.tick(FPS)
 
    def _cell_rect(self, index):
        row, col = divmod(index, 3)
        return (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
 
    def _cell_center(self, index):
        x, y, w, h = self._cell_rect(index)
        return (x + w // 2, y + h // 2)
 
    def _draw_board(self, board_state, winning_line, mouse):
        pygame.draw.rect(self.screen, BOARD_BG, (0, 0, BOARD_SIZE, BOARD_SIZE))
 

        hovered = self.cell_at(mouse)
        if hovered is not None and board_state[hovered] == ' ' and not winning_line:
            pygame.draw.rect(self.screen, HOVER, self._cell_rect(hovered))
 
        # Fondo de las casillas ganadoras
        if winning_line:
            for i in winning_line:
                pygame.draw.rect(self.screen, WIN_BG, self._cell_rect(i))
 
        # Líneas de la cuadrícula
        for k in (1, 2):
            pos = k * CELL_SIZE
            pygame.draw.line(self.screen, GRID, (pos, 12), (pos, BOARD_SIZE - 12), 4)
            pygame.draw.line(self.screen, GRID, (12, pos), (BOARD_SIZE - 12, pos), 4)
 
        # Fichas
        for i, symbol in enumerate(board_state):
            sprite = self._sprites.get(symbol)
            if sprite is not None:
                self.screen.blit(sprite, self._cell_rect(i)[:2])
 
        # Línea que atraviesa la jugada ganadora
        if winning_line:
            start = self._cell_center(winning_line[0])
            end = self._cell_center(winning_line[-1])
            pygame.draw.line(self.screen, WIN_LINE, start, end, 8)
 
    def _update_winner_overlay(self, winner):
        """Muestra el anuncio del ganador una vez pasada la pausa inicial."""
        if not winner:
            self._win_since = None
            self._overlay_visible = False
            return
        now = pygame.time.get_ticks()
        if self._win_since is None:
            self._win_since = now
        self._overlay_visible = (now - self._win_since) >= WINNER_DELAY_MS
        if self._overlay_visible:
            self._draw_winner_overlay(winner)
 
    def _draw_winner_overlay(self, winner):
        pygame.draw.rect(self.screen, WINNER_BG, (0, 0, BOARD_SIZE, BOARD_SIZE))
        cx, cy = BOARD_SIZE // 2, 190
        if winner == 'X':
            d = 72
            pygame.draw.line(self.screen, WINNER_FG, (cx - d, cy - d), (cx + d, cy + d), 24)
            pygame.draw.line(self.screen, WINNER_FG, (cx - d, cy + d), (cx + d, cy - d), 24)
        else:
            pygame.draw.circle(self.screen, WINNER_FG, (cx, cy), 80, 24)
        self._text_centered("¡GANADOR!", self.font_winner, WINNER_FG, (cx, 340))
        self._text_centered("Clic para jugar de nuevo", self.font_text, WINNER_HINT, (cx, 410))
 
    def _text_centered(self, text, font, color, center):
        surface = font.render(text, True, color)
        self.screen.blit(surface, (center[0] - surface.get_width() // 2,
                                   center[1] - surface.get_height() // 2))
 
    # ------------------------------------------------------------------
    # Fichas con efecto neón
    # ------------------------------------------------------------------
    def _neon_sprite(self, kind):
        """Superficie transparente de una casilla con la ficha 'X' u 'O' brillante."""
        glow = X_GLOW if kind == 'X' else O_GLOW
        sprite = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
 
        
        for width, alpha in ((40, 18), (32, 30), (25, 50), (19, 80)):
            layer = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            self._draw_stroke(layer, kind, width, (*glow, alpha))
            sprite.blit(layer, (0, 0))
 
        
        self._draw_stroke(sprite, kind, 13, (*glow, 255))
        self._draw_stroke(sprite, kind, 6, NEON_CORE)
        return sprite
 
    @staticmethod
    def _draw_stroke(surface, kind, width, color):
        """Dibuja la forma de la ficha con el grosor y color dados (extremos redondeados)."""
        c = CELL_SIZE // 2
        r = int(CELL_SIZE * 0.33)
        if kind == 'X':
            for a, b in (((c - r, c - r), (c + r, c + r)),
                         ((c - r, c + r), (c + r, c - r))):
                pygame.draw.line(surface, color, a, b, width)
                pygame.draw.circle(surface, color, a, width // 2)
                pygame.draw.circle(surface, color, b, width // 2)
        else:
          
            pygame.draw.circle(surface, color, (c, c), r + width // 2, width)
 
    def _draw_panel(self, status_text, mode, metrics, mouse):
        pygame.draw.rect(self.screen, PANEL_BG, (BOARD_SIZE, 0, PANEL_WIDTH, BOARD_SIZE))
        self._text("Tres en Raya", self.font_title, TEXT, (_PX, 20))
 
        # Estado de la partida
        self._text("ESTADO", self.font_small, TEXT_DIM, (_PX, 66))
        self._text(status_text, self.font_text, TEXT, (_PX, 86))
 
        # Modos de juego
        self._text("MODO DE JUEGO", self.font_small, TEXT_DIM, (_PX, 126))
        for name, label in MODE_BUTTONS:
            self._button(name, label, active=(name == mode), mouse=mouse)
 
        # Métricas de rendimiento 
        self._text("---", self.font_small, TEXT_DIM, (_PX, 322))
        nodes = metrics.get("nodes")
        time_ms = metrics.get("time_ms")
        # self._text("Nodos explorados: " + ("—" if nodes is None else f"{nodes:,}"),
        #           self.font_text, TEXT, (_PX, 344))
        #self._text("Tiempo: " + ("—" if time_ms is None else f"{time_ms:.2f} ms"),
         #          self.font_text, TEXT, (_PX, 368))
 
        self._button(RESET_BUTTON[0], RESET_BUTTON[1], active=False, mouse=mouse)
 
    def _button(self, name, label, active, mouse):
        rect = BUTTON_RECTS[name]
        if active:
            color = BTN_ACTIVE
        elif _inside(mouse, rect):
            color = BTN_HOVER
        else:
            color = BTN
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        surface = self.font_btn.render(label, True, TEXT)
        x, y, w, h = rect
        self.screen.blit(surface, (x + (w - surface.get_width()) // 2,
                                   y + (h - surface.get_height()) // 2))
 
    def _text(self, text, font, color, pos):
        self.screen.blit(font.render(text, True, color), pos)
 
    def close(self):
        pygame.quit()
 
 
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
if __name__ == "__main__":
    view = GUIView()
    sample = ['X', 'O', 'X',
              ' ', 'X', 'O',
              ' ', ' ', 'X']
    mode = "human_vs_human"
    running = True
    while running:
        for ev in view.poll_events():
            print("Evento:", ev)
            if ev[0] == "quit":
                running = False
            elif ev[0] == "button" and ev[1] in BUTTON_LABELS and ev[1] != "reset":
                mode = ev[1]
        view.render(sample, "Juego finalizado", winning_line=[0, 4, 8],
                    mode=mode, metrics={"nodes": None, "time_ms": None},
                    winner='X')
    view.close()