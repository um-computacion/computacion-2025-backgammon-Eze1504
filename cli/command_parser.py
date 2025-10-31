# -*- coding: utf-8 -*-
"""
Parser de comandos para la CLI de Backgammon.

Comandos soportados:
  - roll
  - move <from> <steps>
  - end
  - show | status
  - help | h | ?
  - quit | q | exit

Notas:
  * <from>: 1..24, o 'bar' (0), 'off' (25)
  * <steps>: 1..6
"""

from dataclasses import dataclass

__all__ = ["Command", "parse_command"]

@dataclass
class Command:
    name: str
    from_pos: int | None = None
    steps: int | None = None


def _parse_point(token: str) -> int:
    """
    Convierte el token del origen a un entero:
      - 'bar' -> 0
      - 'off' -> 25
      - '1'..'24' -> int
    """
    t = token.strip().lower()
    if t == "bar":
        return 0
    if t == "off":
        return 25
    try:
        v = int(t)
    except ValueError as ex:
        raise ValueError("from debe ser un número, 'bar' o 'off'.") from ex
    if v < 0 or v > 25:
        raise ValueError("from fuera de rango (0..25). Usá 'bar' para 0 y 'off' para 25.")
    return v


def parse_command(raw: str) -> Command:
    """
    Parsea una línea cruda de la consola y devuelve un Command.
    Lanza ValueError ante entradas inválidas.
    """
    if raw is None:
        raise ValueError("Comando vacío. Escribí 'help' para ver opciones.")

    parts = raw.strip().split()
    if not parts:
        raise ValueError("Comando vacío. Escribí 'help' para ver opciones.")

    cmd = parts[0].lower()

    # quit / help / show / roll / end
    if cmd in ("quit", "q", "exit"):
        return Command(name="quit")

    if cmd in ("help", "h", "?"):
        return Command(name="help")

    if cmd in ("show", "status"):
        return Command(name="show")

    if cmd == "roll":
        if len(parts) != 1:
            raise ValueError("Uso: roll")
        return Command(name="roll")

    if cmd == "end":
        if len(parts) != 1:
            raise ValueError("Uso: end")
        return Command(name="end")

    # move <from> <steps>
    if cmd == "move":
        if len(parts) != 3:
            raise ValueError("Uso: move <from> <steps>  (ej: 'move 13 5' o 'move bar 4')")

        from_pos = _parse_point(parts[1])

        try:
            steps = int(parts[2])
        except ValueError as ex:
            raise ValueError("steps debe ser un entero entre 1 y 6.") from ex
        if steps < 1 or steps > 6:
            raise ValueError("steps debe estar entre 1 y 6.")

        return Command(name="move", from_pos=from_pos, steps=steps)

    # Desconocido
    raise ValueError(f"Comando desconocido: {cmd}. Escribí 'help' para ver opciones.")
