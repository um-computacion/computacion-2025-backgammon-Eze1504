<<<<<<<<< Temporary merge branch 1
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

    @property
    def last_roll(self) -> Tuple[int, int]:
        """
        Obtiene la última tirada realizada.
        
        Returns:
            tuple: (dado1, dado2) de la última tirada, o None si no se ha tirado
        """
        return self._last_roll
    
    @property
    def available_moves(self) -> List[int]:
        """
        Obtiene los movimientos disponibles restantes.
        
        Returns:
            list: Lista de valores de dados disponibles para usar
        """
        return self._available_moves.copy()
    
    @property
    def used_moves(self) -> List[int]:
        """
        Obtiene los movimientos ya utilizados.
        
        Returns:
            list: Lista de valores de dados ya utilizados
        """
        return self._used_moves.copy()
    
    def is_double(self) -> bool:
        """
        Verifica si la última tirada fue doble.
        
        Returns:
            bool: True si ambos dados mostraron el mismo valor
        """
        if self._last_roll is None:
            return False
        return self._last_roll[0] == self._last_roll[1]
    
    def has_moves_available(self) -> bool:
        """
        Verifica si quedan movimientos disponibles.
        
        Returns:
            bool: True si hay movimientos sin usar
        """
        return len(self._available_moves) > 0
    
    def use_move(self, value: int) -> bool:
        """
        Marca un movimiento como utilizado.
        
        Args:
            value (int): Valor del dado a marcar como usado
            
        Returns:
            bool: True si el movimiento fue marcado exitosamente
            
        Raises:
            ValueError: Si el valor no está disponible
        """
        if value not in self._available_moves:
            raise ValueError(f"Movimiento {value} no está disponible. Disponibles: {self._available_moves}")
        
        # Remover el primer occurrence del valor
        self._available_moves.remove(value)
        self._used_moves.append(value)
        return True
    
    def can_use_move(self, value: int) -> bool:
        """
        Verifica si un movimiento específico está disponible.
        
        Args:
            value (int): Valor del dado a verificar
            
        Returns:
            bool: True si el movimiento está disponible
        """
        return value in self._available_moves
    
    def get_possible_move_values(self) -> List[int]:
        """
        Obtiene los valores únicos de movimientos disponibles.
        
        Returns:
            list: Lista de valores únicos disponibles (sin duplicados)
        """
        return list(set(self._available_moves))
    
    def reset_moves(self):
        """
        Reinicia los movimientos disponibles a la última tirada.
        
        Útil para deshacer movimientos o reiniciar el turno.
        """
        if self._last_roll is not None:
            self._calculate_available_moves()
    
    def get_moves_summary(self) -> dict:
        """
        Obtiene un resumen completo del estado de los dados.
        
        Returns:
            dict: Diccionario con información completa de los dados
        """
        return {
            'last_roll': self._last_roll,
            'is_double': self.is_double(),
            'available_moves': self.available_moves,
            'used_moves': self.used_moves,
            'moves_remaining': len(self._available_moves),
            'has_moves': self.has_moves_available()
        }
    
    def simulate_roll(self, die1: int, die2: int):
        """
        Simula una tirada específica (útil para testing).
        
        Args:
            die1 (int): Valor del primer dado (1-6)
            die2 (int): Valor del segundo dado (1-6)
            
        Raises:
            ValueError: Si los valores no están en el rango válido
        """
        if not (self.MIN_VALUE <= die1 <= self.MAX_VALUE):
            raise ValueError(f"Valor del dado 1 inválido: {die1}. Debe estar entre {self.MIN_VALUE} y {self.MAX_VALUE}")
        
        if not (self.MIN_VALUE <= die2 <= self.MAX_VALUE):
            raise ValueError(f"Valor del dado 2 inválido: {die2}. Debe estar entre {self.MIN_VALUE} y {self.MAX_VALUE}")
        
        self._last_roll = (die1, die2)
        self._calculate_available_moves()
    
    def __str__(self) -> str:
        """
        Representación como string de los dados.
        
        Returns:
            str: Representación legible del estado actual
        """
        if self._last_roll is None:
            return "Dados sin tirar"
        
        die1, die2 = self._last_roll
        status = "doble" if self.is_double() else "normal"
        remaining = len(self._available_moves)
        
        return f"Dados: [{die1}, {die2}] - Tirada {status} - {remaining} movimientos restantes"
    
    def __repr__(self) -> str:
        """
        Representación técnica de los dados.
        
        Returns:
            str: Representación técnica para debugging
        """
        return f"Dice(last_roll={self._last_roll}, available={self._available_moves}, used={self._used_moves})"
=========

>>>>>>>>> Temporary merge branch 2
