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
         """Listado de fichas que están en el home board (en el tablero)."""
         start, end = self._home_range()
         return [c for c in self.checkers if c.is_on_board() and start <= c.position <= end]
    def has_checkers_on_bar(self) -> bool:
        """
        Verifica si el jugador tiene fichas en la barra.
        
        Returns:
            bool: True si hay fichas en la barra
        """
        return len(self.get_checkers_on_bar()) > 0
    
    def has_checkers_outside_home_board(self) -> bool:
        """True si hay ficha en barra o en tablero fuera del home board."""
        start, end = self._home_range()
        for c in self.checkers:
            if c.is_on_bar():
                return True
            if c.is_on_board() and not (start <= c.position <= end):
                return True
        return False
    def can_bear_off(self) -> bool:
         """En M2: puede hacer bear-off si no hay fichas fuera del home board ni en la barra."""
         return not self.has_checkers_outside_home_board()

    
    def count_checkers_at_position(self, position: int) -> int:
        """
        Cuenta las fichas en una posición específica.
        
        Args:
            position (int): Posición a contar
            
        Returns:
            int: Número de fichas en esa posición
        """
        return len(self.get_checkers_at_position(position))
    
    def get_checker_at_position(self, position: int) -> Checker:
        """
        Obtiene la primera ficha disponible en una posición.
        
        Args:
            position (int): Posición de la cual obtener una ficha
            
        Returns:
            Checker: Primera ficha en esa posición
            
        Raises:
            ValueError: Si no hay fichas en esa posición
        """
        checkers_at_position = self.get_checkers_at_position(position)
        if not checkers_at_position:
            raise ValueError(f"No hay fichas del jugador {self._name} en la posición {position}")
        
        return checkers_at_position[0]
    
    def move_checker(self, from_position: int, to_position: int) -> Checker:
        """
        Mueve una ficha de una posición a otra.
        
        Args:
            from_position (int): Posición origen
            to_position (int): Posición destino
            
        Returns:
            Checker: La ficha que fue movida
            
        Raises:
            ValueError: Si no hay fichas en la posición origen
        """
        checker = self.get_checker_at_position(from_position)
        checker.move_to(to_position)
        return checker
    
    def add_score(self, points: int):
        """
        Añade puntos al score del jugador.
        
        Args:
            points (int): Puntos a añadir
            
        Raises:
            ValueError: Si los puntos son negativos
        """
        if points < 0:
            raise ValueError("Los puntos no pueden ser negativos")
        
        self._score += points
    
    def win_game(self, points: int = 1):
        """
        Registra una victoria del jugador.
        
        Args:
            points (int): Puntos ganados por la victoria (1=normal, 2=gammon, 3=backgammon)
        """
        self._games_won += 1
        self.add_score(points)
    
    def reset_checkers_positions(self):
        """
        Reinicia las posiciones de todas las fichas (las deja sin posición).
        
        Útil para empezar un nuevo juego.
        """
        for checker in self._checkers:
            checker.position = None
    
    def get_position_summary(self) -> dict:
        """
    Resumen de posiciones (coincide con lo que esperan los tests).
    """
        total = len(self.checkers)
        on_board = sum(1 for c in self.checkers if c.is_on_board())
        on_bar = sum(1 for c in self.checkers if c.is_on_bar())
        borne_off = sum(1 for c in self.checkers if c.is_borne_off())
        in_home_board = len(self.get_checkers_in_home_board())
        return {
            "total_checkers": total,
            "on_board": on_board,
            "on_bar": on_bar,
            "borne_off": borne_off,
            "in_home_board": in_home_board,
            "can_bear_off": self.can_bear_off(),
            }
    def __str__(self) -> str:
        """
        Representación como string del jugador.
        
        Returns:
            str: Representación legible del jugador
        """
        summary = self.get_position_summary()
        return (f"Jugador {self._name} ({self._color}) - "
                f"Tablero: {summary['on_board']}, "
                f"Barra: {summary['on_bar']}, "
                f"Fuera: {summary['borne_off']} - "
                f"Score: {self._score}")
    
    def __repr__(self) -> str:
        """
        Representación técnica del jugador.
        
        Returns:
            str: Representación técnica para debugging
        """
        return f"Player(name='{self._name}', color='{self._color}', score={self._score})"
    
    def __eq__(self, other) -> bool:
        """
        Compara dos jugadores por igualdad.
        
        Args:
            other: Otro jugador a comparar
            
        Returns:
            bool: True si tienen el mismo nombre y color
        """
        if not isinstance(other, Player):
            return False
        return self._name == other._name and self._color == other._color
    
    def _home_range(self) -> tuple[int, int]:
        """Retorna el rango del home board según el color del jugador."""
        if self.color == Checker.WHITE:
            return (1, 6)
        else:
            return (19, 24)
    def get_board_representation(self) -> dict:
        """Devuelve un diccionario con la cantidad de fichas por posición.
    
    Returns:
        Dict[int, int]: {posición: cantidad_de_fichas}
    """
        representation = {}
        for checker in self.checkers:
            if checker.is_on_bar():
            # Fichas en la barra se cuentan en posición 0
                representation[0] = representation.get(0, 0) + 1
            elif checker.position is not None and 1 <= checker.position <= 24:
            # Fichas en el tablero
                representation[checker.position] = representation.get(checker.position, 0) + 1
        return representation