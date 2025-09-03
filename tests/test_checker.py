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

    def test_is_borne_off(self):
        """Test: Verificar si la ficha está fuera del tablero"""
        self.assertFalse(self.white_checker.is_borne_off())
        
        self.white_checker.position = 25
        self.assertTrue(self.white_checker.is_borne_off())
        
        self.white_checker.position = 5
        self.assertFalse(self.white_checker.is_borne_off())

    def test_is_on_board(self):
        """Test: Verificar si la ficha está en el tablero normal"""
        self.assertFalse(self.white_checker.is_on_board())  # position = None
        
        self.white_checker.position = 1
        self.assertTrue(self.white_checker.is_on_board())
        
        self.white_checker.position = 24
        self.assertTrue(self.white_checker.is_on_board())
        
        self.white_checker.position = 0  # Barra
        self.assertFalse(self.white_checker.is_on_board())
        
        self.white_checker.position = 25  # Bear-off
        self.assertFalse(self.white_checker.is_on_board())

    def test_move_to(self):
        """Test: Mover ficha a nueva posición"""
        self.white_checker.position = 5
        old_position = self.white_checker.move_to(10)
        
        self.assertEqual(old_position, 5)
        self.assertEqual(self.white_checker.position, 10)

    def test_move_to_invalid_position(self):
        """Test: Mover a posición inválida debe fallar"""
        self.white_checker.position = 5
        
        with self.assertRaises(ValueError):
            self.white_checker.move_to(-1)

    def test_move_to_bar(self):
        """Test: Mover ficha a la barra"""
        self.white_checker.position = 15
        old_position = self.white_checker.move_to_bar()
        
        self.assertEqual(old_position, 15)
        self.assertEqual(self.white_checker.position, 0)
        self.assertTrue(self.white_checker.is_on_bar())

    def test_bear_off(self):
        """Test: Sacar ficha del tablero"""
        self.white_checker.position = 2
        old_position = self.white_checker.bear_off()
        
        self.assertEqual(old_position, 2)
        self.assertEqual(self.white_checker.position, 25)
        self.assertTrue(self.white_checker.is_borne_off())

    def test_get_home_board_range_white(self):
        """Test: Rango del home board para fichas blancas"""
        start, end = self.white_checker.get_home_board_range()
        self.assertEqual(start, 1)
        self.assertEqual(end, 6)

    def test_get_home_board_range_black(self):
        """Test: Rango del home board para fichas negras"""
        start, end = self.black_checker.get_home_board_range()
        self.assertEqual(start, 19)
        self.assertEqual(end, 24)

    def test_is_in_home_board_white(self):
        """Test: Verificar si ficha blanca está en home board"""
        self.assertFalse(self.white_checker.is_in_home_board())  # Sin posición
        
        self.white_checker.position = 1
        self.assertTrue(self.white_checker.is_in_home_board())
        
        self.white_checker.position = 6
        self.assertTrue(self.white_checker.is_in_home_board())
        
        self.white_checker.position = 7
        self.assertFalse(self.white_checker.is_in_home_board())
        
        self.white_checker.position = 0  # Barra
        self.assertFalse(self.white_checker.is_in_home_board())

    def test_is_in_home_board_black(self):
        """Test: Verificar si ficha negra está en home board"""
        self.assertFalse(self.black_checker.is_in_home_board())  # Sin posición
        
        self.black_checker.position = 19
        self.assertTrue(self.black_checker.is_in_home_board())
        
        self.black_checker.position = 24
        self.assertTrue(self.black_checker.is_in_home_board())
        
        self.black_checker.position = 18
        self.assertFalse(self.black_checker.is_in_home_board())

    def test_str_representation(self):
        """Test: Representación como string"""
        # Sin posición
        expected = "Ficha white - Sin posición"
        self.assertEqual(str(self.white_checker), expected)
        
        # En tablero normal
        self.white_checker.position = 5
        expected = "Ficha white - Punto 5"
        self.assertEqual(str(self.white_checker), expected)
        
        # En barra
        self.white_checker.position = 0
        expected = "Ficha white - En barra"
        self.assertEqual(str(self.white_checker), expected)
        
        # Bear-off
        self.white_checker.position = 25
        expected = "Ficha white - Fuera del tablero"
        self.assertEqual(str(self.white_checker), expected)

    def test_repr_representation(self):
        """Test: Representación técnica"""
        self.white_checker.position = 10
        expected = "Checker(color='white', position=10)"
        self.assertEqual(repr(self.white_checker), expected)

    def test_equality(self):
        """Test: Comparación de igualdad entre fichas"""
        checker1 = Checker("white")
        checker2 = Checker("white")
        checker3 = Checker("black")
        
        checker1.position = 5
        checker2.position = 5
        checker3.position = 5
        
        # Mismas fichas (color y posición)
        self.assertEqual(checker1, checker2)
        
        # Diferentes colores
        self.assertNotEqual(checker1, checker3)
        
        # Diferentes posiciones
        checker2.position = 10
        self.assertNotEqual(checker1, checker2)
        
        # Comparar con objeto diferente
        self.assertNotEqual(checker1, "not a checker")

    def test_hash(self):
        """Test: Hash de las fichas para uso en sets/dicts"""
        checker1 = Checker("white")
        checker2 = Checker("white")
        
        checker1.position = 5
        checker2.position = 5
        
        # Fichas iguales deben tener mismo hash
        self.assertEqual(hash(checker1), hash(checker2))
        
        # Pueden usarse en sets
        checker_set = {checker1, checker2}
        self.assertEqual(len(checker_set), 1)  # Son consideradas la misma ficha

    def test_constants(self):
        """Test: Verificar que las constantes están definidas correctamente"""
        self.assertEqual(Checker.WHITE, "white")
        self.assertEqual(Checker.BLACK, "black")
        self.assertEqual(Checker.BAR_POSITION, 0)
        self.assertEqual(Checker.BEAR_OFF_POSITION, 25)


if __name__ == '__main__':
    # Ejecutar tests con verbose output
    unittest.main(verbosity=2)