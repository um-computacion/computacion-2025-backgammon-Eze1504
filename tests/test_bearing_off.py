# tests/test_bearing_off.py
import pytest
from core.board import Board
from core.checker import Checker
from core.game import BackgammonGame, GameRuleError

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

class _DummyPlayer:
    def __init__(self, color: str):
        self.color = color

@pytest.fixture
def player_white():
    return _DummyPlayer("white")

@pytest.fixture
def player_black():
    return _DummyPlayer("black")

@pytest.fixture
def board():
    return Board()

def clear_board(board: Board):
    for p in range(0, 26):
        board.set_count_at(p, "white", 0)
        board.set_count_at(p, "black", 0)

def test_cannot_bear_off_if_not_all_in_home(board):
    # Caso negativo: al inicio NO están todas en home -> False
    assert not board.all_checkers_in_home_board("white")
    assert not board.can_bear_off_from("white", 1, 1)

def test_white_exact_bear_off_from_point_1(board):
    clear_board(board)
    # Todas las 15 blancas en home; ponemos 1 en punto 1 y el resto en 2
    board.set_count_at(1, "white", 1)
    board.set_count_at(2, "white", 14)
    assert board.all_checkers_in_home_board("white")
    # Exacto: desde 1 con dado 1
    moved = board.bear_off_checker("white", 1, 1)
    assert board.count_checkers_at(25, "white") == 1  # OFF
    assert board.count_checkers_at(1, "white") == 0

def test_white_overshoot_allowed_if_no_higher_points(board):
    clear_board(board)
    # Solo blancas en home, todas en 1..3 y ninguna en 4..6
    board.set_count_at(3, "white", 1)   # ficha a sacar
    board.set_count_at(2, "white", 7)
    board.set_count_at(1, "white", 7)
    assert board.all_checkers_in_home_board("white")

    # Desde 3 con dado 5: 3-5 = -2 -> overshoot permitido si no hay fichas en (4..6)
    assert board.can_bear_off_from("white", 3, 5)
    board.bear_off_checker("white", 3, 5)
    assert board.count_checkers_at(25, "white") == 1

def test_white_overshoot_blocked_if_higher_points_exist(board):
    clear_board(board)
    # Hay una blanca en 5 (más lejos), y quiero sacar desde 3 con dado 5
    board.set_count_at(5, "white", 1)   # bloquea overshoot
    board.set_count_at(3, "white", 1)
    board.set_count_at(1, "white", 13)
    assert board.all_checkers_in_home_board("white")
    assert not board.can_bear_off_from("white", 3, 5)
    with pytest.raises(Exception):
        board.bear_off_checker("white", 3, 5)

def test_game_consumes_die_on_bearing_off(board, player_white, player_black):
    clear_board(board)
    board.set_count_at(1, "white", 1)
    board.set_count_at(2, "white", 14)
    dice = DummyDice()
    dice.reset((1, 3))  # usamos el 1 para bearing off desde punto 1
    game = BackgammonGame(board, dice, (player_white, player_black), starting_color=player_white.color)
    game.start_turn()
    game.apply_player_move(from_pos=1, steps=1)  # bearing off
    assert 1 not in game.dice.available_moves()
    assert board.count_checkers_at(25, "white") == 1

