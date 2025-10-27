class Checker:
    """
    Representa una ficha individual en el juego de Backgammon.
    Compatible con tests que usan getters estilo get_color/get_position.
    """

    # Constantes
    WHITE = "white"
    BLACK = "black"
    BAR_POSITION = 0
    BEAR_OFF_POSITION = 25

    def __init__(self, color: str, position: int | None = None):
        # normalizar y validar color
        color = str(color).lower()
        if color not in (self.WHITE, self.BLACK):
            raise ValueError(f"Color inválido: {color}. Debe ser '{self.WHITE}' o '{self.BLACK}'")
        self._color = color

        # Posición None por defecto; 0..25 válidas si se provee
        self._position = None
        if position is not None:
            self.set_position(position)

    # --------- API de propiedades "pythonic" ---------
    @property
    def color(self) -> str:
        return self._color

    @property
    def position(self) -> int | None:
        return self._position

    @position.setter
    def position(self, new_position: int | None):
        self.set_position(new_position)

    # --------- API de getters/setters estilo tests ---------
    def get_color(self) -> str:
        return self._color

    def get_position(self) -> int | None:
        return self._position

    def set_position(self, new_position: int | None):
        if new_position is not None:
            if not isinstance(new_position, int):
                raise ValueError("La posición debe ser un entero")
            if new_position < 0 or new_position > 25:
                raise ValueError("La posición debe estar entre 0 y 25")
        self._position = new_position

    # --------- Helpers de estado ---------
    def is_on_bar(self) -> bool:
        return self._position == self.BAR_POSITION

    def is_borne_off(self) -> bool:
        return self._position == self.BEAR_OFF_POSITION

    def is_on_board(self) -> bool:
        return self._position is not None and 1 <= self._position <= 24

    def get_home_board_range(self) -> tuple[int, int]:
        # Para que in_home_board sea 1 cuando hay una en 1 y otra en 5:
    # white -> 19..24 ; black -> 1..6
        if self._color == self.WHITE:
            return (19, 24)
        else:
            return (1, 6)
    def is_in_home_board(self) -> bool:
        if not self.is_on_board():
            return False
        lo, hi = self.get_home_board_range()
        return lo <= self._position <= hi

    # --------- Movimientos básicos ---------
    def move_to(self, new_position: int) -> int | None:
        old = self._position
        self.set_position(new_position)
        return old

    def move_to_bar(self) -> int | None:
        return self.move_to(self.BAR_POSITION)

    def bear_off(self) -> int | None:
        return self.move_to(self.BEAR_OFF_POSITION)

    # --------- Representaciones ---------
    def __str__(self) -> str:
        if self.is_on_bar():
            pos = "En barra"
        elif self.is_borne_off():
            pos = "Fuera del tablero"
        elif self.is_on_board():
            pos = f"Punto {self._position}"
        else:
            pos = "Sin posición"
        return f"Ficha {self._color} - {pos}"

    def __repr__(self) -> str:
        return f"Checker(color='{self._color}', position={self._position})"

    def __eq__(self, other) -> bool:
        return isinstance(other, Checker) and \
               self._color == other._color and \
               self._position == other._position

    def __hash__(self) -> int:
        return hash((self._color, self._position))
