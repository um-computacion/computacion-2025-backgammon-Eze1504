import unittest
import sys
import os

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.checker import Checker


class TestChecker(unittest.TestCase):
    """Tests para la clase Checker"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.white_checker = Checker(Checker.WHITE)
        self.black_checker = Checker(Checker.BLACK)

    def test_checker_creation_valid_colors(self):
        """Test: Creación de fichas con colores válidos"""
        white_checker = Checker("white")
        black_checker = Checker("black")
        
        self.assertEqual(white_checker.color, "white")
        self.assertEqual(black_checker.color, "black")
        self.assertIsNone(white_checker.position)
        self.assertIsNone(black_checker.position)

    def test_checker_creation_invalid_color(self):
        """Test: Creación de ficha con color inválido debe fallar"""
        with self.assertRaises(ValueError) as context:
            Checker("red")
        
        self.assertIn("Color inválido", str(context.exception))

    def test_position_property_getter(self):
        """Test: Obtener posición de la ficha"""
        self.assertIsNone(self.white_checker.position)
        
        self.white_checker._position = 5
        self.assertEqual(self.white_checker.position, 5)

    def test_position_property_setter_valid(self):
        """Test: Establecer posición válida"""
        self.white_checker.position = 10
        self.assertEqual(self.white_checker.position, 10)
        
        self.white_checker.position = 0  # Barra
        self.assertEqual(self.white_checker.position, 0)
        
        self.white_checker.position = 25  # Bear-off
        self.assertEqual(self.white_checker.position, 25)
        
        self.white_checker.position = None  # Sin posición
        self.assertIsNone(self.white_checker.position)

    def test_position_property_setter_invalid(self):
        """Test: Establecer posición inválida debe fallar"""
        with self.assertRaises(ValueError):
            self.white_checker.position = -1
        
        with self.assertRaises(ValueError):
            self.white_checker.position = 26
        
        with self.assertRaises(ValueError):
            self.white_checker.position = "invalid"

    def test_is_on_bar(self):
        """Test: Verificar si la ficha está en la barra"""
        self.assertFalse(self.white_checker.is_on_bar())
        
        self.white_checker.position = 0
        self.assertTrue(self.white_checker.is_on_bar())
        
        self.white_checker.position = 5
        self.assertFalse(self.white_checker.is_on_bar())