# -*- coding: utf-8 -*-
"""
Punto de entrada para jugar Backgammon desde la consola.
"""

from core.board import Board
from core.dice import Dice
from core.player import Player
from core.game import BackgammonGame
from cli.cli_runner import CommandRunner
from cli.command_parser import parse_command
from core.exceptions import CommandParseError  # Fuente única del error de parseo

def main():
    print("🎲 Bienvenido al Backgammon CLI 🎲")
    print("Escribí 'help' para ver los comandos disponibles.\n")

    board = Board()
    dice = Dice()
    white = Player("White", "white")
    black = Player("Black", "black")

    # Evitamos hardcodear el color y usamos el del objeto Player
    game = BackgammonGame(board, dice, (white, black), starting_color=white.color)
    runner = CommandRunner(game)

    while True:
        try:
            line = input("> ").strip()
            if not line:
                continue
            cmd = parse_command(line)
            done, msg = runner.execute(cmd)
            if msg:
                print(msg)
            if done:
                print("👋 ¡Gracias por jugar!")
                break

        except CommandParseError as ex:
            print(f"⚠️  Error de comando: {ex}")

        except KeyboardInterrupt:
            print("\n👋 Saliste con Ctrl+C")
            break

        except EOFError:
            print("\n👋 Entrada finalizada (EOF). ¡Hasta la próxima!")
            break

        except Exception as ex:
            print(f"💥 Ocurrió un error: {ex}")

if __name__ == "__main__":
    main()
