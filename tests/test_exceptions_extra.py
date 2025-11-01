import pytest
from core.board import Board
from core.game import BackgammonGame, GameRuleError
from core.dice import Dice
from core.player import Player
from core.exceptions import (
    BackgammonException,
    PlayerException,
    InvalidPlayerNameException,
    InvalidPlayerColorException,
    NoCheckersAtPositionException,
    NegativeScoreException,
    CheckerException,
    InvalidCheckerColorException,
    InvalidPositionException,
    CheckerNotMovableException,
    DiceException,
    InvalidDiceValueException,
    DiceNotRolledException,
    NoMovesAvailableException,
    InvalidMoveException,
    CommandParseError,
)


# -------------------- Tests de errores del flujo de juego --------------------
def test_invalid_move_raises():
    board = Board()
    with pytest.raises(Exception):
        board.move_checker("white", 30, 1)  # fuera de rango


def test_start_turn_twice_raises():
    b = Board()
    d = Dice()
    p1, p2 = Player("P1", "white"), Player("P2", "black")
    g = BackgammonGame(b, d, (p1, p2))
    g.start_turn()
    with pytest.raises(GameRuleError):
        g.start_turn()


def test_end_turn_without_start_raises():
    b = Board()
    d = Dice()
    p1, p2 = Player("P1", "white"), Player("P2", "black")
    g = BackgammonGame(b, d, (p1, p2))
    with pytest.raises(GameRuleError):
        g.end_turn()


# Dummy dice para pruebas controladas
class _DummyDice:
    def __init__(self, vals):
        self._vals = list(vals)

    def roll(self):  # no hace nada
        pass

    def available_moves(self):
        return list(self._vals)

    def use_move(self, v):
        self._vals.remove(v)

    def has_moves(self):
        return bool(self._vals)


def test_apply_move_with_invalid_die():
    b = Board()
    d = _DummyDice([1, 2])  # dados disponibles: 1 y 2
    p1, p2 = Player("P1", "white"), Player("P2", "black")
    g = BackgammonGame(b, d, (p1, p2), starting_color="white")
    g.start_turn()
    with pytest.raises(GameRuleError):
        g.apply_player_move(from_pos=1, steps=6)  # 6 no disponible


# -------------------- Tests específicos de exceptions.py --------------------
def test_backgammon_exception_str_with_code():
    e = BackgammonException("msg", error_code="X1")
    s = str(e)
    assert "[X1]" in s and "msg" in s


def test_invalid_player_color_with_valids():
    e = InvalidPlayerColorException("azul", valid_colors=["white", "black"])
    s = str(e)
    assert "inválido" in s or "inválida" in s
    assert "white" in s and "black" in s


def test_no_checkers_at_position_has_detail():
    e = NoCheckersAtPositionException("W", 13)
    s = str(e)
    assert "W" in s and "13" in s


def test_negative_score_exception_message():
    e = NegativeScoreException(-5)
    assert "-5" in str(e)


def test_invalid_checker_color_message():
    e = InvalidCheckerColorException("verde")
    assert "inválido" in str(e) or "inválida" in str(e)


def test_invalid_position_exception_message():
    e = InvalidPositionException(99, "0-25")
    s = str(e)
    assert "99" in s and "0-25" in s


def test_checker_not_movable_exception_message():
    e = CheckerNotMovableException("C1", "bloqueada")
    s = str(e)
    assert "C1" in s and "bloqueada" in s


def test_invalid_dice_value_with_number():
    e = InvalidDiceValueException(7, dice_number=2)
    s = str(e)
    assert "dado" in s


def test_dice_not_rolled_exception_default():
    e = DiceNotRolledException()
    assert "dados" in str(e).lower()


def test_no_moves_available_with_list():
    e = NoMovesAvailableException([1, 2])
    s = str(e)
    assert "1" in s and "2" in s


def test_no_moves_available_default():
    e = NoMovesAvailableException()
    assert "No quedan movimientos disponibles" in str(e)


def test_invalid_move_exception_with_and_without_position():
    e1 = InvalidMoveException("Fuera de rango", position=30)
    e2 = InvalidMoveException("Otro")
    assert "posición" in str(e1)
    assert "Otro" in str(e2)


def test_command_parse_error_is_value_error():
    with pytest.raises(ValueError):
        raise CommandParseError("boom")
