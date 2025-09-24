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