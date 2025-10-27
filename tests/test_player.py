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

    def test_get_checkers_borne_off(self):
        """Test: Obtener fichas fuera del tablero"""
        # Inicialmente no hay fichas fuera
        self.assertEqual(len(self.player_white.get_checkers_borne_off()), 0)
        
        # Sacar fichas del tablero
        self.player_white.checkers[0].bear_off()
        self.player_white.checkers[1].bear_off()
        
        checkers_borne_off = self.player_white.get_checkers_borne_off()
        self.assertEqual(len(checkers_borne_off), 2)

    def test_get_checkers_on_board(self):
        """Test: Obtener fichas en el tablero"""
        # Colocar fichas en diferentes posiciones
        self.player_white.checkers[0].position = 5
        self.player_white.checkers[1].position = 10
        self.player_white.checkers[2].move_to_bar()  # Barra, no cuenta
        self.player_white.checkers[3].bear_off()     # Bear-off, no cuenta
        
        checkers_on_board = self.player_white.get_checkers_on_board()
        self.assertEqual(len(checkers_on_board), 2)

    def test_get_checkers_in_home_board_white(self):
        """Test: Fichas en home board para jugador blanco"""
        # Home board blanco: posiciones 1-6
        self.player_white.checkers[0].position = 1   # En home board
        self.player_white.checkers[1].position = 6   # En home board
        self.player_white.checkers[2].position = 7   # Fuera del home board
        self.player_white.checkers[3].position = 24  # Fuera del home board
        
        checkers_in_home = self.player_white.get_checkers_in_home_board()
        self.assertEqual(len(checkers_in_home), 2)

    def test_get_checkers_in_home_board_black(self):
        """Test: Fichas en home board para jugador negro"""
        # Home board negro: posiciones 19-24
        self.player_black.checkers[0].position = 19  # En home board
        self.player_black.checkers[1].position = 24  # En home board
        self.player_black.checkers[2].position = 18  # Fuera del home board
        self.player_black.checkers[3].position = 1   # Fuera del home board
        
        checkers_in_home = self.player_black.get_checkers_in_home_board()
        self.assertEqual(len(checkers_in_home), 2)

    def test_has_checkers_outside_home_board(self):
        """Test: Verificar fichas fuera del home board"""
        # Inicialmente todas las fichas están sin posición, no fuera del home board
        self.assertFalse(self.player_white.has_checkers_outside_home_board())
        
        # Colocar ficha en la barra
        self.player_white.checkers[0].move_to_bar()
        self.assertTrue(self.player_white.has_checkers_outside_home_board())
        
        # Mover de la barra al tablero fuera del home board
        self.player_white.checkers[0].position = 10  # Fuera del home board blanco
        self.assertTrue(self.player_white.has_checkers_outside_home_board())
        
        # Mover todas las fichas al home board
        for i, checker in enumerate(self.player_white.checkers):
            if i < 15:  # Solo las primeras 15
                checker.position = 1 + (i % 6)  # Posiciones 1-6 (home board blanco)
        
        self.assertFalse(self.player_white.has_checkers_outside_home_board())

    def test_can_bear_off(self):
        """Test: Verificar si puede hacer bear-off"""
        # Inicialmente no puede porque no hay fichas en el home board
        self.assertTrue(self.player_white.can_bear_off())  # Técnicamente sí, porque no hay fichas fuera
        
        # Colocar ficha fuera del home board
        self.player_white.checkers[0].position = 10
        self.assertFalse(self.player_white.can_bear_off())
        
        # Mover todas al home board
        for checker in self.player_white.checkers:
            checker.position = 1  # Home board blanco
        
        self.assertTrue(self.player_white.can_bear_off())

    def test_count_checkers_at_position(self):
        """Test: Contar fichas en posición específica"""
        self.assertEqual(self.player_white.count_checkers_at_position(5), 0)
        
        # Colocar fichas
        self.player_white.checkers[0].position = 5
        self.player_white.checkers[1].position = 5
        self.player_white.checkers[2].position = 10
        
        self.assertEqual(self.player_white.count_checkers_at_position(5), 2)
        self.assertEqual(self.player_white.count_checkers_at_position(10), 1)
        self.assertEqual(self.player_white.count_checkers_at_position(15), 0)

    def test_get_checker_at_position_success(self):
        """Test: Obtener ficha específica en posición"""
        self.player_white.checkers[0].position = 5
        
        checker = self.player_white.get_checker_at_position(5)
        self.assertEqual(checker.position, 5)
        self.assertEqual(checker.color, Checker.WHITE)

    def test_get_checker_at_position_no_checkers(self):
        """Test: Obtener ficha en posición vacía debe fallar"""
        with self.assertRaises(ValueError) as context:
            self.player_white.get_checker_at_position(5)
        
        self.assertIn("No hay fichas del jugador Alice en la posición 5", str(context.exception))

    def test_move_checker_success(self):
        """Test: Mover ficha exitosamente"""
        # Colocar ficha en posición inicial
        self.player_white.checkers[0].position = 5
        
        # Mover la ficha
        moved_checker = self.player_white.move_checker(5, 10)
        
        self.assertEqual(moved_checker.position, 10)
        self.assertEqual(self.player_white.count_checkers_at_position(5), 0)
        self.assertEqual(self.player_white.count_checkers_at_position(10), 1)

    def test_move_checker_no_checkers_at_origin(self):
        """Test: Mover ficha desde posición vacía debe fallar"""
        with self.assertRaises(ValueError):
            self.player_white.move_checker(5, 10)

    def test_add_score_valid(self):
        """Test: Añadir puntuación válida"""
        self.assertEqual(self.player_white.score, 0)
        
        self.player_white.add_score(5)
        self.assertEqual(self.player_white.score, 5)
        
        self.player_white.add_score(3)
        self.assertEqual(self.player_white.score, 8)

    def test_add_score_invalid(self):
        """Test: Añadir puntuación negativa debe fallar"""
        with self.assertRaises(ValueError) as context:
            self.player_white.add_score(-1)
        
        self.assertIn("Los puntos no pueden ser negativos", str(context.exception))

    def test_win_game_default(self):
        """Test: Ganar juego con puntuación por defecto"""
        initial_score = self.player_white.score
        initial_games = self.player_white.games_won
        
        self.player_white.win_game()
        
        self.assertEqual(self.player_white.score, initial_score + 1)
        self.assertEqual(self.player_white.games_won, initial_games + 1)

    def test_win_game_custom_points(self):
        """Test: Ganar juego con puntuación personalizada"""
        self.player_white.win_game(3)  # Backgammon
        
        self.assertEqual(self.player_white.score, 3)
        self.assertEqual(self.player_white.games_won, 1)

    def test_reset_checkers_positions(self):
        """Test: Reiniciar posiciones de fichas"""
        # Colocar fichas en diferentes posiciones
        self.player_white.checkers[0].position = 5
        self.player_white.checkers[1].position = 10
        self.player_white.checkers[2].move_to_bar()
        
        # Reiniciar
        self.player_white.reset_checkers_positions()
        
        # Verificar que todas las fichas están sin posición
        for checker in self.player_white.checkers:
            self.assertIsNone(checker.position)

    def test_get_position_summary(self):
        """Test: Obtener resumen de posiciones"""
        # Configurar fichas en diferentes posiciones
        self.player_white.checkers[0].position = 5   # Tablero
        self.player_white.checkers[1].position = 1   # Home board
        self.player_white.checkers[2].move_to_bar()  # Barra
        self.player_white.checkers[3].bear_off()     # Bear-off
        
        summary = self.player_white.get_position_summary()
        
        expected = {
            'total_checkers': 15,
            'on_board': 2,
            'on_bar': 1,
            'borne_off': 1,
            'in_home_board': 1,
            'can_bear_off': False  # Porque hay una ficha en posición 5 (fuera del home board)
        }
        
        self.assertEqual(summary, expected)

    def test_get_board_representation(self):
        """Test: Obtener representación del tablero"""
        # Colocar fichas
        self.player_white.checkers[0].position = 5
        self.player_white.checkers[1].position = 5
        self.player_white.checkers[2].position = 10
        self.player_white.checkers[3].move_to_bar()
        
        representation = self.player_white.get_board_representation()
        
        expected = {
            0: 1,   # 1 ficha en barra
            5: 2,   # 2 fichas en posición 5
            10: 1   # 1 ficha en posición 10
        }
        
        self.assertEqual(representation, expected)

    def test_constants(self):
        """Test: Verificar constantes de la clase"""
        self.assertEqual(Player.TOTAL_CHECKERS, 15)

    def test_str_representation(self):
        """Test: Representación como string"""
        self.player_white.checkers[0].position = 5
        self.player_white.checkers[1].move_to_bar()
        self.player_white.checkers[2].bear_off()
        self.player_white.add_score(5)
    
        result = str(self.player_white)
    
        self.assertIn("Alice", result)
        self.assertIn("white", result)
        self.assertIn("Tablero: 1", result)
        self.assertIn("Barra: 1", result)
        self.assertIn("Fuera: 1", result)
        self.assertIn("Score: 5", result)

    def test_repr_representation(self):
        """Test: Representación técnica"""
        self.player_white.add_score(10)
        
        result = repr(self.player_white)
        expected = "Player(name='Alice', color='white', score=10)"
        
        self.assertEqual(result, expected)

    def test_equality(self):
        """Test: Comparación de igualdad entre jugadores"""
        player1 = Player("TestPlayer", Checker.WHITE)
        player2 = Player("TestPlayer", Checker.WHITE)
        player3 = Player("TestPlayer", Checker.BLACK)
        player4 = Player("OtherPlayer", Checker.WHITE)
        
        # Mismos nombre y color
        self.assertEqual(player1, player2)
        
        # Diferentes colores
        self.assertNotEqual(player1, player3)
        
        # Diferentes nombres
        self.assertNotEqual(player1, player4)
        
        # Comparar con objeto diferente
        self.assertNotEqual(player1, "not a player")

    def test_integration_scenario(self):
        """Test: Escenario de integración completo"""
        # Simular movimientos típicos
        player = Player("IntegrationTest", Checker.WHITE)
        
        # Colocar fichas en posiciones iniciales típicas
        for i in range(2):
            player.checkers[i].position = 24  # 2 fichas en punto 24
        for i in range(2, 7):
            player.checkers[i].position = 13  # 5 fichas en punto 13
        for i in range(7, 10):
            player.checkers[i].position = 8   # 3 fichas en punto 8
        for i in range(10, 15):
            player.checkers[i].position = 6   # 5 fichas en punto 6
        
        # Verificar estado inicial
        self.assertEqual(player.count_checkers_at_position(24), 2)
        self.assertEqual(player.count_checkers_at_position(13), 5)
        self.assertEqual(player.count_checkers_at_position(8), 3)
        self.assertEqual(player.count_checkers_at_position(6), 5)
        
        # Verificar que no puede hacer bear-off (tiene fichas fuera del home board)
        self.assertFalse(player.can_bear_off())
        
        # Mover todas las fichas al home board
        for checker in player.checkers:
            if checker.position > 6:
                checker.position = 1  # Mover al home board