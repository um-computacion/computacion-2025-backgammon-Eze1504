"""
Módulo que contiene la implementación de la clase Board para el juego de Backgammon.
"""

from typing import List, Dict, Optional, Tuple
from .checker import Checker
from .player import Player
from .exceptions import InvalidPositionException, InvalidMoveException
from .exceptions import (
    InvalidPositionException,
    NoCheckersAtPositionException,
    CheckerNotMovableException,
)



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
    
    def is_valid_position(self, position: int) -> bool:
        """
        Verifica si una posición es válida en el tablero.
        
        Args:
            position (int): Posición a validar
            
        Returns:
            bool: True si la posición es válida (0-25), False en caso contrario
        """
        return 0 <= position <= 25
    
    def is_point_occupied_by_opponent(self, position: int, player_color: str) -> bool:
        """
        Verifica si un punto está ocupado por el oponente.
        
        Args:
            position (int): Posición del punto
            player_color (str): Color del jugador ("white" o "black")
            
        Returns:
            bool: True si el punto está ocupado por el oponente, False en caso contrario
            
        Raises:
            InvalidPositionException: Si la posición no es válida
        """
        if not self.is_valid_position(position):
            raise InvalidPositionException(f"Posición {position} no es válida.")
        
        point_checkers = self.__points[position]
        if not point_checkers:
            return False
        
        # Si hay fichas y son del color opuesto
        opponent_color = "black" if player_color == "white" else "white"
        return point_checkers[0].get_color() == opponent_color
    
    def is_point_blocked(self, position: int, player_color: str) -> bool:
        """
        Verifica si un punto está bloqueado para un jugador.
        Un punto está bloqueado si tiene 2 o más fichas del oponente.
        
        Args:
            position (int): Posición del punto
            player_color (str): Color del jugador
            
        Returns:
            bool: True si el punto está bloqueado, False en caso contrario
            
        Raises:
            InvalidPositionException: Si la posición no es válida
        """
        if not self.is_valid_position(position):
            raise InvalidPositionException(f"Posición {position} no es válida.")
        
        point_checkers = self.__points[position]
        if len(point_checkers) < 2:
            return False
        
        # Si hay 2 o más fichas del oponente, está bloqueado
        opponent_color = "black" if player_color == "white" else "white"
        return point_checkers[0].get_color() == opponent_color
    
    def can_place_checker(self, position: int, player_color: str) -> bool:
        """
        Verifica si un jugador puede colocar una ficha en una posición.
        
        Args:
            position (int): Posición donde se quiere colocar la ficha
            player_color (str): Color del jugador
            
        Returns:
            bool: True si se puede colocar la ficha, False en caso contrario
        """
        if not self.is_valid_position(position):
            return False
        
        # No se puede colocar en un punto bloqueado
        if self.is_point_blocked(position, player_color):
            return False
        
        return True
    def place_checker(self, checker: Checker, position: int) -> Optional[Checker]:
        """
        Coloca una ficha en una posición específica.
        """
        if not self.is_valid_position(position):
            raise InvalidPositionException(f"Posición {position} no es válida.")

        if not self.can_place_checker(position, checker.get_color()):
            raise InvalidPositionException(f"No se puede colocar ficha en posición {position}.")

        captured_checker = None
        point_checkers = self.__points[position]

        if (len(point_checkers) == 1
            and point_checkers[0].get_color() != checker.get_color()):
            captured_checker = point_checkers.pop()
            captured_checker.position = 0   # enviar al bar

        checker.position = position
        self.__points[position].append(checker)

        return captured_checker

    def remove_checker(self, position: int) -> Optional[Checker]:
        """
        Remueve una ficha de una posición específica.
        
        Args:
            position (int): Posición de donde remover la ficha
            
        Returns:
            Optional[Checker]: Ficha removida si existe, None en caso contrario
            
        Raises:
            InvalidPositionException: Si la posición no es válida
        """
        if not self.is_valid_position(position):
            raise InvalidPositionException(f"Posición {position} no es válida.")
        
        if not self.__points[position]:
            return None
        
        return self.__points[position].pop()
    
    def get_checkers_in_bar(self, player_color: str) -> List[Checker]:
        """
        Obtiene las fichas de un jugador que están en el bar (capturadas).
        
        Args:
            player_color (str): Color del jugador
            
        Returns:
            List[Checker]: Lista de fichas del jugador en el bar
        """
        bar_checkers = self.__points[0]
        return [checker for checker in bar_checkers if checker.get_color() == player_color]
    
    def get_checkers_off_board(self, player_color: str) -> List[Checker]:
        """
        Obtiene las fichas de un jugador que están fuera del tablero (sacadas).
        
        Args:
            player_color (str): Color del jugador
            
        Returns:
            List[Checker]: Lista de fichas del jugador fuera del tablero
        """
        off_checkers = self.__points[25]
        return [checker for checker in off_checkers if checker.get_color() == player_color]
    
    def get_home_board_range(self, player_color: str) -> Tuple[int, int]:
        """
        Obtiene el rango del home board para un jugador.
        
        Args:
            player_color (str): Color del jugador
            
        Returns:
            Tuple[int, int]: Rango (inicio, fin) del home board
        """
        if player_color == "white":
            return (1, 6)  # Home board del jugador blanco
        else:
            return (19, 24)  # Home board del jugador negro
    
    def all_checkers_in_home_board(self, player_color: str) -> bool:
        """
        Verifica si todas las fichas de un jugador están en su home board.
        
        Args:
            player_color (str): Color del jugador
            
        Returns:
            bool: True si todas las fichas están en el home board, False en caso contrario
        """
        home_start, home_end = self.get_home_board_range(player_color)
        
        # Verificar que no haya fichas en el bar
        if self.get_checkers_in_bar(player_color):
            return False
        
        # Verificar que no haya fichas fuera del home board
        for position in range(1, 25):
            if position < home_start or position > home_end:
                checkers = self.__points[position]
                if any(checker.get_color() == player_color for checker in checkers):
                    return False
        
        return True
    
    def count_checkers(self, player_color: str) -> Dict[str, int]:
        """
        Cuenta las fichas de un jugador en diferentes áreas del tablero.
        
        Args:
            player_color (str): Color del jugador
            
        Returns:
            Dict[str, int]: Diccionario con conteos por área
        """
        counts = {
            "board": 0,
            "bar": 0,
            "off": 0,
            "total": 0
        }
        
        # Contar fichas en el tablero (puntos 1-24)
        for position in range(1, 25):
            checkers = self.__points[position]
            counts["board"] += sum(1 for checker in checkers if checker.get_color() == player_color)
        
        # Contar fichas en el bar
        counts["bar"] = len(self.get_checkers_in_bar(player_color))
        
        # Contar fichas fuera del tablero
        counts["off"] = len(self.get_checkers_off_board(player_color))
        
        counts["total"] = counts["board"] + counts["bar"] + counts["off"]
        
        return counts
    
    def __str__(self) -> str:
        """
        Representación en string del tablero.
        
        Returns:
            str: Representación visual del tablero
        """
        lines = []
        lines.append("Tablero de Backgammon")
        lines.append("=" * 40)
        
        # Mostrar puntos 13-24 (parte superior)
        upper_line = []
        for i in range(13, 25):
            checkers = self.__points[i]
            if checkers:
                color_initial = checkers[0].get_color()[0].upper()
                count = len(checkers)
                upper_line.append(f"{i:2d}({color_initial}{count})")
            else:
                upper_line.append(f"{i:2d}(--)")
        
        lines.append("Upper: " + " ".join(upper_line))
        
        # Mostrar bar
        bar_white = len([c for c in self.__points[0] if c.get_color() == "white"])
        bar_black = len([c for c in self.__points[0] if c.get_color() == "black"])
        lines.append(f"BAR: W={bar_white}, B={bar_black}")
        
        # Mostrar puntos 12-1 (parte inferior)
        lower_line = []
        for i in range(12, 0, -1):
            checkers = self.__points[i]
            if checkers:
                color_initial = checkers[0].get_color()[0].upper()
                count = len(checkers)
                lower_line.append(f"{i:2d}({color_initial}{count})")
            else:
                lower_line.append(f"{i:2d}(--)")
        
        lines.append("Lower: " + " ".join(lower_line))
        
        # Mostrar off board
        off_white = len([c for c in self.__points[25] if c.get_color() == "white"])
        off_black = len([c for c in self.__points[25] if c.get_color() == "black"])
        lines.append(f"OFF: W={off_white}, B={off_black}")
        
        return "\n".join(lines)
    

    # ---------- M2-02: helpers de dirección y destino ----------

    def _validate_color(self, color: str) -> None:
        if color not in ("white", "black"):
            raise InvalidMoveException(f"Color inválido: {color}")

    def _direction_for(self, color: str) -> int:
        """white: -1 (24->1), black: +1 (1->24)"""
        self._validate_color(color)
        return -1 if color == "white" else +1

    def _target_from(self, color: str, from_pos: int, steps: int) -> int:
        """Calcula destino según color/dirección y pasos (valor del dado)."""
        if not isinstance(steps, int) or steps <= 0:
            raise InvalidMoveException("Los pasos deben ser un entero > 0.")
        if steps > 6:
            # si tus tests permiten >6 por otras reglas, ajustá; por ahora, básico
            raise InvalidMoveException("Valor de dado inválido (>6) para M2.")
        if not (1 <= from_pos <= 24):
            # mover desde bar/off o fuera del tablero no corresponde en M2-02
            raise InvalidPositionException("El origen debe estar en 1..24.")

        d = self._direction_for(color)
        return from_pos + d * steps

    def _has_checker_of_color(self, position: int, color: str) -> bool:
        """Hay al menos una ficha del color en 'position'."""
        if not (1 <= position <= 24):
            return False
        return any(ch.get_color() == color for ch in self.__points[position])

    def _can_land_on(self, color: str, position: int) -> bool:
        """
        Se puede caer en:
        - Punto vacío
        - Punto propio (>=1 del mismo color)
        - Punto rival con EXACTAMENTE 1 ficha (captura)
        Bloqueado si hay 2+ del rival.
        """
        if not (1 <= position <= 24):
            return False
        pile = self.__points[position]
        if not pile:
            return True
        top_color = pile[0].get_color()
        if top_color == color:
            return True
        # rival
        return len(pile) == 1  # blot -> capturable

    # ---------- M2-02: validador de movimiento básico ----------

    def validate_basic_move(self, color: str, from_pos: int, steps: int) -> int:
        """
        Valida un movimiento SINGLE (un dado).
        Reglas M2-02:
          - Origen 1..24 y contiene ficha del color.
          - steps en 1..6.
          - Dirección correcta según color.
          - Destino dentro de 1..24 (sin bearing off en M2).
          - Destino no bloqueado (no 2+ del rival).
        Devuelve: índice de destino si es válido.
        Lanza InvalidMoveException/InvalidPositionException si no.
        """
        self._validate_color(color)

        # origen válido y con ficha propia
        if not (1 <= from_pos <= 24):
            raise InvalidPositionException("El origen debe estar en 1..24.")
        if not self._has_checker_of_color(from_pos, color):
            raise InvalidMoveException("No hay ficha propia en el punto de origen.")

        # destino según dado y dirección
        to_pos = self._target_from(color, from_pos, steps)

        # sin bearing-off en M2
        if not (1 <= to_pos <= 24):
            raise InvalidMoveException("Destino fuera de 1..24 (bearing off no habilitado en M2).")

        # destino no bloqueado
        if not self._can_land_on(color, to_pos):
            raise InvalidMoveException("El destino está bloqueado por el rival.")

        return to_pos
    
    #Helpers de captura
    def _is_blot(self, position: int, color: str) -> bool:
        """True si en `position` hay exactamente 1 ficha del rival (capturable)."""
        if not (0 <= position <= 25):
            return False
        pile = self.__points[position]
        if len(pile) != 1:
            return False
        return pile[0].get_color() != color

    def can_capture(self, position: int, color: str) -> bool:
        """
    ¿Se puede capturar en `position`?
    Sí, si hay exactamente 1 ficha rival (blot).
    """
        if not self.is_valid_position(position):
            return False
    # Bar (0) y Off (25) no son objetivos de captura.
        if position in (0, 25):
            return False
        return self._is_blot(position, color)

    def _capture_at(self, position: int, color: str):
        """
    Efectúa la captura en `position` si hay blot rival.
    Devuelve la ficha capturada o None.
    Deja la ficha capturada en BAR (0) y le setea position=0.
    """
        if not self.is_valid_position(position):
            raise InvalidPositionException(position)

        if not self.can_capture(position, color):
           return None

        captured = self.__points[position].pop()
        captured.position = 0  # enviar al BAR
        self.__points[0].append(captured)
        return captured


    

    