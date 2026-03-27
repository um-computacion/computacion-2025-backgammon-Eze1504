import pytest
from types import SimpleNamespace

from core.game import BackgammonGame, GameRuleError
from core.board import Board
from core.dice import Dice
from core.player import Player
from core.exceptions import InvalidPlayerNameException, InvalidMoveException


def make_game():
    board = Board()
    dice = Dice()
    white = Player("White", "white")
    black = Player("Black", "black")
    return BackgammonGame(board, dice, (white, black), starting_color="white")


def test_cannot_start_turn_twice():
    g = make_game()
    g.start_turn()
    with pytest.raises(GameRuleError):
        g.start_turn()


def test_cannot_move_without_turn():
    g = make_game()
    with pytest.raises(GameRuleError):
        g.apply_player_move(1, 2)


def test_cannot_use_unavailable_die():
    g = make_game()
    g.start_turn()
    # Reemplazamos el dado real por un dummy que expone la interfaz mínima requerida:
    # _get_available_moves acepta atributo 'available_moves' como lista o como callable.
    g.dice = SimpleNamespace(
        available_moves=[1],      # sólo está disponible el 1
        has_moves=lambda: True,   # simula que aún hay movimientos
        use_move=lambda v: None,  # no hace nada
    )
    with pytest.raises(GameRuleError):
        g.apply_player_move(1, 3)  # intenta usar 3 (no disponible) => debe fallar


def test_determine_outcome_single(monkeypatch):
    g = make_game()
    # El perdedor tiene al menos una ficha off
    g.board.count_checkers = lambda color: {"off": 2}
    assert g._determine_outcome("white", "black") == ("single", 1)


def test_determine_outcome_gammon(monkeypatch):
    g = make_game()
    g.board.count_checkers = lambda c: {"off": 0}
    g.board.get_checkers_in_bar = lambda c: []
    g.board.get_home_board_range = lambda c: (1, 6)
    g.board.get_point = lambda p: []
    assert g._determine_outcome("white", "black") == ("gammon", 2)


def test_determine_outcome_backgammon(monkeypatch):
    g = make_game()
    g.board.count_checkers = lambda c: {"off": 0}
    g.board.get_checkers_in_bar = lambda c: [1]
    g.board.get_home_board_range = lambda c: (1, 6)
    g.board.get_point = lambda p: []
    assert g._determine_outcome("white", "black") == ("backgammon", 3)


def test_invalid_player_name_message():
    err = InvalidPlayerNameException("")
    assert "inválido" in str(err)


def test_invalid_move_with_position():
    err = InvalidMoveException("Fuera de rango", 30)
    assert "posición" in str(err)

def make_game():
    board = Board()
    dice = Dice()
    white = Player("White", "white")
    black = Player("Black", "black")
    return BackgammonGame(board, dice, (white, black), starting_color="white")


def test_state_moves_left_reflects_available(monkeypatch):
    g = make_game()
    # Simulamos dados disponibles 1,1,3
    monkeypatch.setattr(g, "_get_available_moves", lambda: [1, 1, 3])
    st = g.state()
    assert st.current_color == "white"
    assert st.dice_values == (1, 1, 3)
    assert st.moves_left == 3


def test_bar_priority_forces_from_bar(monkeypatch):
    g = make_game()
    g.start_turn()

    # Hay fichas en BAR -> mover desde punto 5 debe fallar
    monkeypatch.setattr(g, "_has_bar", lambda c=None: True)
    # Simulamos que el dado 2 está disponible
    monkeypatch.setattr(g, "_get_available_moves", lambda: [2])

    with pytest.raises(GameRuleError):
        g.apply_player_move(from_pos=5, steps=2)


def test_high_die_rule_enforced_when_only_one_is_legal(monkeypatch):
    g = make_game()
    g.start_turn()

    # Dos dados distintos y solo uno jugable: debe usar el más alto
    monkeypatch.setattr(g, "_has_bar", lambda c=None: False)
    monkeypatch.setattr(g, "_get_available_moves", lambda: [2, 5])

    # Solo el 5 es legal
    monkeypatch.setattr(g, "_legal_single_move_exists", lambda color, steps: (steps == 5))

    # board.move_checker llamado cuando se usa el dado correcto
    called = {"ok": False}
    def fake_move_checker(color, from_pos, steps):
        called["ok"] = True
    monkeypatch.setattr(g.board, "move_checker", fake_move_checker)

    # Intentar con 2 -> debe fallar por la regla del dado más alto
    with pytest.raises(GameRuleError):
        g.apply_player_move(from_pos=12, steps=2)

    # Con 5 -> debe pasar y llamar al board
    # _get_available_moves vuelve a evaluar → mantenemos mismo monkeypatch
    # Simulamos consumo de dado (no usamos el real) para no interferir
    monkeypatch.setattr(g.dice, "use_move", lambda v: None)
    g.apply_player_move(from_pos=12, steps=5)
    assert called["ok"] is True


def test_end_turn_blocks_when_moves_available(monkeypatch):
    g = make_game()
    g.start_turn()

    # Hay dados y hay al menos una jugada -> no se puede terminar
    monkeypatch.setattr(g.dice, "has_moves", lambda: True, raising=False)
    monkeypatch.setattr(g, "_any_legal_move_exists_for_any_die", lambda color: True)

    with pytest.raises(GameRuleError):
        g.end_turn()


def test_end_turn_allows_when_no_moves_left(monkeypatch):
    g = make_game()
    g.start_turn()

    # No quedan jugadas posibles -> se puede terminar y cambia el turno
    monkeypatch.setattr(g.dice, "has_moves", lambda: False, raising=False)
    monkeypatch.setattr(g, "_any_legal_move_exists_for_any_die", lambda color: False)

    current = g.current_color
    g.end_turn()
    assert g.current_color != current



def test_move_happy_path_without_bar(monkeypatch):
    g = make_game()
    g.start_turn()

    # Sin BAR, dado 3 disponible, mover desde 13 con 3
    monkeypatch.setattr(g, "_has_bar", lambda c=None: False)
    monkeypatch.setattr(g, "_get_available_moves", lambda: [3])

    moved = {"ok": False}
    def fake_move_checker(color, from_pos, steps):
        assert color == g.current_color
        assert from_pos == 13 and steps == 3
        moved["ok"] = True

    monkeypatch.setattr(g.board, "move_checker", fake_move_checker)
    monkeypatch.setattr(g.dice, "use_move", lambda v: None)

    g.apply_player_move(from_pos=13, steps=3)
    assert moved["ok"] is True