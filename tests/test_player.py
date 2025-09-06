import unittest
import sys
import os

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.player import Player
from core.checker import Checker


class TestPlayer(unittest.TestCase):
    """Tests para la clase Player"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.player_white = Player("Alice", Checker.WHITE)
        self.player_black = Player("Bob", Checker.BLACK)

    def test_player_creation_valid(self):
        """Test: Creación válida de jugador"""
        player = Player("TestPlayer", Checker.WHITE)
        
        self.assertEqual(player.name, "TestPlayer")
        self.assertEqual(player.color, Checker.WHITE)
        self.assertEqual(player.score, 0)
        self.assertEqual(player.games_won, 0)
        self.assertEqual(len(player.checkers), Player.TOTAL_CHECKERS)

    def test_player_creation_name_strip(self):
        """Test: Creación con nombre que necesita strip"""
        player = Player("  TestPlayer  ", Checker.WHITE)
        self.assertEqual(player.name, "TestPlayer")

    def test_player_creation_invalid_name(self):
        """Test: Creación con nombre inválido debe fallar"""
        with self.assertRaises(ValueError) as context:
            Player("", Checker.WHITE)
        self.assertIn("nombre del jugador no puede estar vacío", str(context.exception))
        
        with self.assertRaises(ValueError):
            Player("   ", Checker.WHITE)
        
        with self.assertRaises(ValueError):
            Player(None, Checker.WHITE)

    def test_player_creation_invalid_color(self):
        """Test: Creación con color inválido debe fallar"""
        with self.assertRaises(ValueError) as context:
            Player("TestPlayer", "red")
        self.assertIn("Color inválido", str(context.exception))

    def test_checkers_creation(self):
        """Test: Creación automática de fichas"""
        self.assertEqual(len(self.player_white.checkers), 15)
        self.assertEqual(len(self.player_black.checkers), 15)
        
        # Verificar que todas las fichas tienen el color correcto
        for checker in self.player_white.checkers:
            self.assertEqual(checker.color, Checker.WHITE)
        
        for checker in self.player_black.checkers:
            self.assertEqual(checker.color, Checker.BLACK)
        
        # Verificar que todas las fichas empiezan sin posición
        for checker in self.player_white.checkers:
            self.assertIsNone(checker.position)

    def test_get_checkers_at_position_empty(self):
        """Test: Obtener fichas en posición sin fichas"""
        checkers = self.player_white.get_checkers_at_position(5)
        self.assertEqual(checkers, [])

    def test_get_checkers_at_position_with_checkers(self):
        """Test: Obtener fichas en posición con fichas"""
        # Colocar algunas fichas en posición 5
        self.player_white.checkers[0].position = 5
        self.player_white.checkers[1].position = 5
        self.player_white.checkers[2].position = 10
        
        checkers_at_5 = self.player_white.get_checkers_at_position(5)
        checkers_at_10 = self.player_white.get_checkers_at_position(10)
        
        self.assertEqual(len(checkers_at_5), 2)
        self.assertEqual(len(checkers_at_10), 1)
        self.assertTrue(all(c.position == 5 for c in checkers_at_5))

    def test_get_checkers_on_bar(self):
        """Test: Obtener fichas en la barra"""
        # Inicialmente no hay fichas en la barra
        self.assertEqual(len(self.player_white.get_checkers_on_bar()), 0)
        self.assertFalse(self.player_white.has_checkers_on_bar())
        
        # Colocar ficha en la barra
        self.player_white.checkers[0].move_to_bar()
        
        checkers_on_bar = self.player_white.get_checkers_on_bar()
        self.assertEqual(len(checkers_on_bar), 1)
        self.assertTrue(self.player_white.has_checkers_on_bar())