import pytest
from types import SimpleNamespace

from core.game import BackgammonGame, GameRuleError
from core.board import Board
from core.dice import Dice
from core.player import Player
from core.exceptions import InvalidPlayerNameException, InvalidMoveException


def make_game():
    board = Board()
    dice = Dice()
    white = Player("White", "white")
    black = Player("Black", "black")
    return BackgammonGame(board, dice, (white, black), starting_color="white")


def test_cannot_start_turn_twice():
    g = make_game()
    g.start_turn()
    with pytest.raises(GameRuleError):
        g.start_turn()


def test_cannot_move_without_turn():
    g = make_game()
    with pytest.raises(GameRuleError):
        g.apply_player_move(1, 2)


def test_cannot_use_unavailable_die():
    g = make_game()
    g.start_turn()
    # Reemplazamos el dado real por un dummy que expone la interfaz mínima requerida:
    # _get_available_moves acepta atributo 'available_moves' como lista o como callable.
    g.dice = SimpleNamespace(
        available_moves=[1],      # sólo está disponible el 1
        has_moves=lambda: True,   # simula que aún hay movimientos
        use_move=lambda v: None,  # no hace nada
    )
    with pytest.raises(GameRuleError):
        g.apply_player_move(1, 3)  # intenta usar 3 (no disponible) => debe fallar


def test_determine_outcome_single(monkeypatch):
    g = make_game()
    # El perdedor tiene al menos una ficha off
    g.board.count_checkers = lambda color: {"off": 2}
    assert g._determine_outcome("white", "black") == ("single", 1)


def test_determine_outcome_gammon(monkeypatch):
    g = make_game()
    g.board.count_checkers = lambda c: {"off": 0}
    g.board.get_checkers_in_bar = lambda c: []
    g.board.get_home_board_range = lambda c: (1, 6)
    g.board.get_point = lambda p: []
    assert g._determine_outcome("white", "black") == ("gammon", 2)


def test_determine_outcome_backgammon(monkeypatch):
    g = make_game()
    g.board.count_checkers = lambda c: {"off": 0}
    g.board.get_checkers_in_bar = lambda c: [1]
    g.board.get_home_board_range = lambda c: (1, 6)
    g.board.get_point = lambda p: []
    assert g._determine_outcome("white", "black") == ("backgammon", 3)


def test_invalid_player_name_message():
    err = InvalidPlayerNameException("")
    assert "inválido" in str(err)


def test_invalid_move_with_position():
    err = InvalidMoveException("Fuera de rango", 30)
    assert "posición" in str(err)
