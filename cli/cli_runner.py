# -*- coding: utf-8 -*-
from typing import Tuple
from .command_parser import Command
from .cli_exceptions import CommandExecError
from core.exceptions import InvalidMoveException

class CommandRunner:
    def __init__(self, game) -> None:
        self.game = game

    def execute(self, cmd: Command) -> Tuple[bool, str]:
        if cmd.name == "help":
            return (False, self._help_text())
        if cmd.name == "quit":
            return (True, "Saliendo del juego.")
        if cmd.name == "roll":
            try:
                self.game.start_turn()
            except Exception as ex:
                raise CommandExecError(str(ex)) from ex
            st = self.game.state()
            return (False, f"Turno de {st.current_color}. Dados: {st.dice_values} (movimientos: {st.moves_left})")

        if cmd.name == "move":
            try:
                self.game.apply_player_move(cmd.from_pos, cmd.steps)
            except InvalidMoveException as ex:
                raise CommandExecError(f"Movimiento inválido: {ex}") from ex
            except Exception as ex:
                raise CommandExecError(str(ex)) from ex

            if getattr(self.game, "game_over", False):
                r = self.game.result
                return (True, f"Juego terminado. Ganador: {r.winner_color} ({r.outcome}, {r.points} punto(s)).")

            st = self.game.state()
            return (False, f"OK. Dados restantes: {st.dice_values} (movimientos: {st.moves_left})")

        raise CommandExecError(f"Comando no ejecutable: {cmd.name}")

    @staticmethod
    def _help_text() -> str:
        return (
            "Comandos disponibles:\n"
            "  - roll                  : inicia el turno y tira los dados\n"
            "  - move <from> <steps>   : mueve una ficha (ej: 'move 13 5', 'move bar 4')\n"
            "  - help                  : muestra esta ayuda\n"
            "  - quit                  : salir\n"
            "\nNotas:\n"
            "  * 'bar' equivale a 0 (reingreso), 'off' equivale a 25.\n"
            "  * 'steps' debe estar entre 1 y 6.\n"
            "  * Las reglas del juego se validan en el motor.\n"
        )

__all__ = ["CommandRunner"]
