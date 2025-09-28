class Checker:
    """
    Representa una ficha individual en el juego de Backgammon.
    
    Una ficha tiene un color que determina a qué jugador pertenece
    y puede estar en diferentes posiciones del tablero o en la barra.
    """
    
    # Constantes para los colores de las fichas
    WHITE = "white"
    BLACK = "black"

     # Constantes para posiciones especiales
    BAR_POSITION = 0     # Fichas capturadas van a la barra
    BEAR_OFF_POSITION = 25  # Fichas sacadas del tablero
    
    def __init__(self, color):
        """
        Inicializa una nueva ficha.
        
        Args:
            color (str): Color de la ficha, debe ser "white" o "black"
            
        Raises:
            ValueError: Si el color no es válido
        """
        if color not in [self.WHITE, self.BLACK]:
            raise ValueError(f"Color inválido: {color}. Debe ser '{self.WHITE}' o '{self.BLACK}'")
        
        self._color = color
        self._position = None  # Posición inicial será establecida por el tablero
    
    @property
    def color(self):
        """
        Obtiene el color de la ficha.
        
        Returns:
            str: Color de la ficha ("white" o "black")
        """
        return self._color
    
    @property
    def position(self):
        """
        Obtiene la posición actual de la ficha.
        
        Returns:
            int: Posición actual (1-24 para puntos del tablero, 
                 0 para barra, 25 para bear-off, None si no está colocada)
        """
        return self._position
    
    @position.setter
    def position(self, new_position):
        """
        Establece la posición de la ficha.
        
        Args:
            new_position (int or None): Nueva posición de la ficha
            
        Raises:
            ValueError: Si la posición no es válida
        """
        if new_position is not None:
            if not isinstance(new_position, int):
                raise ValueError("La posición debe ser un número entero")
            
            if new_position < 0 or new_position > 25:
                raise ValueError("La posición debe estar entre 0 y 25")
        
        self._position = new_position
    
    def is_on_bar(self):
        """
        Verifica si la ficha está en la barra (capturada).
        
        Returns:
            bool: True si la ficha está en la barra, False en caso contrario
        """
        return self._position == self.BAR_POSITION
    
    def is_borne_off(self):
        """
        Verifica si la ficha ha sido sacada del tablero (bear-off).
        
        Returns:
            bool: True si la ficha está fuera del tablero, False en caso contrario
        """
        return self._position == self.BEAR_OFF_POSITION
    
    def is_on_board(self):
        """
        Verifica si la ficha está en una posición normal del tablero.
        
        Returns:
            bool: True si está en los puntos 1-24, False en caso contrario
        """
        return self._position is not None and 1 <= self._position <= 24
    
    def move_to(self, new_position):
        """
        Mueve la ficha a una nueva posición.
        
        Args:
            new_position (int): Nueva posición destino
            
        Returns:
            int: Posición anterior de la ficha
            
        Raises:
            ValueError: Si la nueva posición no es válida
        """
        old_position = self._position
        self.position = new_position  # Usa el setter para validar
        return old_position
    
    def move_to_bar(self):
        """
        Mueve la ficha a la barra (cuando es capturada).
        
        Returns:
            int: Posición anterior de la ficha
        """
        return self.move_to(self.BAR_POSITION)
    
    def bear_off(self):
        """
        Saca la ficha del tablero (bear-off).
        
        Returns:
            int: Posición anterior de la ficha
        """
        return self.move_to(self.BEAR_OFF_POSITION)
    
    def get_home_board_range(self):
        """
        Obtiene el rango del home board para esta ficha según su color.
        
        Returns:
            tuple: (inicio, fin) del rango del home board
        """
        if self._color == self.WHITE:
            return (1, 6)  # Puntos 1-6 para fichas blancas
        else:
            return (19, 24)  # Puntos 19-24 para fichas negras
    
    def is_in_home_board(self):
        """
        Verifica si la ficha está en su home board.
        
        Returns:
            bool: True si está en el home board, False en caso contrario
        """
        if not self.is_on_board():
            return False
        
        start, end = self.get_home_board_range()
        return start <= self._position <= end
    
    def __str__(self):
        """
        Representación como string de la ficha.
        
        Returns:
            str: Representación legible de la ficha
        """
        position_str = "Sin posición"
        if self.is_on_bar():
            position_str = "En barra"
        elif self.is_borne_off():
            position_str = "Fuera del tablero"
        elif self.is_on_board():
            position_str = f"Punto {self._position}"
        
        return f"Ficha {self._color} - {position_str}"
    
    def __repr__(self):
        """
        Representación técnica de la ficha.
        
        Returns:
            str: Representación técnica para debugging
        """
        return f"Checker(color='{self._color}', position={self._position})"
    
    def __eq__(self, other):
        """
        Compara dos fichas por igualdad.
        
        Args:
            other: Otra ficha a comparar
            
        Returns:
            bool: True si las fichas son iguales (mismo color y posición)
        """
        if not isinstance(other, Checker):
            return False
        return self._color == other._color and self._position == other._position
    
    def __hash__(self):
        """
        Genera hash de la ficha para uso en sets y diccionarios.
        
        Returns:
            int: Hash basado en color y posición
        """
        return hash((self._color, self._position))