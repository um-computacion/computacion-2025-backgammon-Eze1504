"""
Módulo que contiene la implementación de la clase Board para el juego de Backgammon.
"""

from typing import List, Dict, Optional, Tuple
from .checker import Checker
from .player import Player
from .exceptions import InvalidPositionException


class Board:
    """
    Representa el tablero de Backgammon con 24 puntos (triángulos).
    
    El tablero se divide en 4 cuadrantes:
    - Cuadrante 1: puntos 1-6 (home board del jugador 1)
    - Cuadrante 2: puntos 7-12 
    - Cuadrante 3: puntos 13-18
    - Cuadrante 4: puntos 19-24 (home board del jugador 2)
    
    Posiciones especiales:
    - Bar: punto 0 (fichas capturadas)
    - Off: punto 25 (fichas sacadas del tablero)
    """
    
    def __init__(self):
        """
        Inicializa el tablero con las posiciones estándar del Backgammon.
        """
        # Diccionario que representa los 24 puntos + bar (0) + off (25)
        # Cada punto contiene una lista de fichas
        self.__points: Dict[int, List[Checker]] = {}
        
        # Inicializar todos los puntos vacíos
        for i in range(26):  # 0 (bar) a 25 (off)
            self.__points[i] = []
         # Configurar posiciones iniciales estándar
        self._setup_initial_position()
    
    def _setup_initial_position(self) -> None:
        """
        Configura las posiciones iniciales estándar del Backgammon.
        
        Posición inicial:
        - Jugador 1 (blanco): 2 fichas en punto 24, 5 en punto 13, 3 en punto 8, 5 en punto 6
        - Jugador 2 (negro): 2 fichas en punto 1, 5 en punto 12, 3 en punto 17, 5 en punto 19
        """
        # Jugador 1 (blanco) - se mueve hacia puntos menores (24->1)
        # 2 fichas en punto 24
        for _ in range(2):
            self.__points[24].append(Checker("white", 24))
        
        # 5 fichas en punto 13
        for _ in range(5):
            self.__points[13].append(Checker("white", 13))
        
        # 3 fichas en punto 8
        for _ in range(3):
            self.__points[8].append(Checker("white", 8))
        
        # 5 fichas en punto 6
        for _ in range(5):
            self.__points[6].append(Checker("white", 6))
        
        # Jugador 2 (negro) - se mueve hacia puntos mayores (1->24)
        # 2 fichas en punto 1
        for _ in range(2):
            self.__points[1].append(Checker("black", 1))
        
        # 5 fichas en punto 12
        for _ in range(5):
            self.__points[12].append(Checker("black", 12))
        
        # 3 fichas en punto 17
        for _ in range(3):
            self.__points[17].append(Checker("black", 17))
        
        # 5 fichas en punto 19
        for _ in range(5):
            self.__points[19].append(Checker("black", 19))
    
    def get_point(self, position: int) -> List[Checker]:
        """
        Obtiene las fichas en una posición específica.
        
        Args:
            position (int): Posición del punto (0-25)
            
        Returns:
            List[Checker]: Lista de fichas en esa posición
            
        Raises:
            InvalidPositionException: Si la posición no es válida
        """
        if not self.is_valid_position(position):
            raise InvalidPositionException(f"Posición {position} no es válida. Debe estar entre 0 y 25.")
        
        return self.__points[position].copy()  # Retorna una copia para evitar modificaciones externas
    