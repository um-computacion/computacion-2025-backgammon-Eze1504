import builtins
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
    game = BackgammonGame(board, dice, (white, black), starting_color=white.color)
    return game

def test_hint_does_not_mutate_state():
    game = make_game()
    runner = CommandRunner(game)
    # snapshot simple: cantidad total de fichas por color en tablero + bar + off
    before = game.state()  # asumimos que expone posiciones/bar/off y turno
    done, msg = runner.execute(parse_command("hint"))
    assert done is False
    assert isinstance(msg, str) and len(msg) > 0
    after = game.state()
    assert after == before, "hint no debe mutar el estado del juego"

