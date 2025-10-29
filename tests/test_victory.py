# tests/test_victory.py
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

# ---------- Single (1 punto): perdedor tiene ≥1 borneadas ----------
def test_victory_single(board, player_white, player_black):
    clear_board(board)
    # White: 14 off + 1 en punto 1 -> necesita dado 1 para terminar
    board.set_count_at(25, "white", 14)
    board.set_count_at(1, "white", 1)

    # Black: ya borneó 1 (single)
    board.set_count_at(25, "black", 1)
    board.set_count_at(12, "black", 14)

    dice = DummyDice()
    dice.reset((1, 3))
    game = BackgammonGame(board, dice, (player_white, player_black), starting_color=player_white.color)
    game.start_turn()
    game.apply_player_move(from_pos=1, steps=1)

    assert game.game_over is True
    assert game.result is not None
    assert game.result.winner_color == "white"
    assert game.result.outcome == "single"
    assert game.result.points == 1

# ---------- Gammon (2 puntos): perdedor no borneó ninguna ----------
def test_victory_gammon(board, player_white, player_black):
    clear_board(board)
    # White va a completar 15-off
    board.set_count_at(25, "white", 14)
    board.set_count_at(1, "white", 1)

    # Black: 0 off, y SIN fichas en el home del ganador ni en BAR (para que no sea backgammon)
    board.set_count_at(12, "black", 15)  # todas fuera del home blanco (1..6) y no en BAR

    dice = DummyDice()
    dice.reset((1, 5))
    game = BackgammonGame(board, dice, (player_white, player_black), starting_color=player_white.color)
    game.start_turn()
    game.apply_player_move(from_pos=1, steps=1)

    assert game.game_over is True
    assert game.result.outcome == "gammon"
    assert game.result.points == 2

# ---------- Backgammon (3 puntos): perdedor no borneó ninguna y tiene fichas en BAR o en home del ganador ----------
def test_victory_backgammon_by_bar(board, player_white, player_black):
    clear_board(board)
    board.set_count_at(25, "white", 14)
    board.set_count_at(1, "white", 1)

    # Black: 0 off y al menos una en BAR
    board.set_count_at(0, "black", 1)     # BAR
    board.set_count_at(12, "black", 14)

    dice = DummyDice()
    dice.reset((1, 2))
    game = BackgammonGame(board, dice, (player_white, player_black), starting_color=player_white.color)
    game.start_turn()
    game.apply_player_move(from_pos=1, steps=1)

    assert game.game_over is True
    assert game.result.outcome == "backgammon"
    assert game.result.points == 3

def test_victory_backgammon_by_checker_in_winner_home(board, player_white, player_black):
    clear_board(board)
    board.set_count_at(25, "white", 14)
    board.set_count_at(1, "white", 1)

    # Black: 0 off y una ficha en el home de white (1..6)
    board.set_count_at(3, "black", 1)
    board.set_count_at(12, "black", 14)

    dice = DummyDice()
    dice.reset((1, 4))
    game = BackgammonGame(board, dice, (player_white, player_black), starting_color=player_white.color)
    game.start_turn()
    game.apply_player_move(from_pos=1, steps=1)

    assert game.game_over is True
    assert game.result.outcome == "backgammon"
    assert game.result.points == 3
