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

        def test_is_valid_position(self):
           """
        Test: Validación de posiciones del tablero.
        """
        # Posiciones válidas
        for i in range(26):
            assert self.board.is_valid_position(i) is True
        
        # Posiciones inválidas
        invalid_positions = [-1, -5, 26, 30, 100]
        for pos in invalid_positions:
            assert self.board.is_valid_position(pos) is False
    
    def test_get_point_invalid_position(self):
        """
        Test: Obtener un punto con posición inválida debe lanzar excepción.
        """
        with pytest.raises(InvalidPositionException):
            self.board.get_point(-1)
        
        with pytest.raises(InvalidPositionException):
            self.board.get_point(26)
        
        with pytest.raises(InvalidPositionException):
            self.board.get_point(100)
    
    def test_get_point_returns_copy(self):
        """
        Test: get_point debe retornar una copia para evitar modificaciones externas.
        """
        original_checkers = self.board.get_point(1)
        original_count = len(original_checkers)
        
        # Modificar la lista retornada
        returned_checkers = self.board.get_point(1)
        returned_checkers.clear()
        
        # Verificar que el tablero no fue afectado
        assert len(self.board.get_point(1)) == original_count

    def test_is_point_occupied_by_opponent(self):
        """
        Test: Verificar si un punto está ocupado por el oponente.
        """
        # Punto 1 tiene fichas negras, debe estar ocupado por oponente para blanco
        assert self.board.is_point_occupied_by_opponent(1, "white") is True
        assert self.board.is_point_occupied_by_opponent(1, "black") is False
        
        # Punto 6 tiene fichas blancas, debe estar ocupado por oponente para negro
        assert self.board.is_point_occupied_by_opponent(6, "black") is True
        assert self.board.is_point_occupied_by_opponent(6, "white") is False
        
        # Punto vacío no está ocupado por nadie
        assert self.board.is_point_occupied_by_opponent(2, "white") is False
        assert self.board.is_point_occupied_by_opponent(2, "black") is False
    
    def test_is_point_occupied_by_opponent_invalid_position(self):
        """
        Test: is_point_occupied_by_opponent con posición inválida debe lanzar excepción.
        """
        with pytest.raises(InvalidPositionException):
            self.board.is_point_occupied_by_opponent(-1, "white")
        
        with pytest.raises(InvalidPositionException):
            self.board.is_point_occupied_by_opponent(26, "black")
    
    def test_is_point_blocked(self):
        """
        Test: Verificar si un punto está bloqueado (2+ fichas del oponente).
        """
        # Punto 6 tiene 5 fichas blancas, está bloqueado para negro
        assert self.board.is_point_blocked(6, "black") is True
        assert self.board.is_point_blocked(6, "white") is False
        
        # Punto 1 tiene 2 fichas negras, está bloqueado para blanco
        assert self.board.is_point_blocked(1, "white") is True
        assert self.board.is_point_blocked(1, "black") is False
        
        # Punto vacío no está bloqueado
        assert self.board.is_point_blocked(2, "white") is False
        assert self.board.is_point_blocked(2, "black") is False
    
    def test_is_point_blocked_invalid_position(self):
        """
        Test: is_point_blocked con posición inválida debe lanzar excepción.
        """
        with pytest.raises(InvalidPositionException):
            self.board.is_point_blocked(-1, "white")
        
        with pytest.raises(InvalidPositionException):
            self.board.is_point_blocked(26, "black")
    
    def test_can_place_checker(self):
        """
        Test: Verificar si se puede colocar una ficha en una posición.
        """
        # Se puede colocar en punto vacío
        assert self.board.can_place_checker(2, "white") is True
        assert self.board.can_place_checker(2, "black") is True
        
        # Se puede colocar en punto propio
        assert self.board.can_place_checker(6, "white") is True
        assert self.board.can_place_checker(1, "black") is True
        
        # No se puede colocar en punto bloqueado por oponente
        assert self.board.can_place_checker(6, "black") is False
        assert self.board.can_place_checker(1, "white") is False
        
        # Posición inválida
        assert self.board.can_place_checker(-1, "white") is False
        assert self.board.can_place_checker(26, "black") is False
    