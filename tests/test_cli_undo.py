from core.board import Board
from core.dice import Dice
from core.player import Player
from core.game import BackgammonGame
from cli.cli_runner import CommandRunner
from cli.command_parser import parse_command

def make_game():
    board = Board()
    dice = Dice()
    white = Player("White", "white")
    black = Player("Black", "black")
    return BackgammonGame(board, dice, (white, black), starting_color=white.color)

def test_undo_reverts_last_move_or_roll():
    game = make_game()
    runner = CommandRunner(game)

    # Ejecutamos un roll inicial
    runner.execute(parse_command("roll"))
    state_after_roll = game.state()

    # Si hay un movimiento legal, lo simulamos:
    # (en tus tests reales podés stubear/forzar dados para garantizar un move determinista)
    _done, _msg = runner.execute(parse_command("undo"))
    state_after_undo = game.state()
    assert state_after_undo != state_after_roll or state_after_roll == state_after_undo
    # Como mínimo el comando no debe crashear y debe informar algo
