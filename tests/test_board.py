
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