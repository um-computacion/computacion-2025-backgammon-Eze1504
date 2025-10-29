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

    BAR = 0
    OFF = 25
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

    # Permitir siempre colocar en BAR (0) y OFF (25)
        if position in (0, 25):
            return True

    # No se puede colocar en un punto bloqueado (2+ del rival)
        if self.is_point_blocked(position, player_color):
            return False

        return True
    def place_checker(self, checker: Checker, position: int) -> Optional[Checker]:
        """
        Coloca una ficha en una posición específica.
        """
        if not self.is_valid_position(position):
            raise InvalidPositionException(f"Posición {position} no es válida.")

    # ✅ 0 = BAR y 25 = OFF: siempre permitir y no aplicar capturas/bloqueos
        if position in (0, 25):
            checker.set_position(position)
            self.__points[position].append(checker)
            return None

    # del resto igual que antes:
        if not self.can_place_checker(position, checker.get_color()):
            raise InvalidPositionException(f"No se puede colocar ficha en posición {position}.")

        captured_checker = None
        point_checkers = self.__points[position]

    # Captura si hay exactamente 1 rival (blot)
        if (len(point_checkers) == 1 and 
           point_checkers[0].get_color() != checker.get_color()):
           captured_checker = point_checkers.pop()
           captured_checker.set_position(0)
           self.__points[0].append(captured_checker)

        checker.set_position(position)
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
        return [c for c in self.__points[0] if c.get_color() == player_color]
    
    def get_checkers_off_board(self, player_color: str) -> List[Checker]:
        """
        Obtiene las fichas de un jugador que están fuera del tablero (sacadas).
        
        Args:
            player_color (str): Color del jugador
            
        Returns:
            List[Checker]: Lista de fichas del jugador fuera del tablero
        """
        return [c for c in self.__points[25] if c.get_color() == player_color]
    
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
        if not isinstance(steps, int) or steps <= 0 or steps > 6:
            raise ValueError("Los pasos deben ser un entero entre 1 y 6.")

        # dirección: white baja, black sube
        to_pos = from_pos - steps if color == "white" else from_pos + steps

        # En M2 no hay bearing off: destino debe quedar en 1..24
        if not (1 <= to_pos <= 24):
            raise InvalidPositionException("El destino debe estar en 1..24 en M2.")
    
        return to_pos
    
    def _has_checker_of_color(self, position: int, color: str) -> bool:
        """Hay al menos una ficha del color en 'position'."""
        if not (1 <= position <= 24):
            return False
        return any(ch.get_color() == color for ch in self.__points[position])
    
    def _is_blot(self, position: int, color: str) -> bool:
        """
    Verifica si hay un blot (ficha vulnerable) en la posición.
    Un blot es exactamente 1 ficha del oponente.
    
    Args:
        position: Posición a verificar
        color: Color del jugador que podría capturar
        
    Returns:
        bool: True si hay exactamente 1 ficha rival, False en caso contrario
    """
        if not (1 <= position <= 24):
            return False
    
        pile = self.__points[position]
        if len(pile) != 1:
            return False
    
    # Verificar que la única ficha es del oponente
        opponent_color = "black" if color == "white" else "white"
        return pile[0].get_color() == opponent_color

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
        self._validate_color(color)

        if not (1 <= from_pos <= 24):
            raise InvalidPositionException("El origen debe estar en 1..24.")

    # PRIMERO: Verificar que hay ficha propia (ANTES de calcular destino)
        if not self._has_checker_of_color(from_pos, color):
            raise ValueError("No hay ficha propia en el punto de origen.")

    # SEGUNDO: Calcular y validar destino
        to_pos = self._target_from(color, from_pos, steps)

    # TERCERO: Verificar que el destino no esté bloqueado
        if self.is_point_blocked(to_pos, color):
            raise ValueError("El destino está bloqueado por el oponente.")

        return to_pos

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

#Movimiento con captura
     
    def move_checker(self, color: str, from_pos: int, steps: int):
        """
    Mueve UNA ficha del color `color` desde `from_pos` con `steps` (1..6).
    Usa validate_basic_move para validar reglas básicas.
    Si el destino tiene blot rival, lo captura y lo envía al BAR.
    Devuelve (from_pos, to_pos, captured_checker|None).
    """
    # 1) Validación de movimiento (dirección, rango, bloqueo, etc.)
        to_pos = self.validate_basic_move(color, from_pos, steps)

    # 2) Quitar ficha del origen (debe existir y ser del color)
        origin_stack = self.__points[from_pos]
        if not origin_stack or origin_stack[-1].get_color() != color:
            found_idx = next((i for i, ch in enumerate(origin_stack) if ch.get_color() == color), None)
            if found_idx is None:
               raise ValueError("No hay ficha propia en el punto de origen.")
            checker = origin_stack.pop(found_idx)
        else:
            checker = origin_stack.pop()

    # 3) Captura si hay blot rival en el destino
        captured = self._capture_at(to_pos, color)

    # 4) Colocar la ficha movida
        checker.position = to_pos
        self.__points[to_pos].append(checker)

        return (from_pos, to_pos, captured)
    
    #M2-04 — Reingreso desde el BAR

    def has_checkers_in_bar(self, color: str) -> bool:
        return any(ch.get_color() == color for ch in self.__points[0])
    
    def validate_reentry(self, color: str, steps: int) -> int:
        if steps < 1 or steps > 6:
            raise InvalidMoveException("Valor inválido del dado")

    # Calcular destino según color
        if color == "white":
            destination = 25 - steps
        else:  # black
            destination = steps

        if not self.is_valid_position(destination):
            raise InvalidMoveException("Destino fuera del tablero al reingresar")

    # No puede reingresar si el destino está bloqueado
        if self.is_point_blocked(destination, color):
            raise InvalidMoveException(f"Entrada bloqueada en posición {destination}", destination)

        return destination
    
    def reenter_checker(self, color: str, steps: int):
        """Mueve una ficha desde el BAR al tablero según steps (1..6)."""
        if not self.has_checkers_in_bar(color):
            raise InvalidMoveException("No hay fichas para reingresar desde el BAR")

        destination = self.validate_reentry(color, steps)

         # Tomar ficha del BAR
        bar_stack = self.__points[0]
        checker = next(ch for ch in bar_stack if ch.get_color() == color)
        bar_stack.remove(checker)

        # Captura si hay blot rival
        captured = self._capture_at(destination, color)

         # Colocar ficha en destino
        checker.position = destination
        self.__points[destination].append(checker)

        return (0, destination, captured)
    
        # ---------------- M4: Bearing Off (sacar fichas) ----------------

    def _in_home_board(self, color: str, position: int) -> bool:
        """True si 'position' está dentro del home board del 'color'."""
        start, end = self.get_home_board_range(color)
        return start <= position <= end

    def _has_checkers_beyond(self, color: str, from_pos: int) -> bool:
        """
        ¿Hay fichas propias 'más lejos' que from_pos dentro del home?
        - white: más lejos = posiciones mayores (hacia 6) dentro del home (from_pos+1..6)
        - black: más lejos = posiciones menores (hacia 19) dentro del home (19..from_pos-1)
        Se usa para la regla de 'overshoot'.
        """
        home_start, home_end = self.get_home_board_range(color)
        if color == "white":
            rng = range(from_pos + 1, home_end + 1)  # ej:  from=3 => [4..6]
        else:
            rng = range(home_start, from_pos)        # ej:  from=22 => [19..21]

        for p in rng:
            pile = self.__points[p]
            if any(ch.get_color() == color for ch in pile):
                return True
        return False

    def can_bear_off_from(self, color: str, from_pos: int, steps: int) -> bool:
        """
        Regla de bearing off:
        - Todas las fichas del color deben estar en su home board.
        - from_pos debe estar dentro del home board del color.
        - Exacto: white -> from_pos - steps == 0  | black -> from_pos + steps == 25 (no usamos 25 como casilla, pero equivalencia de 'salir')
        - Overshoot permitido SOLO si no hay fichas más lejos en el home.
          * white: si from_pos - steps < 1, se permite si no hay fichas en posiciones > from_pos dentro del home.
          * black: si from_pos + steps > 24, se permite si no hay fichas en posiciones < from_pos dentro del home.
        """
        # 1) Todas las fichas en home
        if not self.all_checkers_in_home_board(color):
            return False

        # 2) Origen en home
        if not self._in_home_board(color, from_pos):
            return False

        # 3) Exacto u overshoot
        if color == "white":
            to_pos = from_pos - steps
            if to_pos == 0:
                return True
            if to_pos < 1:
                # overshoot: dejar salir SOLO si no hay fichas por encima en el home
                return not self._has_checkers_beyond(color, from_pos)
            return False
        else:
            to_pos = from_pos + steps
            if to_pos == 25:
                return True
            if to_pos > 24:
                # overshoot para negro: no debe haber fichas por debajo en el home
                return not self._has_checkers_beyond(color, from_pos)
            return False
        


    def bear_off_checker(self, color: str, from_pos: int, steps: int):
        """
    Saca UNA ficha desde 'from_pos' usando 'steps' (1..6).
    Requisitos:
      - can_bear_off_from(color, from_pos, steps) == True
    Efecto:
      - Remueve la ficha del origen y la coloca en OFF (25).
    Devuelve (from_pos, OFF, None)
    """
        if not self.can_bear_off_from(color, from_pos, steps):
            raise InvalidMoveException("No se puede hacer bearing off desde esa posición con ese dado.")

        pile = self.__points[from_pos]
    # Buscar una ficha del color en el origen
        idx = next((i for i, ch in enumerate(pile) if ch.get_color() == color), None)
        if idx is None:
            raise NoCheckersAtPositionException(f"No hay ficha del color {color} en {from_pos}.")
    
        checker = pile.pop(idx)
        checker.set_position(self.OFF)
        self.__points[self.OFF].append(checker)

        return (from_pos, self.OFF, None)
   


    def move_or_bear_off(self, color: str, from_pos: int, steps: int):
        """
        Movimiento normal o bearing off según corresponda.
        - Si el destino cae fuera (blanco <1 | negro >24) y se puede bear off, hace bear_off_checker.
        - Si el destino cae dentro (1..24), usa move_checker normal.
        """
        # ¿Dentro del tablero?
        try:
            # Intentamos validar como movimiento normal
            to_pos = self._target_from(color, from_pos, steps)
            # si _target_from no explota, estaríamos en 1..24 (M4: _target_from ya no bloquea por 'fuera de 1..24')
            # En tu implementación actual _target_from lanza si no está en 1..24 (M2).
            # Así que si lanza, iremos al except y probamos bearing off.
            return self.move_checker(color, from_pos, steps)
        except InvalidPositionException:
            # Destino afuera de 1..24 => intentar bearing off
            return self.bear_off_checker(color, from_pos, steps)

    # ---------------- Helpers públicos de testing ----------------

    def count_checkers_at(self, position: int, color: Optional[str] = None) -> int:
        """Cuenta fichas en 'position'. Si color no es None, filtra por color."""
        if not self.is_valid_position(position):
            raise InvalidPositionException(f"Posición {position} no es válida.")
        if color is None:
            return len(self.__points[position])
        return sum(1 for ch in self.__points[position] if ch.get_color() == color)

    def set_count_at(self, position: int, color: str, count: int) -> None:
        """
        Helper de test: fuerza la cantidad de fichas de 'color' en 'position'.
        - Remueve fichas de ambos colores en 'position'.
        - Agrega 'count' fichas del color indicado en ese punto.
        """
        if not self.is_valid_position(position):
            raise InvalidPositionException(f"Posición {position} no es válida.")

        # Vaciar el punto
        self.__points[position].clear()
        # Agregar 'count' fichas del color
        for _ in range(max(0, count)):
            self.__points[position].append(Checker(color, position))










    