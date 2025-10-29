import pytest
from core.board import Board
from core.checker import Checker
from core.exceptions import InvalidMoveException

# Helpers
def clear_board(b: Board):
    for p in range(26):
        b.set_count_at(p, "white", 0)
        b.set_count_at(p, "black", 0)

def put_checker(b: Board, pos: int, color: str, n=1):
    for _ in range(n):
        ch = Checker(color, pos)
        b.place_checker(ch, pos)

def test_get_point_returns_copy_immutable():
    b = Board()
    clear_board(b)
    put_checker(b, 6, "white", 1)
    lst = b.get_point(6)
    lst.append(Checker("white", 6))   # modifico la copia
    # el tablero no debe cambiar
    assert len(b.get_point(6)) == 1

def test_reentry_blocked_then_capturing_reentry_succeeds():
    b = Board()
    clear_board(b)
    # White tiene 1 en BAR
    put_checker(b, 0, "white", 1)

    # Reingreso con steps=1 => destino 24 (para white)
    # Bloqueado por 2 negras en 24
    put_checker(b, 24, "black", 2)
    with pytest.raises(InvalidMoveException):
        b.reenter_checker("white", steps=1)

    # Desbloqueo: dejo blot (1 negra) para que sea capturable
    b.set_count_at(24, "black", 1)
    # Reingreso ahora debe capturar y mandar la negra al BAR (0)
    from_pos, to_pos, captured = b.reenter_checker("white", steps=1)
    assert (from_pos, to_pos) == (0, 24)
    assert captured is not None
    # la capturada quedó en BAR como negra
    bar_blacks = [c for c in b.get_point(0) if c.get_color() == "black"]
    assert len(bar_blacks) == 1

def test_move_or_bear_off_branch_for_black_exact_bear_off():
    b = Board()
    clear_board(b)
    # Negro con todas en home (19..24); ponemos 15 en 24 para simplificar
    b.set_count_at(24, "black", 15)
    # Movimiento 24 + 1 => fuera del tablero (bearing off exacto)
    before_off = len(b.get_checkers_off_board("black"))
    b.move_or_bear_off("black", from_pos=24, steps=1)
    after_off = len(b.get_checkers_off_board("black"))
    assert after_off == before_off + 1

def test_can_place_checker_blocked_is_false_for_opponent():
    b = Board()
    clear_board(b)
    # Dos negras en 10 bloquean a white
    put_checker(b, 10, "black", 2)
    assert b.can_place_checker(10, "white") is False
    # En BAR y OFF siempre se puede
    assert b.can_place_checker(0, "white") is True
    assert b.can_place_checker(25, "white") is True

def test_all_checkers_in_home_board_false_if_any_on_bar():
    b = Board()
    clear_board(b)
    # todas las blancas en home, pero 1 en BAR
    b.set_count_at(1, "white", 14)
    b.set_count_at(0, "white", 1)
    assert b.all_checkers_in_home_board("white") is False

