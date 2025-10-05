"""
Tests unitarios para la clase Board del juego de Backgammon.
"""

import pytest
from unittest.mock import MagicMock
import sys
import os

# Agregar el directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.board import Board
from core.checker import Checker
from core.exceptions import InvalidPositionException


class TestBoard:
    """
    Clase de tests para la clase Board.
    """
    
    def setup_method(self):
        """
        Configuración inicial para cada test.
        """
        self.board = Board()
    
    def test_board_initialization(self):
        """
        Test: La inicialización del tablero debe crear 26 posiciones (0-25).
        """
        # Verificar que se pueden obtener todas las posiciones válidas
        for i in range(26):
            assert isinstance(self.board.get_point(i), list)
    
    def test_initial_position_setup(self):
        """
        Test: Las posiciones iniciales deben estar configuradas correctamente.
        """
        # Verificar posiciones iniciales del jugador blanco
        assert len(self.board.get_point(24)) == 2  # 2 fichas blancas en punto 24
        assert len(self.board.get_point(13)) == 5  # 5 fichas blancas en punto 13
        assert len(self.board.get_point(8)) == 3   # 3 fichas blancas en punto 8
        assert len(self.board.get_point(6)) == 5   # 5 fichas blancas en punto 6
        
        # Verificar que todas son blancas
        for position in [24, 13, 8, 6]:
            checkers = self.board.get_point(position)
            for checker in checkers:
                assert checker.get_color() == "white"
        
        # Verificar posiciones iniciales del jugador negro
        assert len(self.board.get_point(1)) == 2   # 2 fichas negras en punto 1
        assert len(self.board.get_point(12)) == 5  # 5 fichas negras en punto 12
        assert len(self.board.get_point(17)) == 3  # 3 fichas negras en punto 17
        assert len(self.board.get_point(19)) == 5  # 5 fichas negras en punto 19
        
        # Verificar que todas son negras
        for position in [1, 12, 17, 19]:
            checkers = self.board.get_point(position)
            for checker in checkers:
                assert checker.get_color() == "black"
        
        # Verificar que bar y off están vacíos inicialmente
        assert len(self.board.get_point(0)) == 0   # Bar vacío
        assert len(self.board.get_point(25)) == 0  # Off vacío