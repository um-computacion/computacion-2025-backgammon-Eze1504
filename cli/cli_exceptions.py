# -*- coding: utf-8 -*-
class CommandParseError(ValueError):
    """Errores al parsear una línea de comando (sintaxis/validación)."""
    pass

class CommandExecError(RuntimeError):
    """Errores al ejecutar un comando válido contra el juego (estado/reglas)."""
    pass
