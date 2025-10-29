
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple

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
         - USA el motor del Board:
              * from_pos == 0 -> reenter_checker(color, steps)
              * otro punto      -> move_checker(color, from_pos, steps)
        """
        if not self._turn_active:
            raise GameRuleError("No hay turno activo. Llamá a start_turn() primero.")
        if steps not in self.dice.available_moves():
            raise GameRuleError(f"Dado {steps} no disponible: {self.dice.available_moves()}")

        if self._has_bar(self.current_color) and from_pos != self.BAR:
            raise GameRuleError("Debés reingresar desde el BAR antes de mover otras fichas.")

        if from_pos == self.BAR:
            # Reingreso con validación/captura delegada a Board
            self.board.reenter_checker(self.current_color, steps)
        else:
            # Movimiento normal (M3, sin bearing off)
            self.board.move_checker(self.current_color, from_pos, steps)

        # Consumir dado SIEMPRE al final de un movimiento válido
        self.dice.use_move(steps)

    def end_turn(self) -> None:
        """Termina el turno y alterna el color actual."""
        if not self._turn_active:
            raise GameRuleError("No hay turno activo para terminar.")
        self._turn_active = False
        self.current_color = self._other_color(self.current_color)
        self.turn_number += 1

    def state(self) -> TurnState:
        return TurnState(
            current_color=self.current_color,
            dice_values=tuple(self.dice.available_moves()),
            moves_left=len(self.dice.available_moves()),
        )

