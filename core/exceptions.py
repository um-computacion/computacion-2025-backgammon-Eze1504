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