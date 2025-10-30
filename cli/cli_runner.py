# -*- coding: utf-8 -*-
from typing import Tuple
from core.command_parser import Command
from cli.cli_exceptions import CommandExecError
from core.exceptions import InvalidMoveException  # tus propias excepciones
from core.constants import BAR

class CommandRunner:
    """
    Puente sin I/O entre comandos parseados y BackgammonGame.
    Devuelve (done, message):
      - done=True si el comando implica terminar (quit) o juego terminado
      - message=texto informativo
    """
    def __init__(self, game) -> None:
        self.game = game  # instancia de BackgammonGame

    def execute(self, cmd: Command) -> Tuple[bool, str]:
        if cmd.name == "help":
            return (False, self._help_text())
        if cmd.name == "quit":
            return (True, "Saliendo del juego.")

        if cmd.name == "roll":
            # delegamos al ciclo de turnos del juego
            try:
                self.game.start_turn()
            except Exception as ex:
                raise CommandExecError(str(ex)) from ex
            state = self.game.state()
            return (False, f"Turno de {state.current_color}. Dados: {state.dice_values} (movimientos: {state.moves_left})")

        if cmd.name == "move":
            # Validación ligera: el parser ya validó rango/forma; el juego valida reglas.
            try:
                self.game.apply_player_move(cmd.from_pos, cmd.steps)
            except InvalidMoveException as ex:
                # Propagamos con mensaje claro para el usuario
                raise CommandExecError(f"Movimiento inválido: {ex}") from ex
            except Exception as ex:
                raise CommandExecError(str(ex)) from ex

            # Estado post-movimiento (puede haber terminado)
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
            "  * Las reglas del juego (prioridad de BAR, bloqueos, bearing off, etc.)\n"
            "    son validadas por el motor del juego.\n"
        )
