from typing import List
from core.checker import Checker


class Player:
    """
    Representa un jugador en el juego de Backgammon.
    
    Cada jugador tiene un nombre, color y gestiona sus 15 fichas.
    También mantiene estadísticas básicas del juego.
    """
    
    TOTAL_CHECKERS = 15
    
    def __init__(self, name: str, color: str):
        """
        Inicializa un nuevo jugador.
        
        Args:
            name (str): Nombre del jugador
            color (str): Color de las fichas ("white" o "black")
            
        Raises:
            ValueError: Si el nombre está vacío o el color es inválido
        """
        if not name or not isinstance(name, str) or name.strip() == "":
            raise ValueError("El nombre del jugador no puede estar vacío")
        
        if color not in [Checker.WHITE, Checker.BLACK]:
            raise ValueError(f"Color inválido: {color}. Debe ser '{Checker.WHITE}' o '{Checker.BLACK}'")
        
        self._name = name.strip()
        self._color = color
        self._checkers = []
        self._score = 0
        self._games_won = 0
        
        # Crear las 15 fichas del jugador
        self._create_checkers()
    
    def _create_checkers(self):
        """
        Crea las 15 fichas del jugador.
        """
        self._checkers = [Checker(self._color) for _ in range(self.TOTAL_CHECKERS)]
    
    @property
    def name(self) -> str:
        """
        Obtiene el nombre del jugador.
        
        Returns:
            str: Nombre del jugador
        """
        return self._name
    
    @property
    def color(self) -> str:
        """
        Obtiene el color de las fichas del jugador.
        
        Returns:
            str: Color de las fichas ("white" o "black")
        """
        return self._color
    
    @property
    def checkers(self) -> List[Checker]:
        """
        Obtiene todas las fichas del jugador.
        
        Returns:
            list: Lista de todas las fichas del jugador
        """
        return self._checkers.copy()
    
    @property
    def score(self) -> int:
        """
        Obtiene la puntuación actual del jugador.
        
        Returns:
            int: Puntuación acumulada
        """
        return self._score
    
    @property
    def games_won(self) -> int:
        """
        Obtiene el número de juegos ganados.
        
        Returns:
            int: Cantidad de juegos ganados
        """
        return self._games_won
    
    def get_checkers_at_position(self, position: int) -> List[Checker]:
        """
        Obtiene todas las fichas en una posición específica.
        
        Args:
            position (int): Posición a consultar (0=barra, 1-24=tablero, 25=bear-off)
            
        Returns:
            list: Lista de fichas en esa posición
        """
        return [checker for checker in self._checkers if checker.position == position]
    
    def get_checkers_on_bar(self) -> List[Checker]:
        """
        Obtiene todas las fichas que están en la barra.
        
        Returns:
            list: Lista de fichas en la barra
        """
        return self.get_checkers_at_position(Checker.BAR_POSITION)
    
    def get_checkers_borne_off(self) -> List[Checker]:
        """
        Obtiene todas las fichas que han sido sacadas del tablero.
        
        Returns:
            list: Lista de fichas fuera del tablero
        """
        return self.get_checkers_at_position(Checker.BEAR_OFF_POSITION)
    
    def get_checkers_on_board(self) -> List[Checker]:
        """
        Obtiene todas las fichas que están en el tablero (posiciones 1-24).
        
        Returns:
            list: Lista de fichas en el tablero
        """
        return [checker for checker in self._checkers if checker.is_on_board()]
    
    def get_checkers_in_home_board(self) -> List[Checker]:
        """
        Obtiene todas las fichas que están en el home board del jugador.
        
        Returns:
            list: Lista de fichas en el home board
        """
        return [checker for checker in self._checkers if checker.is_in_home_board()]
    
    def has_checkers_on_bar(self) -> bool:
        """
        Verifica si el jugador tiene fichas en la barra.
        
        Returns:
            bool: True si hay fichas en la barra
        """
        return len(self.get_checkers_on_bar()) > 0