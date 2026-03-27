# -*- coding: utf-8 -*-
"""
Motor de hints MUY simple y no intrusivo (no modifica estado).
La idea es dar una sugerencia razonable sin depender de APIs internas del motor.
"""
__all__ = ["suggest_move"]

from typing import Any


def suggest_move(game) -> str:
    st = game.state()

    def _get(obj, *names, default=None):
        for n in names:
            # soporta dict o objeto con atributos
            if isinstance(obj, dict) and n in obj:
                return obj[n]
            if hasattr(obj, n):
                return getattr(obj, n)
        return default

    dice = list(_get(st, "dice_values", "dice", default=[]) or [])
    moves_left = _get(st, "moves_left", "moves", default=0)
    color = _get(st, "current_color", "turn", "color", default="white")

    if not dice or moves_left == 0:
        return "No hay movimientos activos. Tir\u00E1 los dados con 'roll'."

    top = sorted(dice, reverse=True)[0]

    try:
        bar_count = game.board.count_at(0, color)
    except Exception:
        bar_count = 0

    if bar_count and bar_count > 0:
        return f"Prob\u00E1 reingresar desde BAR (0) usando el {top}."

    if color == "white":
        return f"Prob\u00E1 mover desde un punto alto (24..19) usando el {top}."
    else:
        return f"Prob\u00E1 mover desde un punto alto de tu direcci\u00F3n (1..6) usando el {top}."
