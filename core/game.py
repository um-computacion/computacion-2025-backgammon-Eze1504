
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple
from typing import Literal
from types import SimpleNamespace


Outcome = Literal["single", "gammon", "backgammon"]

@dataclass(frozen=True)
class GameResult:
    winner_color: str
    loser_color: str
    outcome: Outcome
    points: int


class GameRuleError(ValueError):
    """Excepción para violaciones de reglas a nivel juego (flujo de turno, dados, BAR)."""

@dataclass(frozen=True)
class TurnState:
    current_color: str
    dice_values: Tuple[int, ...]
    moves_left: int

class BackgammonGame:
    """
    Orquesta el flujo del turno:
      - inicio/fin de turno
      - prioridad de reingreso desde BAR
      - consumo de dados por movimiento

    Delegamos validaciones duras (bloqueos, captura, etc.) a Board:
      - Reingreso: board.reenter_checker(color, steps)
      - Movimiento normal: board.move_checker(color, from_pos, steps)
      - Estado BAR: board.has_checkers_in_bar(color)
    """

    BAR = 0
    OFF = 25  # (no se usa en M3; bearing off va en M4)

    def __init__(self, board, dice, players: Tuple[object, object], starting_color: Optional[str] = None):
        self.board = board
        self.dice = dice
        self.players = {players[0].color: players[0], players[1].color: players[1]}
        self._order = (players[0].color, players[1].color)
        self.current_color = starting_color or self._order[0]
        self.turn_number = 1
        self._turn_active = False
        self.game_over: bool = False
        self.result: Optional[GameResult] = None
        self._turn_start_dice: Tuple[int, ...] = tuple()




    # ---------------- Utils ----------------
    def _other_color(self, color: str) -> str:
        return "black" if color == "white" else "white"

    def current_player(self):
        return self.players[self.current_color]

    def opponent_player(self):
        return self.players[self._other_color(self.current_color)]

    def _has_bar(self, color: Optional[str] = None) -> bool:
        return bool(self.board.get_checkers_in_bar(color))

    # ---------------- Turno ----------------
    def start_turn(self) -> TurnState:
        """Comienza el turno: (opcional) tira dados si existe dice.roll()."""
        if self._turn_active:
            raise GameRuleError("El turno ya está activo.")
        self._turn_active = True

        if hasattr(self.dice, "roll"):
            self.dice.roll()

        # guardamos una foto de los dados disponibles al inicio (informativo)
        self._turn_start_dice = tuple(self._get_available_moves())
        return self.state()

    

    def can_player_move(self) -> bool:
        """Heurística mínima: si hay dados disponibles, podríamos mover (Board valida)."""
        return bool(self.dice.has_moves())

    def apply_player_move(self, from_pos: int, steps: int) -> None:
        """
    Aplica UNA jugada del jugador actual y consume el dado 'steps'.
    Reglas:
     - Si hay fichas en BAR, sólo se puede mover desde BAR (from_pos == 0).
     - 'steps' debe estar disponible en el dice.
     - Motores del Board:
         * from_pos == self.BAR -> reenter_checker(color, steps)
         * otro punto           -> move_or_bear_off(color, from_pos, steps) si existe, si no move_checker
    """
        if not self._turn_active:
            raise GameRuleError("No hay turno activo. Llamá a start_turn() primero.")
        available = self._get_available_moves()
        if steps not in available:
            raise GameRuleError(f"Dado {steps} no disponible: {available}")
        if self._has_bar(self.current_color) and from_pos != self.BAR:
            raise GameRuleError("Debés reingresar desde el BAR antes de mover otras fichas.")
    
        # Regla del dado más alto si quedan exactamente dos valores distintos y solo uno es jugable.
        remaining = self._get_available_moves()
        if len(remaining) == 2 and remaining[0] != remaining[1]:
            a, b = sorted(remaining)          # a = menor, b = mayor
            can_a = self._legal_single_move_exists(self.current_color, a)
            can_b = self._legal_single_move_exists(self.current_color, b)
            if can_a != can_b:
                must_use = b if can_b else a
                if steps != must_use:
                    raise GameRuleError(
                        f"Debés usar el dado {must_use} al inicio del turno: "
                        "solo uno es jugable y debe ser el más alto."
                    )
    
        # 1) Ejecutar UNA acción de movimiento (puede incluir bearing off)
        if from_pos == self.BAR:
            self.board.reenter_checker(self.current_color, steps)
        else:
            if hasattr(self.board, "move_or_bear_off"):
                self.board.move_or_bear_off(self.current_color, from_pos, steps)
            else:
                self.board.move_checker(self.current_color, from_pos, steps)
    
        # 2) Consumir el dado tras un movimiento válido
        self.dice.use_move(steps)
    
         # 3) Verificar victoria después de consumir el dado
        if self.board.count_checkers(self.current_color).get("off", 0) == 15:
            self._finalize_game(winner_color=self.current_color)
            return
    
        # 4) Re-chequeo de victoria por si el orden del test evalúa luego del consumo
        self._maybe_finalize_if_won(self.current_color)

    def end_turn(self) -> None:
        """Termina el turno y alterna el color actual."""
        if not self._turn_active:
            raise GameRuleError("No hay turno activo para terminar.")
        # Regla: no podés terminar si aún quedan dados jugables
        if self.dice.has_moves() and self._any_legal_move_exists_for_any_die(self.current_color):
            raise GameRuleError("Aún hay movimientos posibles con los dados restantes: debés jugarlos antes de terminar el turno.")
        # cerrar turno y alternar
        self._turn_active = False
        self.current_color = self._other_color(self.current_color)



    def state(self) -> TurnState:
        _av = self._get_available_moves()
        return TurnState(
            current_color=self.current_color,
            dice_values=tuple(_av),
            moves_left=len(_av),
        )

    
    def _maybe_finalize_if_won(self, color: str) -> None:
        counts = self.board.count_checkers(color)
        if counts.get("off", 0) == 15:
            self._finalize_game(winner_color=color)

    def _finalize_game(self, winner_color: str) -> None:
        # early-exit si ya terminó
        if getattr(self, "game_over", False):
            return

        loser_color = self._other_color(winner_color)
        outcome, points = self._determine_outcome(winner_color, loser_color)

        self.game_over = True
        self.result = SimpleNamespace(
            # alias compatibles con distintos tests
            winner=winner_color,
            winner_color=winner_color,
            loser=loser_color,
            loser_color=loser_color,
            outcome=outcome,   # "single" | "gammon" | "backgammon"
            points=points,
        )
    def _determine_outcome(self, winner_color: str, loser_color: str) -> tuple[str, int]:
        """
    Determina single/gammon/backgammon y devuelve (outcome, points).
    Regla usada:
      - single: perdedor ya borneó ≥1 ficha (off > 0) -> 1 punto
      - backgammon: perdedor con 0 off y (≥1 en BAR o ≥1 dentro del home del ganador) -> 3 puntos
      - gammon: perdedor con 0 off y sin fichas en BAR ni en el home del ganador -> 2 puntos
    """
        loser_counts = self.board.count_checkers(loser_color)
        if loser_counts.get("off", 0) > 0:
            return ("single", 1)

        # 0 off: ver BAR o fichas en el home del ganador
        has_bar = self.board.get_checkers_in_bar(loser_color) != []
        home_start, home_end = self.board.get_home_board_range(winner_color)
        has_in_winner_home = any(
            any(ch.get_color() == loser_color for ch in self.board.get_point(p))
            for p in range(home_start, home_end + 1)
        )

        if has_bar or has_in_winner_home:
             return ("backgammon", 3)
        return ("gammon", 2)

    
    def _legal_single_move_exists(self, color: str, steps: int) -> bool:
        """
    ¿Existe una única jugada legal con 'steps' para 'color', sin tocar el estado?
    Respeta prioridad de BAR. Usa solo validadores del Board.
    """
    # Si hay fichas en BAR, solo vale reingreso
        if self._has_bar(color):
            try:
                self.board.validate_reentry(color, steps)
                return True
            except Exception:
                return False

        # Si no hay en BAR: buscar cualquier origen 1..24 con ficha propia que valide
        # (movimiento normal o bearing off)
        for pos in range(1, 25):
            if self.board._has_checker_of_color(pos, color):
            # Movimiento normal
                try:
                    self.board.validate_basic_move(color, pos, steps)
                    return True
                except Exception:
                    pass
                # Bearing off
                try:
                    if hasattr(self.board, "can_bear_off_from") and self.board.can_bear_off_from(color, pos, steps):
                        return True
                except Exception:
                    pass
        return False

    def _any_legal_move_exists_for_any_die(self, color: str) -> bool:
        """
    ¿Existe al menos un movimiento legal con alguno de los dados disponibles?
    (sin mutar el board)
    """
        moves = self._get_available_moves()
        # probar únicos para evitar trabajo duplicado
        for die in sorted(set(moves)):
            if self._legal_single_move_exists(color, die):
                return True
        return False
    
    def _get_available_moves(self) -> list[int]:
        """
    Acceso robusto a los dados: tolera .available_moves (lista/propiedad) o .available_moves() (método).
    """
        am = getattr(self.dice, "available_moves")
        return list(am() if callable(am) else am)






