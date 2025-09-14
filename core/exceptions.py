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
