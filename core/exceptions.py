"""
Excepciones personalizadas para el juego de Backgammon.

Este módulo define todas las excepciones específicas del dominio del juego,
organizadas por categorías para facilitar el manejo de errores y la depuración.
"""


class BackgammonException(Exception):
    """
    Excepción base para todos los errores específicos del juego de Backgammon.
    
    Todas las excepciones personalizadas del juego deben heredar de esta clase
    para facilitar el manejo general de errores.
    """
    
    def __init__(self, message: str, error_code: str = None):
        """
        Inicializa la excepción base.
        
        Args:
            message (str): Mensaje descriptivo del error
            error_code (str, optional): Código de error para logging/debugging
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        
    def __str__(self) -> str:
        """Representación string de la excepción."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message
    
    # EXCEPCIONES DEL JUGADOR (PLAYER)

class PlayerException(BackgammonException):
    """Excepción base para errores relacionados con jugadores."""
    pass


class InvalidPlayerNameException(PlayerException):
    """Excepción lanzada cuando se proporciona un nombre de jugador inválido."""
    
    def __init__(self, name: str):
        message = f"Nombre de jugador inválido: '{name}'. El nombre no puede estar vacío."
        super().__init__(message, "INVALID_PLAYER_NAME")
        self.invalid_name = name


class InvalidPlayerColorException(PlayerException):
    """Excepción lanzada cuando se proporciona un color de jugador inválido."""
    
    def __init__(self, color: str, valid_colors: list = None):
        if valid_colors:
            valid_str = "', '".join(valid_colors)
            message = f"Color de jugador inválido: '{color}'. Colores válidos: '{valid_str}'"
        else:
            message = f"Color de jugador inválido: '{color}'"
        super().__init__(message, "INVALID_PLAYER_COLOR")
        self.invalid_color = color
        self.valid_colors = valid_colors or []

class NoCheckersAtPositionException(PlayerException):
    """Excepción lanzada cuando se intenta acceder a fichas en una posición vacía."""
    
    def __init__(self, player_name: str, position: int):
        message = f"El jugador '{player_name}' no tiene fichas en la posición {position}"
        super().__init__(message, "NO_CHECKERS_AT_POSITION")
        self.player_name = player_name
        self.position = position


class NegativeScoreException(PlayerException):
    """Excepción lanzada cuando se intenta añadir puntos negativos al score."""
    
    def __init__(self, points: int):
        message = f"No se pueden añadir puntos negativos: {points}"
        super().__init__(message, "NEGATIVE_SCORE")
        self.invalid_points = points

# EXCEPCIONES DE FICHAS (CHECKER)

class CheckerException(BackgammonException):
    """Excepción base para errores relacionados con fichas."""
    pass
class InvalidCheckerColorException(CheckerException):
    """Excepción lanzada cuando se crea una ficha con color inválido."""
    
    def __init__(self, color: str):
        message = f"Color de ficha inválido: '{color}'. Debe ser 'white' o 'black'"
        super().__init__(message, "INVALID_CHECKER_COLOR")
        self.invalid_color = color


class InvalidPositionException(CheckerException):
    """Excepción lanzada cuando se intenta mover una ficha a una posición inválida."""
    
    def __init__(self, position: int, valid_range: str = "0-25"):
        message = f"Posición inválida: {position}. Rango válido: {valid_range}"
        super().__init__(message, "INVALID_POSITION")
        self.invalid_position = position
        self.valid_range = valid_range


class CheckerNotMovableException(CheckerException):
    """Excepción lanzada cuando se intenta mover una ficha que no puede moverse."""
    
    def __init__(self, checker_id: str = None, reason: str = "La ficha no puede moverse"):
        message = f"Ficha {checker_id or 'desconocida'}: {reason}"
        super().__init__(message, "CHECKER_NOT_MOVABLE")
        self.checker_id = checker_id
        self.reason = reason
