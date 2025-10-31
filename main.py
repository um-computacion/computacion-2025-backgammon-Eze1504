# -*- coding: utf-8 -*-
from core.board import Board
from core.dice import Dice
from core.player import Player
from core.game import BackgammonGame
from cli.cli_runner import CommandRunner
from cli.command_parser import parse_command

def main():
    print("=== BACKGAMMON (modo consola) ===")
    print("Escribí 'help' para ver comandos, 'quit' para salir.\n")

    board = Board()
    dice = Dice()
    p1 = Player("White", "white")
    p2 = Player("Black", "black")
    game = BackgammonGame(board, dice, (p1, p2), starting_color="white")
    runner = CommandRunner(game)

    while True:
        try:
            raw = input(">>> ").strip()
            cmd = parse_command(raw)
            should_quit, msg = runner.execute(cmd)
            print(msg)
            if should_quit:
                break
        except Exception as ex:
            print(f"⚠️  {ex}")

if __name__ == "__main__":
    main()

