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
