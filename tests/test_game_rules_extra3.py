import pytest
from types import SimpleNamespace

from core.board import Board
from core.player import Player
from core.game import BackgammonGame, GameRuleError


def _players():
    return Player("White", "white"), Player("Black", "black")


def test_start_turn_roll_called_and_no_roll_path(monkeypatch):
    # Caso A: el dice TIENE roll() y se llama
    b = Board(); w, k = _players()
    called = {"roll": False}
    diceA = SimpleNamespace(
        roll=lambda: called.__setitem__("roll", True),
        available_moves=lambda: [3, 4],
    )
    gA = BackgammonGame(b, diceA, (w, k), starting_color=w.color)
    gA.start_turn()
    assert called["roll"] is True  # cubre senda "tiene roll()"

    # Caso B: el dice NO TIENE roll() -> no revienta y el turno queda activo igual
    b2 = Board(); w2, k2 = _players()
    diceB = SimpleNamespace(available_moves=lambda: [2, 5])  # sin roll
    gB = BackgammonGame(b2, diceB, (w2, k2), starting_color=w2.color)
    st = gB.start_turn()
    assert st.current_color == "white"  # turno arrancó sin necesidad de roll()


def test_can_player_move_true_and_false(monkeypatch):
    b = Board(); w, k = _players()
    dice = SimpleNamespace(available_moves=lambda: [], roll=lambda: None)
    g = BackgammonGame(b, dice, (w, k), starting_color=w.color)

    # True
    monkeypatch.setattr(g.dice, "has_moves", lambda: True, raising=False)
    assert g.can_player_move() is True

    # False
    monkeypatch.setattr(g.dice, "has_moves", lambda: False, raising=False)
    assert g.can_player_move() is False


def test_apply_uses_move_checker_when_no_move_or_bear_off(monkeypatch):
    b = Board(); w, k = _players()
    used = {"die": None}
    dice = SimpleNamespace(
        available_moves=lambda: [4],
        roll=lambda: None,
        use_move=lambda v: used.__setitem__("die", v),
    )
    g = BackgammonGame(b, dice, (w, k), starting_color=w.color)
    g.start_turn()

    # Sin BAR, y como Board no tiene move_or_bear_off, debe caer en move_checker
    monkeypatch.setattr(g, "_has_bar", lambda color=None: False)

    called = {"mc": False}
    def _mc(color, from_pos, steps):
        called["mc"] = True
        assert color == "white" and from_pos == 13 and steps == 4
    monkeypatch.setattr(g.board, "move_checker", _mc, raising=False)

    # Evitar finalización accidental
    monkeypatch.setattr(g.board, "count_checkers", lambda color: {"off": 0}, raising=False)

    g.apply_player_move(from_pos=13, steps=4)
    assert called["mc"] is True
    assert used["die"] == 4

    def _mc(color, from_pos, steps):
        called["mc"] = True
        assert color == "white" and from_pos == 13 and steps == 4
    monkeypatch.setattr(g.board, "move_checker", _mc, raising=False)

    # Evitar finalización accidental
    monkeypatch.setattr(g.board, "count_checkers", lambda color: {"off": 0}, raising=False)

    g.apply_player_move(from_pos=13, steps=4)
    assert called["mc"] is True
    assert used["die"] == 4


def test_finalize_game_idempotent(monkeypatch):
    """
    Llamar _finalize_game dos veces no debe romper ni cambiar el resultado.
    """
    b = Board(); w, k = _players()
    dice = SimpleNamespace(available_moves=lambda: [1], roll=lambda: None, use_move=lambda v: None)
    g = BackgammonGame(b, dice, (w, k), starting_color=w.color)

    # Forzamos outcome estable
    monkeypatch.setattr(g, "_determine_outcome", lambda wc, lc: ("single", 1))
    g._finalize_game("white")
    first = g.result

    # Segunda llamada no debe alterar nada
    g._finalize_game("white")
    second = g.result

    assert g.game_over is True
    assert first is second
    assert g.result.winner_color == "white"
    assert g.result.outcome == "single"
    assert g.result.points == 1


def test_end_turn_flips_turn_when_no_legal_moves(monkeypatch):
    """
    end_turn permite cerrar si no hay jugadas legales aunque existan dados (has_moves True).
    """
    b = Board(); w, k = _players()
    dice = SimpleNamespace(available_moves=lambda: [6], roll=lambda: None)
    g = BackgammonGame(b, dice, (w, k), starting_color=w.color)
    g.start_turn()

    # has_moves True pero NO hay jugadas legales -> end_turn debe permitir
    monkeypatch.setattr(g.dice, "has_moves", lambda: True, raising=False)
    monkeypatch.setattr(g, "_any_legal_move_exists_for_any_die", lambda color: False)

    before = g.current_color
    g.end_turn()
    assert g.current_color != before


def test_check_victory_after_move_direct_call_if_present(monkeypatch):
    """
    Si el helper privado existe, lo cubrimos directamente con 15 off.
    Si no existe en tu implementación, el test no falla (se omite).
    """
    b = Board(); w, k = _players()
    dice = SimpleNamespace(available_moves=lambda: [], roll=lambda: None, use_move=lambda v: None)
    g = BackgammonGame(b, dice, (w, k), starting_color=w.color)

    if hasattr(g, "_check_victory_after_move"):
        # 15 off por cualquier via
        monkeypatch.setattr(g.board, "count_checkers", lambda color: {"off": 15}, raising=False)
        monkeypatch.setattr(g.board, "count_off", lambda color: 15, raising=False)
        monkeypatch.setattr(g.board, "count_at", lambda pos, color: 15 if pos == 25 else 0, raising=False)
        monkeypatch.setattr(g, "_determine_outcome", lambda wc, lc: ("gammon", 2))
        g._check_victory_after_move("white")
        assert g.game_over is True
        assert g.result.winner_color == "white"
        assert g.result.outcome == "gammon"
        assert g.result.points == 2
    else:
        pytest.skip("BackgammonGame no define _check_victory_after_move; se omite.")
