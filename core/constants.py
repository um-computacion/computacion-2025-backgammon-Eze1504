# -*- coding: utf-8 -*-
from typing import Dict, Tuple

# Posiciones especiales del tablero
BAR: int = 0
OFF: int = 25

# Rangos de home por color
HOME_RANGE: Dict[str, Tuple[int, int]] = {
    "white": (1, 6),
    "black": (19, 24),
}

def opponent(color: str) -> str:
    if color == "white":
        return "black"
    if color == "black":
        return "white"
    raise ValueError(f"Color inválido: {color}")

__all__ = ["BAR", "OFF", "HOME_RANGE", "opponent"]
