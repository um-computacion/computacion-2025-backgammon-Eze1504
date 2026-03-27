# -*- coding: utf-8 -*-
"""
Renderizado ASCII del tablero de Backgammon para consola.
- Muestra puntos 13..24 arriba y 12..1 abajo
- Indica cantidad y color (W/B) por punto
- Muestra BAR y OFF por color
- Si se pasa un `game`, también muestra los dados actuales
"""
from typing import List
from core.constants import BAR, OFF
from core.checker import Checker

def _cell_token(checkers: List[Checker]) -> str:
    """Devuelve un token compacto para un punto: '--', 'W3', 'B5'."""
    if not checkers:
        return "--"
    color = checkers[0].get_color()
    count = sum(1 for c in checkers if c.get_color() == color)
    initial = "W" if color == "white" else "B"
    return f"{initial}{count}"

def render_board(board) -> str:
    """
    Devuelve un string ASCII con:
      - fila superior: puntos 13..24
      - fila inferior: puntos 12..1
      - BAR y OFF por color
    """
    lines = []
    lines.append("Backgammon — Vista ASCII")
    lines.append("=" * 64)

    # Fila superior (13..24)
    top_nums = " ".join([f"{i:>2}" for i in range(13, 25)])
    top_cells = " ".join([f"{_cell_token(board.get_point(i)):>2}" for i in range(13, 25)])
    lines.append(f"   Puntos ↑: {top_nums}")
    lines.append(f"     Fichas: {top_cells}")

    # BAR
    bar_w = sum(1 for c in board.get_point(BAR) if c.get_color() == "white")
    bar_b = sum(1 for c in board.get_point(BAR) if c.get_color() == "black")
    lines.append(f"        BAR: W={bar_w} | B={bar_b}")

    # Fila inferior (12..1)
    bottom_nums = " ".join([f"{i:>2}" for i in range(12, 0, -1)])
    bottom_cells = " ".join([f"{_cell_token(board.get_point(i)):>2}" for i in range(12, 0, -1)])
    lines.append(f" Puntos ↓  : {bottom_nums}")
    lines.append(f"     Fichas: {bottom_cells}")

    # OFF
    off_w = sum(1 for c in board.get_point(OFF) if c.get_color() == "white")
    off_b = sum(1 for c in board.get_point(OFF) if c.get_color() == "black")
    lines.append(f"        OFF: W={off_w} | B={off_b}")

    return "\n".join(lines)

def render_game(game) -> str:
    """
    Como render_board(), pero incluye info de turno/dados si hay turno activo.
    """
    body = render_board(game.board)
    try:
        st = game.state()  # TurnState
        dice = getattr(st, "dice_values", None)
        moves = getattr(st, "moves_left", None)
        who = getattr(st, "current_color", None)
        if dice is not None:
            info = f"\nTurno de {who} — Dados: {tuple(dice)} (movimientos: {moves})"
            return body + info
    except Exception:
        pass
    return body

__all__ = ["render_board", "render_game"]
