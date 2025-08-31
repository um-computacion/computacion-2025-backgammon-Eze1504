import random
from typing import List, Tuple


class Dice:
    """
    Representa los dados del juego de Backgammon.
    
    Maneja la lógica de tirada de dos dados de seis caras,
    incluyendo el comportamiento especial de las tiradas dobles.
    """
    
    MIN_VALUE = 1
    MAX_VALUE = 6
    NUM_DICE = 2
    
    def __init__(self, seed=None):
        """
        Inicializa los dados.
        
        Args:
            seed (int, optional): Semilla para el generador de números aleatorios.
                                 Útil para testing y reproducibilidad.
        """
        if seed is not None:
            random.seed(seed)
        
        self._last_roll = None
        self._available_moves = []
        self._used_moves = []
    
    def roll(self) -> Tuple[int, int]:
        """
        Tira los dos dados y calcula los movimientos disponibles.
        
        Returns:
            tuple: (dado1, dado2) con los valores obtenidos
        """
        die1 = random.randint(self.MIN_VALUE, self.MAX_VALUE)
        die2 = random.randint(self.MIN_VALUE, self.MAX_VALUE)
        
        self._last_roll = (die1, die2)
        self._calculate_available_moves()
        
        return self._last_roll
    
    def _calculate_available_moves(self):
        """
        Calcula los movimientos disponibles basándose en la última tirada.
        
        En tiradas dobles, se obtienen 4 movimientos del mismo valor.
        En tiradas normales, se obtienen 2 movimientos diferentes.
        """
        if self._last_roll is None:
            self._available_moves = []
            return
        
         
        die1, die2 = self._last_roll
        
        if die1 == die2:  # Tirada doble
            self._available_moves = [die1, die1, die1, die1]
        else:  # Tirada normal
            self._available_moves = [die1, die2]
        
        self._used_moves = []
