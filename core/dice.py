
from __future__ import annotations
import random
from typing import List, Optional, Tuple

class Dice:
    MIN_VALUE = 1
    MAX_VALUE = 6
    NUM_DICE  = 2

    def __init__(self, seed: Optional[int] = None) -> None:
        self._rng = random.Random(seed)
        self.last_roll: Optional[Tuple[int, int]] = None
        self.available_moves: List[int] = []
        self.used_moves: List[int] = []

    # ---------- helpers internos ----------
    def _apply_roll(self, a: int, b: int) -> None:
        self.last_roll = (a, b)
        self.used_moves.clear()
        if a == b:
            self.available_moves[:] = [a, a, a, a]
        else:
            self.available_moves[:] = [a, b]

    # ---------- API pública ----------
    def roll(self) -> Tuple[int, int]:
        a = self._rng.randint(self.MIN_VALUE, self.MAX_VALUE)
        b = self._rng.randint(self.MIN_VALUE, self.MAX_VALUE)
        self._apply_roll(a, b)
        return (a, b)

    def simulate_roll(self, a: int, b: int) -> Tuple[int, int]:
        if not (self.MIN_VALUE <= a <= self.MAX_VALUE):
            raise ValueError(f"Valor del dado 1 inválido: {a}")
        if not (self.MIN_VALUE <= b <= self.MAX_VALUE):
            raise ValueError(f"Valor del dado 2 inválido: {b}")
        self._apply_roll(a, b)
        return (a, b)

    def reset_moves(self) -> None:
        if self.last_roll is None:
            self.available_moves.clear()
            self.used_moves.clear()
            return
        a, b = self.last_roll
        self._apply_roll(a, b)

    def use_move(self, value: int) -> bool:
        """
        Marca un movimiento como usado.
        Lanza ValueError si no está disponible (los tests lo requieren).
        """
        try:
            idx = self.available_moves.index(value)
        except ValueError:
            raise ValueError(f"Movimiento {value} no está disponible. Disponibles: {self.available_moves}")
        self.available_moves.pop(idx)
        self.used_moves.append(value)
        return True

    def can_use_move(self, value: int) -> bool:
        return value in self.available_moves

    def get_possible_move_values(self) -> List[int]:
        return sorted(set(self.available_moves))

    # ---------- consultas/alias para tests ----------
    def has_moves_available(self) -> bool:
        return len(self.available_moves) > 0

    def has_moves(self) -> bool:
        return self.has_moves_available()

    def is_double(self) -> bool:
        return self.last_roll is not None and self.last_roll[0] == self.last_roll[1]

    def get_moves_summary(self) -> dict:
        return {
            "last_roll": self.last_roll,
            "is_double": self.is_double(),
            "available_moves": list(self.available_moves),
            "used_moves": list(self.used_moves),
            "moves_remaining": len(self.available_moves),
            "has_moves": self.has_moves_available(),
        }

    # ---------- representaciones ----------
    def __str__(self) -> str:
        if self.last_roll is None:
            return "Dados sin tirar"
        a, b = self.last_roll
        kind = "doble" if a == b else "normal"
        return f"Dados: [{a}, {b}] - Tirada {kind} - {len(self.available_moves)} movimientos restantes"

    def __repr__(self) -> str:
        return f"Dice(last_roll={self.last_roll}, available={self.available_moves}, used={self.used_moves})"
