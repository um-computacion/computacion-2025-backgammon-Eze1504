# -*- coding: utf-8 -*-
import pytest
from core.board import Board
from core.dice import Dice
from core.player import Player
from core.game import BackgammonGame
from cli.command_parser import parse_command
from cli.cli_runner import CommandRunner
from cli.cli_exceptions import CommandExecError

class DummyDice(Dice):
    """Dados deterministas para test."""
    def __init__(self):
        super().__init__()
    
    def reset(self, values):
        """Simula un roll con valores específicos."""
        if len(values) < 2:
            raise ValueError("reset() necesita al menos 2 valores")
        a, b = values[0], values[1]
        self._apply_roll(a, b)  # Usa el método heredado de Dice
    
    def roll(self):
        """No tira dados reales - usar reset() para configurar valores."""
        # Retornar el último roll si existe, sino (1,1) por defecto
        if self.last_roll:
            return self.last_roll
        # Si nunca se llamó reset, comportarse como un roll normal de (1,1)
        self._apply_roll(1, 1)
        return (1, 1)