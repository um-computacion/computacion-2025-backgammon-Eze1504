# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import Optional
from .cli_exceptions import CommandParseError

@dataclass(frozen=True)
class Command:
    name: str                 # "move", "roll", "quit", "help"
    from_pos: Optional[int] = None
    steps: Optional[int] = None

_MOVE_ALIASES = {"move", "m"}
_ROLL_ALIASES = {"roll", "r"}
_QUIT_ALIASES = {"quit", "exit", "q"}
_HELP_ALIASES = {"help", "h", "?"}

def _parse_int(token: str) -> int:
    try:
        return int(token, 10)
    except Exception:
        raise CommandParseError(f"Se esperaba un número entero y llegó: '{token}'")

def _normalize_from_pos(tok: str) -> int:
    t = tok.strip().lower()
    if t in {"bar", "b"}:
        return 0
    if t in {"off"}:
        return 25
    val = _parse_int(t)
    if not (0 <= val <= 25):
        raise CommandParseError("El origen debe estar entre 0 (bar) y 25 (off).")
    return val

def _normalize_steps(tok: str) -> int:
    val = _parse_int(tok)
    if not (1 <= val <= 6):
        raise CommandParseError("Los pasos (dado) deben estar entre 1 y 6.")
    return val

def _normalize_command_name(head: str) -> str:
    h = head.strip().lower()
    if h in _MOVE_ALIASES:
        return "move"
    if h in _ROLL_ALIASES:
        return "roll"
    if h in _QUIT_ALIASES:
        return "quit"
    if h in _HELP_ALIASES:
        return "help"
    raise CommandParseError(f"Comando desconocido: '{head}'. Probá 'help'.")

def parse_command(line: str) -> Command:
    """
    Parsea una línea de texto en un Command.
    Formatos:
      - move <from> <steps>   (ej. 'move 13 5', 'move bar 4')
      - roll
      - quit
      - help
    """
    if line is None:
        raise CommandParseError("Entrada vacía.")
    parts = [p for p in line.strip().split() if p]
    if not parts:
        raise CommandParseError("Entrada vacía.")

    cmd = _normalize_command_name(parts[0])

    if cmd == "move":
        if len(parts) != 3:
            raise CommandParseError("Uso: move <from> <steps>. Ej: 'move 13 5' o 'move bar 4'.")
        from_pos = _normalize_from_pos(parts[1])
        steps = _normalize_steps(parts[2])
        return Command(name="move", from_pos=from_pos, steps=steps)

    if cmd in ("roll", "quit", "help"):
        if len(parts) != 1:
            raise CommandParseError(f"'{cmd}' no acepta parámetros.")
        return Command(name=cmd)

    # No debería llegar
    raise CommandParseError(f"Comando no soportado: '{cmd}'")

__all__ = ["parse_command", "Command"]
