import unittest
import sys
import os

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.dice import Dice


class TestDice(unittest.TestCase):
    """Tests para la clase Dice"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.dice = Dice(seed=42)  # Seed fijo para tests reproducibles

    def test_dice_creation(self):
        """Test: Creación inicial de dados"""
        dice = Dice()
        self.assertIsNone(dice.last_roll)
        self.assertEqual(dice.available_moves, [])
        self.assertEqual(dice.used_moves, [])
        self.assertFalse(dice.has_moves_available())

    def test_dice_creation_with_seed(self):
        """Test: Creación con semilla específica"""
        dice1 = Dice(seed=123)
        dice2 = Dice(seed=123)
        
        roll1 = dice1.roll()
        roll2 = dice2.roll()
        
        # Con la misma semilla, deben dar el mismo resultado
        self.assertEqual(roll1, roll2)

    def test_roll_basic(self):
        """Test: Tirada básica de dados"""
        result = self.dice.roll()
        
        # Verificar que se devuelve una tupla de 2 elementos
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        
        # Verificar rango válido de dados
        die1, die2 = result
        self.assertTrue(1 <= die1 <= 6)
        self.assertTrue(1 <= die2 <= 6)
        
        # Verificar que se guardó como last_roll
        self.assertEqual(self.dice.last_roll, result)

    def test_roll_normal_moves(self):
        """Test: Movimientos disponibles en tirada normal"""
        # Simular tirada normal (no doble)
        self.dice.simulate_roll(3, 5)
        
        self.assertEqual(self.dice.last_roll, (3, 5))
        self.assertFalse(self.dice.is_double())
        self.assertEqual(sorted(self.dice.available_moves), [3, 5])
        self.assertTrue(self.dice.has_moves_available())

    def test_roll_double_moves(self):
        """Test: Movimientos disponibles en tirada doble"""
        # Simular tirada doble
        self.dice.simulate_roll(4, 4)
        
        self.assertEqual(self.dice.last_roll, (4, 4))
        self.assertTrue(self.dice.is_double())
        self.assertEqual(self.dice.available_moves, [4, 4, 4, 4])
        self.assertTrue(self.dice.has_moves_available())

    def test_simulate_roll_valid_values(self):
        """Test: Simulación con valores válidos"""
        self.dice.simulate_roll(1, 6)
        self.assertEqual(self.dice.last_roll, (1, 6))
        
        self.dice.simulate_roll(6, 1)
        self.assertEqual(self.dice.last_roll, (6, 1))

    def test_simulate_roll_invalid_values(self):
        """Test: Simulación con valores inválidos debe fallar"""
        with self.assertRaises(ValueError) as context:
            self.dice.simulate_roll(0, 3)
        self.assertIn("Valor del dado 1 inválido", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            self.dice.simulate_roll(3, 7)
        self.assertIn("Valor del dado 2 inválido", str(context.exception))
        
        with self.assertRaises(ValueError):
            self.dice.simulate_roll(-1, 3)

    def test_use_move_normal_roll(self):
        """Test: Usar movimientos en tirada normal"""
        self.dice.simulate_roll(2, 5)
        
        # Usar primer movimiento
        result = self.dice.use_move(2)
        self.assertTrue(result)
        self.assertEqual(self.dice.available_moves, [5])
        self.assertEqual(self.dice.used_moves, [2])
        
        # Usar segundo movimiento
        result = self.dice.use_move(5)
        self.assertTrue(result)
        self.assertEqual(self.dice.available_moves, [])
        self.assertEqual(self.dice.used_moves, [2, 5])
        self.assertFalse(self.dice.has_moves_available())

    def test_use_move_double_roll(self):
        """Test: Usar movimientos en tirada doble"""
        self.dice.simulate_roll(3, 3)
        
        # Usar primer movimiento
        self.dice.use_move(3)
        self.assertEqual(len(self.dice.available_moves), 3)
        self.assertEqual(self.dice.used_moves, [3])
        
        # Usar segundo movimiento
        self.dice.use_move(3)
        self.assertEqual(len(self.dice.available_moves), 2)
        self.assertEqual(self.dice.used_moves, [3, 3])
    
    def test_use_move_unavailable(self):
        """Test: Intentar usar movimiento no disponible debe fallar"""
        self.dice.simulate_roll(2, 5)
        
        with self.assertRaises(ValueError) as context:
            self.dice.use_move(3)
        
        self.assertIn("Movimiento 3 no está disponible", str(context.exception))
        self.assertIn("Disponibles: [2, 5]", str(context.exception))

    def test_use_move_already_used(self):
        """Test: Intentar usar movimiento ya agotado"""
        self.dice.simulate_roll(2, 5)
        
        # Usar el movimiento de 2
        self.dice.use_move(2)
        
        # Intentar usar 2 nuevamente
        with self.assertRaises(ValueError):
            self.dice.use_move(2)

    def test_can_use_move(self):
        """Test: Verificar disponibilidad de movimientos"""
        self.dice.simulate_roll(3, 6)
        
        self.assertTrue(self.dice.can_use_move(3))
        self.assertTrue(self.dice.can_use_move(6))
        self.assertFalse(self.dice.can_use_move(1))
        self.assertFalse(self.dice.can_use_move(4))
        
        # Después de usar un movimiento
        self.dice.use_move(3)
        self.assertFalse(self.dice.can_use_move(3))
        self.assertTrue(self.dice.can_use_move(6))

    def test_get_possible_move_values(self):
        """Test: Obtener valores únicos de movimientos"""
        # Tirada normal
        self.dice.simulate_roll(2, 5)
        self.assertEqual(sorted(self.dice.get_possible_move_values()), [2, 5])
        
        # Tirada doble
        self.dice.simulate_roll(4, 4)
        self.assertEqual(self.dice.get_possible_move_values(), [4])
        
        # Después de usar algunos movimientos
        self.dice.use_move(4)
        self.dice.use_move(4)
        self.assertEqual(self.dice.get_possible_move_values(), [4])  # Aún queda 4

    def test_reset_moves(self):
        """Test: Reiniciar movimientos disponibles"""
        self.dice.simulate_roll(3, 6)
        self.dice.use_move(3)
        
        # Verificar que se usó un movimiento
        self.assertEqual(self.dice.available_moves, [6])
        self.assertEqual(self.dice.used_moves, [3])
        
        # Reiniciar
        self.dice.reset_moves()
        
        # Verificar que se restauraron los movimientos
        self.assertEqual(sorted(self.dice.available_moves), [3, 6])
        self.assertEqual(self.dice.used_moves, [])

    def test_reset_moves_no_roll(self):
        """Test: Reiniciar cuando no hay tirada previa"""
        self.dice.reset_moves()
        self.assertEqual(self.dice.available_moves, [])
        self.assertEqual(self.dice.used_moves, [])

    def test_get_moves_summary(self):
        """Test: Obtener resumen completo del estado"""
        # Sin tirada
        summary = self.dice.get_moves_summary()
        expected = {
            'last_roll': None,
            'is_double': False,
            'available_moves': [],
            'used_moves': [],
            'moves_remaining': 0,
            'has_moves': False
        }
        self.assertEqual(summary, expected)
        
        # Con tirada normal
        self.dice.simulate_roll(2, 6)
        summary = self.dice.get_moves_summary()
        
        self.assertEqual(summary['last_roll'], (2, 6))
        self.assertFalse(summary['is_double'])
        self.assertEqual(sorted(summary['available_moves']), [2, 6])
        self.assertEqual(summary['moves_remaining'], 2)
        self.assertTrue(summary['has_moves'])

    def test_constants(self):
        """Test: Verificar constantes de la clase"""
        self.assertEqual(Dice.MIN_VALUE, 1)
        self.assertEqual(Dice.MAX_VALUE, 6)
        self.assertEqual(Dice.NUM_DICE, 2)

    def test_str_representation(self):
        """Test: Representación como string"""
        # Sin tirada
        self.assertEqual(str(self.dice), "Dados sin tirar")
        
        # Tirada normal
        self.dice.simulate_roll(3, 5)
        expected = "Dados: [3, 5] - Tirada normal - 2 movimientos restantes"
        self.assertEqual(str(self.dice), expected)
        
        # Tirada doble
        self.dice.simulate_roll(4, 4)
        expected = "Dados: [4, 4] - Tirada doble - 4 movimientos restantes"
        self.assertEqual(str(self.dice), expected)
        
        # Después de usar movimientos
        self.dice.use_move(4)
        expected = "Dados: [4, 4] - Tirada doble - 3 movimientos restantes"
        self.assertEqual(str(self.dice), expected)

    def test_repr_representation(self):
        """Test: Representación técnica"""
        self.dice.simulate_roll(2, 5)
        self.dice.use_move(2)
        
        expected = "Dice(last_roll=(2, 5), available=[5], used=[2])"
        self.assertEqual(repr(self.dice), expected)

    def test_multiple_rolls(self):
        """Test: Múltiples tiradas consecutivas"""
        # Primera tirada
        self.dice.simulate_roll(1, 3)
        self.dice.use_move(1)
        
        # Segunda tirada (debe resetear movimientos)
        self.dice.simulate_roll(5, 6)
        
        # Los movimientos anteriores deben haberse limpiado
        self.assertEqual(sorted(self.dice.available_moves), [5, 6])
        self.assertEqual(self.dice.used_moves, [])

    def test_edge_cases(self):
        """Test: Casos edge importantes"""
        # Usar todos los movimientos de una tirada doble
        self.dice.simulate_roll(2, 2)
        
        for _ in range(4):
            self.assertTrue(self.dice.has_moves_available())
            self.dice.use_move(2)
        
        self.assertFalse(self.dice.has_moves_available())
        self.assertEqual(len(self.dice.used_moves), 4)
        
        # Verificar que no se puede usar más
        with self.assertRaises(ValueError):
            self.dice.use_move(2)


if __name__ == '__main__':
    unittest.main(verbosity=2)