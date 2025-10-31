# -*- coding: utf-8 -*-
"""
Punto de entrada para jugar Backgammon desde la consola.
"""

from core.board import Board
from core.dice import Dice
from core.player import Player
from core.game import BackgammonGame
from cli.cli_runner import CommandRunner
from cli.command_parser import parse_command, CommandParseError
from core.exceptions import CommandParseError
def main():
    print("🎲 Bienvenido al Backgammon CLI 🎲")
    print("Escribí 'help' para ver los comandos disponibles.\n")

    board = Board()
    dice = Dice()
    white = Player("White", "white")
    black = Player("Black", "black")
    game = BackgammonGame(board, dice, (white, black), starting_color="white")
    runner = CommandRunner(game)

    while True:
        try:
            line = input("> ")
            cmd = parse_command(line)
            done, msg = runner.execute(cmd)
            print(msg)
            if done:
                break
        except CommandParseError as ex:
            print(f"⚠️  Error: {ex}")
        except Exception as ex:
            print(f"💥 Ocurrió un error: {ex}")

if __name__ == "__main__":
    main()
