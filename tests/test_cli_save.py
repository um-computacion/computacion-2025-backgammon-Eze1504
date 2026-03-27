import json
import os
import tempfile
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

def test_save_writes_snapshot_json(tmp_path):
    game = make_game()
    runner = CommandRunner(game)
    out_file = tmp_path / "snapshot.json"
    # asumiendo formato: `save <ruta>` o guarda en una ruta por defecto si no se pasa
    _done, msg = runner.execute(parse_command(f"save {out_file.as_posix()}"))
    assert out_file.exists(), f"no se creó el snapshot: {msg}"
    data = json.loads(out_file.read_text())
    assert isinstance(data, dict) and data, "snapshot debe contener estado serializado"
