# tests/test_dice_usage.py
import pytest
from core.board import Board
from core.game import BackgammonGame, GameRuleError
from core.checker import Checker

class DummyDice:
    def __init__(self):
        self._vals = []
    def reset(self, pair):
        a, b = pair
        if a == b:
            self._vals = [a, a, a, a]
        else:
            self._vals = [a, b]
    def available_moves(self):
        return list(self._vals)
    def use_move(self, v):
        self._vals.remove(v)
    def has_moves(self):
        return bool(self._vals)

class _P:
    def __init__(self, color): self.color = color

@pytest.fixture
def W(): return _P("white")

@pytest.fixture
def B(): return _P("black")

@pytest.fixture
def board():
    return Board()

def clear_board(board: Board):
    for p in range(26):
        board.set_count_at(p, "white", 0)
        board.set_count_at(p, "black", 0)

def put_on_bar(board: Board, color: str, n=1):
    for _ in range(n):
        board.place_checker(Checker(color, 0), 0)

def test_higher_die_must_be_used_if_only_one_is_playable(board, W, B):
    # Escenario: white con 2 y 5, solo el 5 permite reingresar (o mover)
    # Forzamos BAR y bloqueamos la entrada del 2.
    clear_board(board)
    put_on_bar(board, "white", 1)
    # Bloquear destino de 2 para white: destino reingreso = 25-2 = 23
    # Ponemos 2 fichas negras en 23 para bloquear
    board.set_count_at(23, "black", 2)

    dice = DummyDice(); dice.reset((2,5))
    g = BackgammonGame(board, dice, (W, B), starting_color=W.color)
    g.start_turn()

    # Intentar usar el 2 (menor) debería fallar: solo es jugable el 5
    with pytest.raises(GameRuleError):
        g.apply_player_move(from_pos=0, steps=2)

    # Con el 5 sí debe dejar
    g.apply_player_move(from_pos=0, steps=5)

def test_must_use_all_possible_dice_before_ending_turn(board, W, B):
    # White con 3 y 5, ambos jugables (reingreso posible a 22 y 20)
    clear_board(board)
    put_on_bar(board, "white", 2)  # dos reingresos posibles

    dice = DummyDice(); dice.reset((3,5))
    g = BackgammonGame(board, dice, (W, B), starting_color=W.color)
    g.start_turn()

    # Reingresa con 3
    g.apply_player_move(from_pos=0, steps=3)
    # Queda el 5 y es jugable -> no debería permitir terminar turno
    with pytest.raises(GameRuleError):
        g.end_turn()

    # Usamos el 5 y ahora sí debe permitir terminar
    g.apply_player_move(from_pos=0, steps=5)
    g.end_turn()

def test_doubles_play_as_many_as_possible(board, W, B):
    # Dobles de 4: intentar usar menos de los que se puede no debe permitir terminar
    clear_board(board)
    put_on_bar(board, "white", 3)  # al menos 3 entradas posibles con 4
    dice = DummyDice(); dice.reset((4,4))
    g = BackgammonGame(board, dice, (W, B), starting_color=W.color)
    g.start_turn()

    # Primer reingreso
    g.apply_player_move(from_pos=0, steps=4)
    # Segundo reingreso
    g.apply_player_move(from_pos=0, steps=4)

    # Todavía hay jugadas posibles con 4 (queda al menos 1 ficha en BAR)
    with pytest.raises(GameRuleError):
        g.end_turn()

    # Tercer reingreso
    g.apply_player_move(from_pos=0, steps=4)

    # Cuarta jugada: ya no hay fichas en BAR; movemos una de 21 -> 17 con 4
    g.apply_player_move(from_pos=21, steps=4)
    g.end_turn()

