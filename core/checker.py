
class Checker:
    """
    Representa una ficha individual en el juego de Backgammon.

    Atributos:
        __color__ (str): "WHITE" o "BLACK".
        __position__ (int|None): 1..24 puntos; 0 = barra; 25 = borne off; None = sin colocar.
    """

    # Colores normalizados (usaremos estos internamente)
    WHITE = "WHITE"
    BLACK = "BLACK"

    # Posiciones especiales
    BAR_POSITION = 0         # Fichas capturadas van a la barra
    BEAR_OFF_POSITION = 25   # Fichas sacadas del tablero

    def __init__(self, color: str, position: int | None = None) -> None:
        """
        Inicializa una ficha con color y (opcionalmente) posición.

        Args:
            color: "white"/"WHITE" o "black"/"BLACK"
            position: None, 0..25 (0=bar, 1..24 tablero, 25=bear off)

        Raises:
            ValueError: si el color o la posición no son válidos.
        """
        # Normalizamos color a MAYÚSCULAS
        norm = color.upper()
        if norm not in (self.WHITE, self.BLACK):
            raise ValueError(f"Color inválido: {color}. Debe ser 'WHITE' o 'BLACK'.")

        self.__color__ = norm
        self.__position__ = None
        # set via property to reuse validation
        self.position = position

    # ---------- Propiedades ----------
    @property
    def color(self) -> str:
        """Color de la ficha ("WHITE"/"BLACK")."""
        return self.__color__

    @property
    def position(self) -> int | None:
        """Posición actual (1..24), 0=bar, 25=bear off, None si no está colocada."""
        return self.__position__

    @position.setter
    def position(self, new_position: int | None) -> None:
        """Valida y actualiza la posición."""
        if new_position is not None:
            if not isinstance(new_position, int):
                raise ValueError("La posición debe ser un número entero o None.")
            if new_position < 0 or new_position > 25:
                raise ValueError("La posición debe estar entre 0 y 25, o None.")
        self.__position__ = new_position

    # ---------- Helpers de estado ----------
    def is_on_bar(self) -> bool:
        return self.__position__ == self.BAR_POSITION

    def is_borne_off(self) -> bool:
        return self.__position__ == self.BEAR_OFF_POSITION

    def is_on_board(self) -> bool:
        p = self.__position__
        return p is not None and 1 <= p <= 24

    # ---------- Movimiento ----------
    def move_to(self, new_position: int) -> int | None:
        """Mueve la ficha (usa el setter para validar) y devuelve la posición anterior."""
        old = self.__position__
        self.position = new_position
        return old

    def move_to_bar(self) -> int | None:
        return self.move_to(self.BAR_POSITION)

    def bear_off(self) -> int | None:
        return self.move_to(self.BEAR_OFF_POSITION)

    # ---------- Home board ----------
    def get_home_board_range(self) -> tuple[int, int]:
        """(1,6) para WHITE; (19,24) para BLACK."""
        return (1, 6) if self.__color__ == self.WHITE else (19, 24)

    def is_in_home_board(self) -> bool:
        if not self.is_on_board():
            return False
        start, end = self.get_home_board_range()
        return start <= self.__position__ <= end

    # ---------- Representaciones / comparación ----------
    def __str__(self) -> str:
        if self.is_on_bar():
            pos = "Bar"
        elif self.is_borne_off():
            pos = "BearOff"
        elif self.is_on_board():
            pos = f"Point {self.__position__}"
        else:
            pos = "Unplaced"
        return f"Checker({self.__color__}, {pos})"

    def __repr__(self) -> str:
        return f"Checker(color='{self.__color__}', position={self.__position__})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Checker) and \
               self.__color__ == other.__color__ and \
               self.__position__ == other.__position__

    def __hash__(self) -> int:
        return hash((self.__color__, self.__position__))
