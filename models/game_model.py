EMPTY = ' '
class GameModel:
    SIZE = 3
 
    def __init__(self, player_one='X', player_two='O'):
        self.players = (player_one, player_two)
        self.board = []
        self.current_player = player_one
        self.reset()
 
    
    def reset(self):
        """Reinicia el tablero y devuelve el turno al primer jugador."""
        self.board = [[EMPTY] * self.SIZE for _ in range(self.SIZE)]
        self.current_player = self.players[0]
 
    def opponent(self, player):
        """Devuelve el símbolo del jugador contrario."""
        return self.players[1] if player == self.players[0] else self.players[0]
 
    def get_board_state(self):
        """Tablero aplanado (lista de 9 elementos). Útil para vista y ML."""
        return [cell for row in self.board for cell in row]
 
    def copy(self):
        """Copia independiente del modelo (útil para simulaciones)."""
        clone = GameModel(*self.players)
        clone.board = [row[:] for row in self.board]
        clone.current_player = self.current_player
        return clone
 
    # ------------------------------------------------------------------
    # Conversión 
    # ------------------------------------------------------------------
    @classmethod
    def _to_row_col(cls, move):
        return divmod(move, cls.SIZE)
 
    @classmethod
    def _is_valid_index(cls, move):
        return isinstance(move, int) and 0 <= move < cls.SIZE * cls.SIZE
 
    # ------------------------------------------------------------------
    # Movimientos
    # ------------------------------------------------------------------
    def is_valid_move(self, move):
        """True si el índice está en rango y la casilla está vacía."""
        if not self._is_valid_index(move):
            return False
        row, col = self._to_row_col(move)
        return self.board[row][col] == EMPTY
 
    def get_available_moves(self):
        """Lista de índices (0-8) de las casillas vacías."""
        return [i for i in range(self.SIZE * self.SIZE) if self.is_valid_move(i)]
 
    def make_move(self, move, player=None):
        """
        Coloca la ficha de `player` 
        Devuelve True si el movimiento fue válido y se aplicó.
        Después de mover, el turno pasa al oponente.
        """
        if player is None:
            player = self.current_player
        if not self.is_valid_move(move):
            return False
        row, col = self._to_row_col(move)
        self.board[row][col] = player
        self.current_player = self.opponent(player)
        return True
 
    def undo_move(self, move):
        """
        BACKTRACKING: deshace el movimiento en `move` y restaura el turno
        al jugador que había colocado esa ficha.
        Devuelve True si había algo que deshacer.
        """
        if not self._is_valid_index(move):
            return False
        row, col = self._to_row_col(move)
        player = self.board[row][col]
        if player == EMPTY:
            return False
        self.board[row][col] = EMPTY
        self.current_player = player
        return True
 
    # ------------------------------------------------------------------
    # Condiciones de fin de partida
    # ------------------------------------------------------------------
    def _all_lines(self):
        """Las 8 líneas ganadoras: 3 filas, 3 columnas y 2 diagonales."""
        n = self.SIZE
        rows = [self.board[r] for r in range(n)] 
        cols = [[self.board[r][c] for r in range(n)] for c in range(n)]
        diag = [self.board[i][i] for i in range(n)]
        anti = [self.board[i][n - 1 - i] for i in range(n)]
        return rows + cols + [diag, anti]
 
    def check_winner(self, player):
        """True si `player` completó alguna fila, columna o diagonal."""
        return any(all(cell == player for cell in line) for line in self._all_lines())
 
    def get_winner(self):
        """Devuelve el símbolo ganador o None si aún no hay ganador."""
        for player in self.players:
            if self.check_winner(player):
                return player
        return None
 
    def get_winning_line(self):
        """
        Devuelve los índices (0-8) de la línea ganadora o None.
        La vista puede usarlo para resaltar la jugada ganadora.
        """
        n = self.SIZE
        lines = (
            [[r * n + c for c in range(n)] for r in range(n)]
            + [[r * n + c for r in range(n)] for c in range(n)]
            + [[i * n + i for i in range(n)], [i * n + (n - 1 - i) for i in range(n)]]
        )
        flat = self.get_board_state()
        for line in lines:
            first = flat[line[0]]
            if first != EMPTY and all(flat[i] == first for i in line):
                return line
        return None
 
    def is_draw(self):
        """Empate: tablero lleno y sin ganador."""
        return not self.get_available_moves() and self.get_winner() is None
 
    def is_game_over(self):
        return self.get_winner() is not None or self.is_draw()
 
    def __str__(self):
        sep = '\n-----------\n'
        return sep.join(' ' + ' | '.join(row) for row in self.board)