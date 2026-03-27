# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Tuple, Optional

from core.exceptions import (
    BackgammonException,
    InvalidMoveException,
    NoMovesAvailableException,
    DiceNotRolledException,
)
from cli.cli_exceptions import CommandExecError
from cli.command_parser import Command
from cli.board_view import render_game
from cli.hint_engine import suggest_move  # heurístico, no muta estado

import json
from dataclasses import asdict, is_dataclass


class CommandRunner:
    """
    Ejecuta comandos parseados contra una instancia de BackgammonGame.
    Devuelve (done, message): done=True para terminar la app.
    """

    def __init__(self, game):
        self.game = game

    # ------------------ API principal ------------------

    def execute(self, cmd: Command) -> Tuple[bool, str]:
        if cmd.name == "help":
            return (False, self._help_text())

        if cmd.name == "quit":
            return (True, "Saliendo del juego.")

        if cmd.name == "show":
            return (False, render_game(self.game))

        if cmd.name == "roll":
            return (False, self._do_roll())

        if cmd.name == "move":
            return (False, self._do_move(cmd.from_pos, cmd.steps))

        if cmd.name == "end":
            return (False, self._do_end())

        if cmd.name == "hint":
            return (False, self._do_hint())

        if cmd.name == "undo":
            return (False, self._do_undo())

        if cmd.name == "save":
            # El parser avanzado debería setear cmd.path; si no existe, elegimos uno por defecto
            path = getattr(cmd, "path", None) or "saved_game.json"
            return (False, self._do_save(path))

        # Comando desconocido (no debería llegar si el parser valida bien)
        raise CommandExecError(f"Comando no soportado: {cmd.name}")

    # ------------------ Operaciones concretas ------------------

    def _do_roll(self) -> str:
        try:
            self.game.start_turn()
        except BackgammonException as ex:
            raise CommandExecError(str(ex)) from ex

        st = self.game.state()
        view = render_game(self.game)
        return (
            f"Turno de {st.current_color}. Dados: {tuple(st.dice_values)} "
            f"(movimientos: {st.moves_left})\n\n{view}"
        )

    def _do_move(self, from_pos: int, steps: int) -> str:
        try:
            self.game.apply_player_move(from_pos, steps)
        except (InvalidMoveException, NoMovesAvailableException) as ex:
            raise CommandExecError(f"Movimiento inválido: {ex}") from ex
        except DiceNotRolledException as ex:
            raise CommandExecError(str(ex)) from ex
        except BackgammonException as ex:
            raise CommandExecError(str(ex)) from ex
        except Exception as ex:
        #  acá capturamos cosas como GameRuleError del motor,
        # y las convertimos en un error de ejecución entendible por la CLI
            raise CommandExecError(str(ex)) from ex

        st = self.game.state()
        view = render_game(self.game)
        msg = [
            f"OK: moviste desde {from_pos} {steps} paso(s).",
            f"Dados restantes: {tuple(st.dice_values)} (movimientos: {st.moves_left})",
    ]
        if getattr(self.game, "game_over", False):
            result = getattr(self.game, "result", None)
            if result is not None:
                winner = getattr(result, "winner_color", "desconocido")
                vtype = getattr(result, "victory_type", "single")
                msg.append(f"\n¡Partida terminada! Ganó {winner} ({vtype}).")
            else:
                msg.append("\n¡Partida terminada!")
        msg.append("\n" + view)
        return "\n".join(msg)


    def _do_end(self) -> str:
        try:
            self.game.end_turn()
        except NoMovesAvailableException as ex:
            # ejemplo: si aún hay jugadas posibles y no se puede cerrar
            raise CommandExecError(str(ex)) from ex
        except BackgammonException as ex:
            raise CommandExecError(str(ex)) from ex

        st = self.game.state()
        view = render_game(self.game)
        return (
            f"Turno finalizado. Ahora juega {st.current_color}. "
            f"Dados: {tuple(st.dice_values)} (movimientos: {st.moves_left})\n\n{view}"
        )

    def _do_hint(self) -> str:
        """
        Heurística no intrusiva: NO muta el estado del juego.
        """
        try:
            suggestion = suggest_move(self.game)
        except BackgammonException as ex:
            raise CommandExecError(str(ex)) from ex

        return f"Sugerencia: {suggestion}"

    def _do_undo(self) -> str:
        """
        Deshacer el último movimiento si el motor lo soporta.
        Si no existe, devolvemos un mensaje claro.
        """
        if not hasattr(self.game, "undo_last_move"):
            return "Deshacer no está disponible en este motor."

        try:
            self.game.undo_last_move()
        except BackgammonException as ex:
            raise CommandExecError(str(ex)) from ex

        st = self.game.state()
        view = render_game(self.game)
        return (
            f"Se deshizo el último movimiento. Dados: {tuple(st.dice_values)} "
            f"(movimientos: {st.moves_left})\n\n{view}"
        )

    def _do_save(self, path: str) -> str:
        """
        Guarda un snapshot mínimo del estado. Intenta serializar con sentido común
        sin acoplarse a detalles internos.
        """
        st = self.game.state()

        def _to_dict(obj):
            if is_dataclass(obj):
                return asdict(obj)
            if isinstance(obj, (list, tuple)):
                return list(obj)
            if hasattr(obj, "__dict__"):
                # SimpleNamespace u objetos simples
                return dict(vars(obj))
            return obj

        payload = {
            "state": _to_dict(st),
        }

        # Si el objeto result existe, guardamos un resumen para depuración
        result = getattr(self.game, "result", None)
        if result is not None:
            payload["result"] = _to_dict(result)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        return f"Partida guardada en: {path}"

    # ------------------ UI helpers ------------------

    def _help_text(self) -> str:
        return (
            "Comandos disponibles:\n"
            "  roll (r)                    -> tirar dados e iniciar turno\n"
            "  move <from> <steps>         -> mover una ficha (ej: 'move 13 5' o 'move bar 4')\n"
            "  end                         -> terminar el turno (si corresponde)\n"
            "  show / status               -> mostrar el tablero\n"
            "  hint                        -> sugerencia de jugada (heurística)\n"
            "  undo                        -> deshacer último movimiento (si el motor lo permite)\n"
            "  save [ruta]                 -> guardar snapshot del estado (si el parser provee path)\n"
            "  help (h, ?)                 -> esta ayuda\n"
            "  quit (q, exit)              -> salir\n"
        )

