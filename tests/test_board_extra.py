import pytest
from core.board import Board
from core.checker import Checker
from core.exceptions import InvalidMoveException, InvalidPositionException, NoCheckersAtPositionException

# Helpers
def clear_board(b: Board):
    for p in range(26):
        b.set_count_at(p, "white", 0)
        b.set_count_at(p, "black", 0)

def add_checker(b: Board, pos: int, color: str, n=1):
    for _ in range(n):
        ch = Checker(color, pos)
        b.place_checker(ch, pos)

# ---------- validate_basic_move & bloqueos ----------

def test_validate_basic_move_raises_if_no_own_checker_at_origin():
    b = Board()
    clear_board(b)
    # origen vacío
    with pytest.raises(ValueError):
        b.validate_basic_move("white", from_pos=6, steps=1)

def test_validate_basic_move_destination_blocked():
    b = Board()
    clear_board(b)
    # white intenta ir a un punto con 2 negras = bloqueado
    add_checker(b, 8, "white", 1)
    add_checker(b, 7, "black", 2)  # destino bloqueado si white mueve 1 desde 8
    with pytest.raises(ValueError):
        b.validate_basic_move("white", from_pos=8, steps=1)

# ---------- captura (blot) y _capture_at ----------

def test_move_checker_captures_blot_and_sends_to_bar():
    b = Board()
    clear_board(b)
    # white 8 -> 7 con steps=1 y hay 1 black en 7 => captura a BAR (0)
    add_checker(b, 8, "white", 1)
    add_checker(b, 7, "black", 1)
    from_pos, to_pos, captured = b.move_checker("white", 8, 1)
    assert (from_pos, to_pos) == (8, 7)
    assert captured is not None
    # capturada en BAR
    assert any(ch.get_color() == "black" for ch in b.get_point(0))
    # y en 7 ahora hay white arriba
    assert any(ch.get_color() == "white" for ch in b.get_point(7))

# ---------- can_place_checker / place_checker (BAR/OFF & bloqueos) ----------

def test_place_checker_bar_and_off_always_allowed():
    b = Board()
    clear_board(b)
    w = Checker("white", 0)
    cap = b.place_checker(w, 0)  # BAR
    assert cap is None
    assert any(ch.get_color() == "white" for ch in b.get_point(0))

    w2 = Checker("white", 25)
    cap2 = b.place_checker(w2, 25)  # OFF
    assert cap2 is None
    assert any(ch.get_color() == "white" for ch in b.get_point(25))

def test_can_place_checker_false_when_blocked():
    b = Board()
    clear_board(b)
    add_checker(b, 10, "black", 2)  # bloqueado para white
    assert b.can_place_checker(10, "white") is False
    # punto vacío o propio -> True
    assert b.can_place_checker(11, "white") is True
    add_checker(b, 12, "white", 1)
    assert b.can_place_checker(12, "white") is True

# ---------- reingreso (validate_reentry) ----------

def test_reenter_blocked_raises():
    b = Board()
    clear_board(b)
    # White en BAR y destino 23 (25-2) bloqueado por 2 negras
    add_checker(b, 0, "white", 1)
    add_checker(b, 23, "black", 2)
    with pytest.raises(InvalidMoveException):
        b.reenter_checker("white", 2)

def test_reenter_invalid_die_raises():
    b = Board()
    clear_board(b)
    add_checker(b, 0, "white", 1)
    with pytest.raises(InvalidMoveException):
        b.reenter_checker("white", 0)
    with pytest.raises(InvalidMoveException):
        b.reenter_checker("white", 7)

# ---------- bearing off por ambas direcciones + overshoot ----------

def test_move_or_bear_off_white_and_black_and_overshoot_rules():
    b = Board()
    clear_board(b)
    # White todo en home (1..6). Una en 1 para bornear exacto con 1.
    b.set_count_at(1, "white", 1)
    b.set_count_at(2, "white", 14)
    assert b.all_checkers_in_home_board("white")
    # ruta move_or_bear_off debe detectar fuera de 1..24 y derivar a bearing off
    before_off_w = len(b.get_checkers_off_board("white"))
    b.move_or_bear_off("white", from_pos=1, steps=1)
    after_off_w = len(b.get_checkers_off_board("white"))
    assert after_off_w == before_off_w + 1

    # Black todo en home (19..24). Una en 24 para bornear exacto con 1.
    clear_board(b)
    b.set_count_at(24, "black", 1)
    b.set_count_at(19, "black", 14)
    assert b.all_checkers_in_home_board("black")
    before_off_b = len(b.get_checkers_off_board("black"))
    b.move_or_bear_off("black", from_pos=24, steps=1)
    after_off_b = len(b.get_checkers_off_board("black"))
    assert after_off_b == before_off_b + 1

    # Overshoot permitido para white si no hay fichas en puntos mayores (4..6)
    clear_board(b)
    b.set_count_at(3, "white", 1)
    b.set_count_at(2, "white", 7)
    b.set_count_at(1, "white", 7)
    assert b.all_checkers_in_home_board("white")
    assert b.can_bear_off_from("white", 3, 5) is True
    before = len(b.get_checkers_off_board("white"))
    b.bear_off_checker("white", 3, 5)
    assert len(b.get_checkers_off_board("white")) == before + 1

# ---------- all_checkers_in_home_board (bar y fuera del home) ----------

def test_all_checkers_in_home_board_false_if_bar_or_outside_home():
    b = Board()
    clear_board(b)
    # blanco: una en BAR -> False
    b.set_count_at(0, "white", 1)
    b.set_count_at(1, "white", 14)
    assert b.all_checkers_in_home_board("white") is False

    clear_board(b)
    # blanco: una fuera del home (punto 8) -> False
    b.set_count_at(2, "white", 14)
    b.set_count_at(8, "white", 1)
    assert b.all_checkers_in_home_board("white") is False

# ---------- remove_checker errores & no-op ----------

def test_remove_checker_invalid_and_empty_returns_none():
    b = Board()
    clear_board(b)
    # fuera de rango
    with pytest.raises(InvalidPositionException):
        b.remove_checker(99)
    # en punto vacío -> None
    assert b.remove_checker(6) is None

# ---------- bear_off_checker errores ----------

def test_bear_off_checker_errors_when_not_allowed():
    b = Board()
    clear_board(b)
    # No está todo en home; intentar bornear debe fallar
    b.set_count_at(7, "white", 1)
    b.set_count_at(1, "white", 14)
    with pytest.raises(InvalidMoveException):
        b.bear_off_checker("white", 1, 1)
    # Origen sin ficha propia
    clear_board(b)
    b.set_count_at(1, "white", 1)
    with pytest.raises(InvalidMoveException):
        b.bear_off_checker("white", 2, 1)
