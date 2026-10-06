class GameController:
    MODE_HUMAN = "human_vs_human"
    MODE_MINIMAX = "human_vs_minimax"
    MODE_ML = "human_vs_ml"
 
    
    AVAILABLE_MODES = {MODE_HUMAN}
 
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.mode = self.MODE_HUMAN
        self.notice = ""                                  
        self.metrics = {"nodes": None, "time_ms": None}   
 
    # ------------------------------------------------------------------
    # Ciclo principal
    # ------------------------------------------------------------------
    def run(self):
        running = True
        self.update_view()
        while running:
            for event in self.view.poll_events():
                if not self.handle_event(event):
                    running = False
            self.update_view()
        self.view.close()
 
    def handle_event(self, event):
        """Procesa un evento de la vista. Devuelve False si hay que salir."""
        kind = event[0]
        if kind == "quit":
            return False
        if kind == "cell":
            self.on_cell_clicked(event[1])
        elif kind == "button":
            self.on_button_clicked(event[1])
        elif kind == "dismiss":
            self.reset_game()        
        return True
 
    # ------------------------------------------------------------------
    # Acciones del usuario 
    # ------------------------------------------------------------------
    def on_cell_clicked(self, index):
        if self.model.is_game_over():
            self.notice = "Partida terminada"
            return
        if not self.model.make_move(index):
            self.notice = "Casilla ocupada"
            return
        self.notice = ""
 
    def on_button_clicked(self, name):
        if name == "reset":
            self.reset_game()
        elif name in self.AVAILABLE_MODES:
            self.mode = name
            self.reset_game()
        else:
            self.notice = "Modo aún no disponible"
 
    def reset_game(self):
        self.model.reset()
        self.notice = ""
        self.metrics = {"nodes": None, "time_ms": None}
 
    # ------------------------------------------------------------------
    # Estado hacia la vista
    # ------------------------------------------------------------------
    def status_text(self):
        if self.model.get_winner():
            return "Juego finalizado"   
        if self.model.is_draw():
            return "Empate"
        if self.notice:
            return self.notice
        return f"Turno de {self.model.current_player}"
 
    def update_view(self):
        self.view.render(
            self.model.get_board_state(),
            self.status_text(),
            winning_line=self.model.get_winning_line(),
            mode=self.mode,
            metrics=self.metrics,
            winner=self.model.get_winner(),
        )