import pytest
import sys
import os

# Permitir importar desde el paquete core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.board import Board
from core.checker import Checker
from core.exceptions import InvalidPositionException


class TestBoardBasicMoveValidation:
    def setup_method(self):
        self.board = Board()

    def test_white_simple_move_ok(self):
        to_pos = self.board.validate_basic_move("white", from_pos=6, steps=1)
        assert to_pos == 5

    def test_black_simple_move_ok(self):
        to_pos = self.board.validate_basic_move("black", from_pos=1, steps=1)
        assert to_pos == 2

    def test_blocked_destination_is_invalid(self):
        with pytest.raises(ValueError):
            self.board.validate_basic_move("white", from_pos=2, steps=1)

    def test_capture_on_blot_is_allowed(self):
        self.board._Board__points[5].clear()
        self.board._Board__points[5].append(Checker("black", 5))
        to_pos = self.board.validate_basic_move("white", from_pos=6, steps=1)
        assert to_pos == 5

    def test_invalid_steps(self):
        for s in (0, 7, -1):
            with pytest.raises(ValueError):
                self.board.validate_basic_move("white", from_pos=6, steps=s)

    def test_from_pos_must_have_own_checker(self):
        with pytest.raises(ValueError):
            self.board.validate_basic_move("white", from_pos=2, steps=1)
        with pytest.raises(ValueError):
            self.board.validate_basic_move("white", from_pos=1, steps=1)

    def test_positions_out_of_range(self):
        with pytest.raises(InvalidPositionException):
            self.board.validate_basic_move("white", from_pos=0, steps=1)
        with pytest.raises(InvalidPositionException):
            self.board.validate_basic_move("white", from_pos=25, steps=1)
    
    # Para testear destino fuera de rango, agregamos ficha manualmente
    # Usamos _Board__points para acceder al atributo privado
        self.board._Board__points[1].append(Checker("white", 1))
        with pytest.raises(InvalidPositionException):
            self.board.validate_basic_move("white", from_pos=1, steps=1)  # to_pos sería 0