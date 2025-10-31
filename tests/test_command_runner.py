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
    def reset(self, values):
        self._avail = list(values)

    def roll(self):
        # no-op en test; usar reset(values)
        pass

    def available_moves(self):
        return list(self._avail)

    def use_move(self, val: int):
        self._avail.remove(val)

def test_help_and_quit_dont_crash():
    b = Board()
    d = DummyDice(); d.reset((3,5))
    w, k = Player("W", "white"), Player("K", "black")
    g = BackgammonGame(b, d, (w,k), starting_color=w.color)
    runner = CommandRunner(g)

    done, msg = runner.execute(parse_command("help"))
    assert done is False and "Comandos disponibles" in msg

    done, msg = runner.execute(parse_command("quit"))
    assert done is True

def test_roll_then_move_flow_ok():
    b = Board()
    d = DummyDice(); d.reset((1,1))  # dobles simples para probar
    w, k = Player("W", "white"), Player("K", "black")
    g = BackgammonGame(b, d, (w,k), starting_color=w.color)
    runner = CommandRunner(g)

    done, msg = runner.execute(parse_command("roll"))
    assert done is False and "Turno de" in msg

    # Mover desde 24 con white con paso 1 es válido por posición inicial
    # (el motor del juego validará según tus reglas)
    done, msg = runner.execute(parse_command("move 24 1"))
    assert done is False and "Dados restantes" in msg

def test_move_rejected_with_clear_message():
    b = Board()
    d = DummyDice(); d.reset((2,5))
    w, k = Player("W", "white"), Player("K", "black")
    g = BackgammonGame(b, d, (w,k), starting_color=w.color)
    runner = CommandRunner(g)

    runner.execute(parse_command("roll"))
    # Intentá un movimiento con dado no disponible
    with pytest.raises(CommandExecError):
        runner.execute(parse_command("move 24 6"))
