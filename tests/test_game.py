
import pytest
from core.game import BackgammonGame, GameRuleError
from core.board import Board
from core.checker import Checker

@pytest.fixture
def board():
    return Board()

class _DummyPlayer:
    def __init__(self, color: str):
        self.color = color

@pytest.fixture
def player_white():
    return _DummyPlayer("white")

@pytest.fixture
def player_black():
    return _DummyPlayer("black")

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


@pytest.fixture
def dice_pair():
    d = DummyDice()
    d.reset((2, 6))
    return d

@pytest.fixture
def dice_double():
    d = DummyDice()
    d.reset((4, 4))
    return d

@pytest.fixture
def game_pair(board, player_white, player_black, dice_pair):
    return BackgammonGame(board, dice_pair, (player_white, player_black), starting_color=player_white.color)

@pytest.fixture
def game_double(board, player_white, player_black, dice_double):
    return BackgammonGame(board, dice_double, (player_white, player_black), starting_color=player_white.color)

def put_checker_on_bar(board: Board, color: str, n=1):
    for _ in range(n):
        board.place_checker(Checker(color, 0), 0)

def test_start_turn_sets_state(game_pair, player_white, dice_pair):
    st = game_pair.start_turn()
    assert st.current_color == player_white.color
    assert sorted(st.dice_values) == sorted(dice_pair.available_moves())
    assert st.moves_left == len(dice_pair.available_moves())

def test_bar_priority_enforced(board, game_pair, player_white):
    game_pair.start_turn()
    put_checker_on_bar(board, player_white.color)
    with pytest.raises(GameRuleError):
        game_pair.apply_player_move(from_pos=6, steps=2)

def test_reentry_consumes_die(board, game_pair, player_white):
    game_pair.start_turn()
    put_checker_on_bar(board, player_white.color)
    game_pair.apply_player_move(from_pos=0, steps=2)
    assert 2 not in game_pair.dice.available_moves()

def test_doubles_allow_four_moves(board, game_double, player_white):
    game_double.start_turn()
    put_checker_on_bar(board, player_white.color, n=4)
    for _ in range(4):
        game_double.apply_player_move(from_pos=0, steps=4)
    assert not game_double.dice.has_moves()

def test_end_turn_switches_player(game_pair, player_black):
    game_pair.start_turn()
    # Vaciar dados para poder terminar el turno sin jugadas pendientes
    if hasattr(game_pair.dice, "_vals"):
        game_pair.dice._vals = []
    game_pair.end_turn()
    assert game_pair.current_color == player_black.color
