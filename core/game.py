
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple
from typing import Literal
from types import SimpleNamespace
import os


Outcome = Literal["single", "gammon", "backgammon"]

@dataclass(frozen=True)
class GameResult:
    winner_color: str
    loser_color: str
    outcome: Outcome
    points: int


from core.exceptions import BackgammonException

class GameRuleError(BackgammonException):
    """Excepción ..."""
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
     - Si hay fichas en BAR, sólo se puede mover desde BAR (from_pos == self.BAR).
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
            a, b = sorted(remaining)
            can_a = self._legal_single_move_exists(self.current_color, a)
            can_b = self._legal_single_move_exists(self.current_color, b)
            if can_a != can_b:
                must_use = b if can_b else a
                if steps != must_use:
                    raise GameRuleError(
                        f"Debés usar el dado {must_use} al inicio del turno: "
                        "solo uno es jugable y debe ser el más alto."
                    )

        # 1) Ejecutar el movimiento en el board
        if from_pos == self.BAR:
            self.board.reenter_checker(self.current_color, steps)
        else:
            if hasattr(self.board, "move_or_bear_off"):
                self.board.move_or_bear_off(self.current_color, from_pos, steps)
            else:
                self.board.move_checker(self.current_color, from_pos, steps)

        # 2) Consumir el dado
        self.dice.use_move(steps)

        # 3) Victoria inmediata si no quedan fichas en tablero ni en BAR
        left = self._remaining_on_board_or_bar(self.current_color)
        if left == 0:
            self._finalize_game(winner_color=self.current_color)
            return

        # 4) (Opcional) fallback: si tu Board expone off correctamente y llega a 15, también cerrá.
        try:
            if self._get_off_count(self.current_color) == 15:
                self._finalize_game(winner_color=self.current_color)
                return
        except Exception:
            pass




    
    def end_turn(self) -> None:
        if not self._turn_active:
            raise GameRuleError("No hay turno activo para terminar.")

        #  Fallback robusto: si Dice no tiene has_moves(), calculamos desde available_moves
        if hasattr(self.dice, "has_moves") and callable(getattr(self.dice, "has_moves")):
            dice_has_moves = self.dice.has_moves()
        else:
            try:
                am = getattr(self.dice, "available_moves")
                moves = am() if callable(am) else am
                dice_has_moves = bool(moves)
            except Exception:
                dice_has_moves = False

        if dice_has_moves and self._any_legal_move_exists_for_any_die(self.current_color):
            raise GameRuleError(
                "Aún hay movimientos posibles con los dados restantes: debés jugarlos antes de terminar el turno."
            )

        self._turn_active = False
        self.current_color = self._other_color(self.current_color)




    def state(self) -> TurnState:
        _av = self._get_available_moves()
        return TurnState(
            current_color=self.current_color,
            dice_values=tuple(_av),
            moves_left=len(_av),
        )



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
    


    def _check_victory_after_move(self, color: str) -> None:
        """
    Si 'color' tiene 15 fichas en OFF, termina la partida delegando
    el armado del resultado a _finalize_game.
    Estrategia robusta para obtener 'off':
      1) board.count_off(color)
      2) board.count_at(OFF, color)
      3) board.count_checkers(color)['off']
      4) Deducción: 15 - (en_tablero + en_BAR) usando get_point() / get_checkers_in_bar()
    """
        OFF = getattr(self, "OFF", 25)
        off = None

        # 1) count_off(color)
        if hasattr(self.board, "count_off"):
            try:
                off = self.board.count_off(color)
            except Exception:
                off = None

        # 2) count_at(OFF, color)
        if off is None and hasattr(self.board, "count_at"):
            try:
                off = self.board.count_at(OFF, color)
            except Exception:
                off = None
    
        # 3) count_checkers(color).get("off", 0)
        if off is None and hasattr(self.board, "count_checkers"):
            try:
                off = self.board.count_checkers(color).get("off", 0)
            except Exception:
                off = None

        # 4) Deducción: 15 - (en_tablero + en_BAR)
        if off is None:
            on_board = 0
            # usar get_point(p) y filtrar por color
            if hasattr(self.board, "get_point"):
                try:
                    for p in range(1, 25):
                        stack = self.board.get_point(p) or []
                        on_board += sum(1 for ch in stack if getattr(ch, "get_color", lambda: None)() == color)
                except Exception:
                    on_board = 0
            # contar en BAR
            in_bar = 0
            if hasattr(self.board, "get_checkers_in_bar"):
                try:
                    in_bar = len(self.board.get_checkers_in_bar(color) or [])
                except Exception:
                    in_bar = 0
            off = max(0, 15 - (on_board + in_bar))

        if off == 15:
            self._finalize_game(winner_color=color)


    def _get_off_count(self, color: str) -> int:
        """
    Cuenta fichas borneadas (OFF) con múltiples estrategias:
      1) board.count_off(color)
      2) board.count_at(OFF, color)
      3) board.count_checkers(color)['off']
      4) Deducción: 15 - (en_tablero + en_BAR)
         - en_tablero con get_point() y chequeo de color por atributo .color o método .get_color()
         - en_BAR con get_checkers_in_bar(color) o count_bar(color)
    """
        OFF = getattr(self, "OFF", 25)

        # 1) count_off(color)
        if hasattr(self.board, "count_off"):
            try:
                return int(self.board.count_off(color))
            except Exception:
                pass
    
        # 2) count_at(OFF, color)
        if hasattr(self.board, "count_at"):
            try:
                return int(self.board.count_at(OFF, color))
            except Exception:
                pass

        # 3) count_checkers(color)
        if hasattr(self.board, "count_checkers"):
            try:
                d = self.board.count_checkers(color) or {}
                if isinstance(d, dict) and "off" in d:
                    return int(d.get("off", 0))
            except Exception:
                pass

    # 4) Deducción
    # 4a) Fichas en tablero
        on_board = 0
        if hasattr(self.board, "get_point"):
            try:
                for p in range(1, 25):
                    stack = self.board.get_point(p) or []
                    for ch in stack:
                        # soportar .color (atributo) o .get_color() (método)
                        ch_color = getattr(ch, "color", None)
                        if ch_color is None and hasattr(ch, "get_color"):
                            try:
                                ch_color = ch.get_color()
                            except Exception:
                                ch_color = None
                        if ch_color == color:
                            on_board += 1
            except Exception:
                on_board = 0

        # 4b) Fichas en BAR
        in_bar = 0
        if hasattr(self.board, "get_checkers_in_bar"):
            try:
                in_bar = len(self.board.get_checkers_in_bar(color) or [])
            except Exception:
                in_bar = 0
        if in_bar == 0 and hasattr(self.board, "count_bar"):
            try:
                in_bar = int(self.board.count_bar(color))
            except Exception:
                pass

        off = 15 - (on_board + in_bar)
        return off if off >= 0 else 0


    def _remaining_on_board_or_bar(self, color: str) -> int:
        """
    Devuelve cuántas fichas de 'color' quedan en tablero (1..24) + BAR.
    No depende de count_off / count_at; usa get_point y get_checkers_in_bar / count_bar.
    """
        left = 0

    # Contar en tablero 1..24
        if hasattr(self.board, "get_point"):
            try:
                for p in range(1, 25):
                    stack = self.board.get_point(p) or []
                    for ch in stack:
                        ch_color = getattr(ch, "color", None)
                        if ch_color is None and hasattr(ch, "get_color"):
                            try:
                                ch_color = ch.get_color()
                            except Exception:
                                ch_color = None
                        if ch_color == color:
                            left += 1
            except Exception:
                pass

        # Contar en BAR
        if hasattr(self.board, "get_checkers_in_bar"):
            try:
                left += len(self.board.get_checkers_in_bar(color) or [])
            except Exception:
                pass
        elif hasattr(self.board, "count_bar"):
            try:
                left += int(self.board.count_bar(color))
            except Exception:
                pass

        return left



