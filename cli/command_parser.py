# -*- coding: utf-8 -*-
"""
Parser de comandos para la CLI de Backgammon.

- Comandos soportados:
  quit|q|exit
  help|h|?
  show|status
  roll|r
  end
  move <from> <steps>        # <from>: 1..24 o 'bar' ; steps: 1..6
  hint
  undo
  save [ruta]                # opcionalmente una ruta de salida

- Errores:
  CommandParseError (subclase de core.exceptions.CommandParseError si está disponible)

- Salida:
  Un objeto Command con los campos relevantes para cada comando.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

# Intentamos heredar de la excepción del core para compatibilidad con el runner/CLI
try:
    from core.exceptions import CommandParseError as _CoreCommandParseError
except Exception:  # pragma: no cover
    _CoreCommandParseError = Exception


class CommandParseError(_CoreCommandParseError):
    """Error de parseo de comando (compatible con core.exceptions.CommandParseError si existe)."""
    pass


@dataclass
class Command:
    name: str
    # Para move:
    from_pos: Optional[int] = None
    steps: Optional[int] = None
    # Para save:
    path: Optional[str] = None


__all__ = ["Command", "CommandParseError", "parse_command"]


# ------------------------- Helpers -------------------------

def _parse_point(token: str) -> int:
    """
    Convierte el punto de origen:
      - 'bar' -> 0
      - 'off' -> 25  (alias aceptado por compatibilidad con tests)
      - '1'..'24' -> entero
    Lanza CommandParseError si no es válido.
    """
    t = token.strip().lower()
    if t == "bar":
        return 0
    if t == "off":
        return 25  # alias de borneadas
    try:
        val = int(t)
    except ValueError as ex:
        raise CommandParseError("from debe ser un entero entre 1 y 24 o 'bar'.") from ex
    if val < 1 or val > 24:
        raise CommandParseError("from debe estar entre 1 y 24 (o 'bar').")
    return val


# ------------------------- Parser principal -------------------------

def parse_command(raw: str) -> Command:
    """
    Parsea una línea cruda y devuelve un Command.
    Lanza CommandParseError ante entradas inválidas.
    """
    if raw is None:
        raise CommandParseError("Comando vacío. Escribí 'help' para ver opciones.")

    parts = raw.strip().split()
    if not parts:
        raise CommandParseError("Comando vacío. Escribí 'help' para ver opciones.")

    cmd = parts[0].lower()

    # quit / help / show / roll / end
    if cmd in ("quit", "q", "exit"):
        return Command(name="quit")

    if cmd in ("help", "h", "?"):
        return Command(name="help")

    if cmd in ("show", "status"):
        return Command(name="show")

    if cmd in ("roll", "r"):
        if len(parts) != 1:
            raise CommandParseError("Uso: roll")
        return Command(name="roll")

    if cmd == "end":
        if len(parts) != 1:
            raise CommandParseError("Uso: end")
        return Command(name="end")

    # move <from> <steps>
    if cmd == "move":
        if len(parts) != 3:
            raise CommandParseError("Uso: move <from> <steps>  (ej: 'move 13 5' o 'move bar 4')")

        from_pos = _parse_point(parts[1])

        try:
            steps = int(parts[2])
        except ValueError as ex:
            raise CommandParseError("steps debe ser un entero entre 1 y 6.") from ex
        if steps < 1 or steps > 6:
            raise CommandParseError("steps debe estar entre 1 y 6.")

        return Command(name="move", from_pos=from_pos, steps=steps)

    # hint
    if cmd == "hint":
        if len(parts) != 1:
            raise CommandParseError("Uso: hint")
        return Command(name="hint")

    # undo
    if cmd == "undo":
        if len(parts) != 1:
            raise CommandParseError("Uso: undo")
        return Command(name="undo")

    # save [path]
    if cmd == "save":
        if len(parts) > 2:
            raise CommandParseError("Uso: save [ruta]")
        path = parts[1] if len(parts) == 2 else None
        return Command(name="save", path=path)

    # Desconocido
    raise CommandParseError(f"Comando desconocido: {cmd}. Escribí 'help' para ver opciones.")
