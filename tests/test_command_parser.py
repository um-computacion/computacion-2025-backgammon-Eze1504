# -*- coding: utf-8 -*-
import pytest
from cli.command_parser import parse_command, Command
from core.exceptions import CommandParseError

def test_parse_help_and_quit_and_roll():
    assert parse_command("help").name == "help"
    assert parse_command("h").name == "help"
    assert parse_command("?").name == "help"

    assert parse_command("quit").name == "quit"
    assert parse_command("q").name == "quit"
    assert parse_command("exit").name == "quit"

    assert parse_command("roll").name == "roll"
    assert parse_command("r").name == "roll"

def test_parse_move_ok_numeric():
    c = parse_command("move 13 5")
    assert c.name == "move" and c.from_pos == 13 and c.steps == 5

def test_parse_move_ok_bar_off_alias():
    c = parse_command("move bar 4")
    assert c.name == "move" and c.from_pos == 0 and c.steps == 4
    # off existe, por compatibilidad, aunque no suele usarse como origen
    c2 = parse_command("move off 1")
    assert c2.name == "move" and c2.from_pos == 25 and c2.steps == 1

@pytest.mark.parametrize("line", ["", "   ", None])
def test_parse_empty(line):
    with pytest.raises(CommandParseError):
        parse_command(line)

@pytest.mark.parametrize("line", ["unknown", "xyz 1 2", "move 3", "move 3 0", "move 3 7", "move -1 3"])
def test_parse_errors(line):
    with pytest.raises(CommandParseError):
        parse_command(line)
