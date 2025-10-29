
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple
from typing import Literal

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
        return self._order[1] if color == self._order[0] else self._order[0]

    def current_player(self):
        return self.players[self.current_color]

    def opponent_player(self):
        return self.players[self._other_color(self.current_color)]

    def _has_bar(self, color: Optional[str] = None) -> bool:
        color = color or self.current_color
        return bool(self.board.has_checkers_in_bar(color))

    # ---------------- Turno ----------------
    def start_turn(self) -> TurnState:
        """Comienza el turno: (opcional) tira dados si existe dice.roll()."""
        if self._turn_active:
            raise GameRuleError("El turno ya está activo.")
        self._turn_active = True
        if hasattr(self.dice, "roll"):
            self.dice.roll()

        self._turn_start_dice = tuple(self.dice.available_moves())

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
         * from_pos == 0 -> reenter_checker(color, steps)
         * otro punto    -> move_or_bear_off(color, from_pos, steps) si existe, si no move_checker
    """
        if not self._turn_active:
            raise GameRuleError("No hay turno activo. Llamá a start_turn() primero.")

        if steps not in self.dice.available_moves():
            raise GameRuleError(f"Dado {steps} no disponible: {self.dice.available_moves()}")

        if self._has_bar(self.current_color) and from_pos != self.BAR:
            raise GameRuleError("Debés reingresar desde el BAR antes de mover otras fichas.")
        
        # Regla: si es el primer movimiento del turno con 2 dados distintos,
        # y solo uno es jugable, debe usarse el MAYOR.
        if tuple(sorted(self.dice.available_moves())) == tuple(sorted(self._turn_start_dice)):
            # Estamos en el primer movimiento del turno (no se usó ningún dado)
            rem = list(self.dice.available_moves())
            # Solo nos importa el caso de dos valores distintos
            if len(rem) == 2 and rem[0] != rem[1]:
                a, b = sorted(rem)           # a = menor, b = mayor
                can_a = self._legal_single_move_exists(self.current_color, a)
                can_b = self._legal_single_move_exists(self.current_color, b)
                if can_a != can_b:
                    must_use = b if can_b else a
                    if steps != must_use:
                        raise GameRuleError(
                        f"Debés usar el dado {must_use} (regla del dado más alto cuando solo uno es jugable)."
                        )


    # Ejecutar UNA sola acción de movimiento
        if from_pos == self.BAR:
        # Reingreso (validación/captura delegado al Board)
            self.board.reenter_checker(self.current_color, steps)
        else:
        # Movimiento normal o bearing off (M4)
            if hasattr(self.board, "move_or_bear_off"):
                self.board.move_or_bear_off(self.current_color, from_pos, steps)
            else:
            # Fallback M3
                self.board.move_checker(self.current_color, from_pos, steps)

    # Consumir dado sólo si el movimiento fue válido
        self.dice.use_move(steps)
        self._maybe_finalize_if_won(self.current_color)



    def end_turn(self) -> None:
        """Termina el turno y alterna el color actual."""
        if not self._turn_active:
            raise GameRuleError("No hay turno activo para terminar.")
        # Regla: no podés terminar si aún quedan dados jugables
        if self.dice.has_moves() and self._any_legal_move_exists_for_any_die(self.current_color):
            raise GameRuleError("Aún hay movimientos posibles con los dados restantes: debés jugarlos antes de terminar el turno.")

        self._turn_active = False
        self.current_color = self._other_color(self.current_color)
        self.turn_number += 1

    def state(self) -> TurnState:
        return TurnState(
            current_color=self.current_color,
            dice_values=tuple(self.dice.available_moves()),
            moves_left=len(self.dice.available_moves()),
        )
    
    def _maybe_finalize_if_won(self, color: str) -> None:
        if self.game_over:
            return

        counts = None
        off = None
        board_ = None
        bar = None

        if hasattr(self.board, "count_checkers"):
            counts = self.board.count_checkers(color)
            off = counts.get("off", 0)
            board_ = counts.get("board", 0)
            bar = counts.get("bar", 0)

        # Fallbacks defensivos (por si tu Board cambia API en el futuro)
        if off is None and hasattr(self.board, "get_checkers_off_board"):
            off = len(self.board.get_checkers_off_board(color))  # debería darte el 15

        if board_ is None:
            # Estimá cantidad en tablero como total - off - bar si tenés 'total'
            if counts and "total" in counts and off is not None and "bar" in counts:
                board_ = counts["total"] - off - counts["bar"]

        if bar is None and hasattr(self.board, "has_checkers_in_bar"):
            bar = 1 if self.board.has_checkers_in_bar(color) else 0

        # --- Condiciones para finalizar ---
        # 1) Regla directa: 15 borneadas
        if off is not None and off >= 15:
            self._finalize_game(winner_color=color)
            return

    # 2) Regla equivalente: no quedan fichas ni en tablero ni en BAR
        if board_ == 0 and bar == 0:
            self._finalize_game(winner_color=color)
            return




    def _finalize_game(self, winner_color: str) -> None:
        loser_color = self._other_color(winner_color)
        outcome, points = self._determine_outcome(winner_color, loser_color)

        self.game_over = True
        self.result = GameResult(
            winner_color=winner_color,
            loser_color=loser_color,
            outcome=outcome,
            points=points,
            )
        self._turn_active = False


    def _determine_outcome(self, winner_color: str, loser_color: str):
        loser_counts = self.board.count_checkers(loser_color)
        loser_off = loser_counts.get("off", 0)

        # Single (1 punto): el perdedor ya sacó ≥ 1 ficha
        if loser_off >= 1:
            return ("single", 1)

        # Gammon / Backgammon (perdedor no sacó ninguna)
        in_bar = self.board.has_checkers_in_bar(loser_color)

        home_start, home_end = self.board.get_home_board_range(winner_color)
        in_winner_home = any(
            self.board.count_checkers_at(pos, loser_color) > 0
            for pos in range(home_start, home_end + 1)
    )

        # Backgammon (3 puntos): perdedor sin off y con ficha en BAR o en home del ganador
        if in_bar or in_winner_home:
            return ("backgammon", 3)

        # Gammon (2 puntos)
        return ("gammon", 2)
    
    def _legal_single_move_exists(self, color: str, die: int) -> bool:
        """¿Existe al menos 1 movimiento legal con este valor de dado?"""
        # Si hay fichas en BAR, solo reingreso
        if self.board.has_checkers_in_bar(color):
            try:
                # Si no levanta excepción, es jugable
                self.board.validate_reentry(color, die)
                return True
            except Exception:
                return False

        # Sin BAR: intentar cualquier ficha del color
        for pos in range(1, 25):
            # ¿hay ficha propia en pos?
            try:
                pile_count = self.board.count_checkers_at(pos, color)
            except Exception:
                pile_count = 0
            if pile_count <= 0:
                continue

            # Bearing off posible
            try:
                if hasattr(self.board, "can_bear_off_from") and self.board.can_bear_off_from(color, pos, die):
                    return True
            except Exception:
                pass

            # Movimiento dentro del tablero
            try:
                # Si no lanza, es jugable (tu validate_basic_move controla bloqueos y rango)
                self.board.validate_basic_move(color, pos, die)
                return True
            except Exception:
                continue

        return False

    def _any_legal_move_exists_for_any_die(self, color: str) -> bool:
        """¿Existe algún movimiento legal con cualquiera de los dados restantes?"""
        # Evaluá por cada valor único aún disponible
        try:
            remaining = list(self.dice.available_moves())
        except Exception:
            remaining = []
        for v in sorted(set(remaining), reverse=True):
            if self._legal_single_move_exists(color, v):
                return True
        return False





