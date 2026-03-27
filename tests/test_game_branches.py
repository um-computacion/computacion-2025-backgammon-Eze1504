import pytest
from types import SimpleNamespace

from core.game import BackgammonGame, GameRuleError
from core.board import Board
from core.player import Player
from core.dice import Dice


def _make_players():
    return Player("White", "white"), Player("Black", "black")


# -------------------- _get_available_moves: callable vs lista --------------------

def test_get_available_moves_works_with_callable(monkeypatch):
    b = Board()
    w, k = _make_players()
    # Dice dummy con available_moves como callable
    dice = SimpleNamespace(available_moves=lambda: [4, 1], roll=lambda: None)
    g = BackgammonGame(b, dice, (w, k), starting_color=w.color)

    st = g.state()
    assert st.dice_values == (4, 1) and st.moves_left == 2


def test_get_available_moves_works_with_list(monkeypatch):
    b = Board()
    w, k = _make_players()
    # Dice dummy con available_moves como lista (no callable)
    dice = SimpleNamespace(available_moves=[3, 3], roll=lambda: None)
    g = BackgammonGame(b, dice, (w, k), starting_color=w.color)

    st = g.state()
    assert st.dice_values == (3, 3) and st.moves_left == 2


# -------------------- start_turn con y sin .roll() --------------------

def test_start_turn_when_dice_has_roll(monkeypatch):
    b = Board()
    w, k = _make_players()
    d = Dice()
    g = BackgammonGame(b, d, (w, k), starting_color=w.color)

    st = g.start_turn()
    # No verificamos valores exactos del dado (aleatorio), solo que activó turno y hay moves list/tuple
    assert g._turn_active is True
    assert isinstance(st.dice_values, tuple)


def test_start_turn_when_dice_has_no_roll(monkeypatch):
    b = Board()
    w, k = _make_players()
    # dado sin método roll
    dice = SimpleNamespace(available_moves=lambda: [2, 5])
    g = BackgammonGame(b, dice, (w, k), starting_color=w.color)

    st = g.start_turn()
    assert st.dice_values == (2, 5)
    assert g._turn_active is True


# -------------------- apply_player_move: move_or_bear_off vs move_checker --------------------

def test_apply_move_uses_move_or_bear_off_if_present(monkeypatch):
    b = Board()
    w, k = _make_players()
    # dado fijo
    dice = SimpleNamespace(available_moves=lambda: [4], use_move=lambda v: None, roll=lambda: None)
    g = BackgammonGame(b, dice, (w, k), starting_color=w.color)
    g.start_turn()

    # Sin BAR
    monkeypatch.setattr(g, "_has_bar", lambda c=None: False)

    called = {"mob": False}

    def mob(color, from_pos, steps):
        called["mob"] = True
        assert color == "white" and from_pos == 13 and steps == 4

    # Board con move_or_bear_off
    monkeypatch.setattr(g.board, "move_or_bear_off", mob, raising=False)

    g.apply_player_move(from_pos=13, steps=4)
    assert called["mob"] is True


def test_apply_move_falls_back_to_move_checker_when_no_move_or_bear_off(monkeypatch):
    b = Board()
    w, k = _make_players()
    dice = SimpleNamespace(available_moves=lambda: [2], use_move=lambda v: None, roll=lambda: None)
    g = BackgammonGame(b, dice, (w, k), starting_color=w.color)
    g.start_turn()

    monkeypatch.setattr(g, "_has_bar", lambda c=None: False)

    called = {"mc": False}

    def mc(color, from_pos, steps):
        called["mc"] = True
        assert color == "white" and from_pos == 6 and steps == 2

    monkeypatch.setattr(g.board, "move_checker", mc, raising=False)

    g.apply_player_move(from_pos=6, steps=2)
    assert called["mc"] is True


# -------------------- _any_legal_move_exists_for_any_die desduplica y consulta helpers --------------------

def test_any_legal_move_exists_for_any_die(monkeypatch):
    b = Board()
    w, k = _make_players()
    d = Dice()
    g = BackgammonGame(b, d, (w, k), starting_color=w.color)

    # Devuelve duplicados para chequear que usa set()
    monkeypatch.setattr(g, "_get_available_moves", lambda: [1, 2, 2])

    # Solo 2 es legal
    monkeypatch.setattr(g, "_legal_single_move_exists", lambda color, steps: steps == 2)

    assert g._any_legal_move_exists_for_any_die("white") is True


# -------------------- _legal_single_move_exists: BAR, basic move y bear-off --------------------

def test_legal_single_move_exists_with_bar_valid_reentry(monkeypatch):
    b = Board()
    w, k = _make_players()
    d = Dice()
    g = BackgammonGame(b, d, (w, k), starting_color=w.color)

    # Hay fichas en BAR → usa validate_reentry
    monkeypatch.setattr(g, "_has_bar", lambda color=None: True)
    monkeypatch.setattr(g.board, "validate_reentry", lambda color, steps: True, raising=False)

    assert g._legal_single_move_exists("white", 3) is True


def test_legal_single_move_exists_basic_move_on_board(monkeypatch):
    b = Board()
    w, k = _make_players()
    d = Dice()
    g = BackgammonGame(b, d, (w, k), starting_color=w.color)

    monkeypatch.setattr(g, "_has_bar", lambda color=None: False)

    # Solo el punto 8 tiene ficha blanca
    def _has_checker_of_color(pos, color):
        return color == "white" and pos == 8

    def validate_basic_move(color, pos, steps):
        assert color == "white" and pos == 8 and steps == 5
        return True

    monkeypatch.setattr(g.board, "_has_checker_of_color", _has_checker_of_color, raising=False)
    monkeypatch.setattr(g.board, "validate_basic_move", validate_basic_move, raising=False)
    # asegurar que can_bear_off_from no se usa en este escenario
    monkeypatch.setattr(g.board, "can_bear_off_from", lambda *a, **k: False, raising=False)

    assert g._legal_single_move_exists("white", 5) is True


def test_legal_single_move_exists_bear_off_path(monkeypatch):
    b = Board()
    w, k = _make_players()
    d = Dice()
    g = BackgammonGame(b, d, (w, k), starting_color=w.color)

    monkeypatch.setattr(g, "_has_bar", lambda color=None: False)

    # No hay basic move válido, pero se puede bear-off desde pos 1
    def _has_checker_of_color(pos, color):
        return color == "white" and pos == 1

    def validate_basic_move(*a, **k):
        raise Exception("no basic move")

    monkeypatch.setattr(g.board, "_has_checker_of_color", _has_checker_of_color, raising=False)
    monkeypatch.setattr(g.board, "validate_basic_move", validate_basic_move, raising=False)
    monkeypatch.setattr(g.board, "can_bear_off_from", lambda color, pos, steps: (color == "white" and pos == 1 and steps == 1), raising=False)

    assert g._legal_single_move_exists("white", 1) is True


# -------------------- _maybe_finalize_if_won y _finalize_game --------------------

def test_maybe_finalize_if_won_uses_count_off(monkeypatch):
    # Finalización vía API pública tras una jugada, simulando 15 off.
    b = Board()
    w, k = _make_players()
    d = Dice()
    g = BackgammonGame(b, d, (w, k), starting_color=w.color)
    g.start_turn()

    # Sin BAR y dado 1 disponible
    monkeypatch.setattr(g, "_has_bar", lambda color=None: False)
    monkeypatch.setattr(g, "_get_available_moves", lambda: [1])
    monkeypatch.setattr(g.dice, "use_move", lambda v: None, raising=False)

    # El movimiento en sí no importa (no-op). Forzamos camino sin move_or_bear_off.
    monkeypatch.setattr(g.board, "move_checker", lambda *a, **k: None, raising=False)
    # Por si tu Board tiene move_or_bear_off y lo usa preferentemente:
    monkeypatch.setattr(g.board, "move_or_bear_off", lambda *a, **k: None, raising=False)

    # Tras el movimiento, cualquier consulta de victoria debe ver 15 off:
    monkeypatch.setattr(g.board, "count_checkers", lambda color: {"off": 15}, raising=False)
    monkeypatch.setattr(g.board, "count_off", lambda color: 15, raising=False)
    monkeypatch.setattr(g.board, "count_at", lambda pos, color: 15 if pos == 25 else 0, raising=False)
    # Y que no haya fichas en BAR
    monkeypatch.setattr(g.board, "get_checkers_in_bar", lambda color=None: [], raising=False)

    g.apply_player_move(from_pos=6, steps=1)

    assert g.game_over is True
    assert g.result is not None
    assert g.result.winner_color == "white"



def test_finalize_game_sets_result_and_is_idempotent(monkeypatch):
    b = Board()
    w, k = _make_players()
    d = Dice()
    g = BackgammonGame(b, d, (w, k), starting_color=w.color)

    # Forzar outcome para no depender de Board
    monkeypatch.setattr(g, "_determine_outcome", lambda wc, lc: ("gammon", 2))
    g._finalize_game("white")

    assert g.game_over is True
    assert g.result.winner_color == "white"
    assert g.result.loser_color == "black"
    assert g.result.outcome == "gammon"
    assert g.result.points == 2

    # Llamada repetida no debe romper ni cambiar nada
    g._finalize_game("white")
    assert g.game_over is True
    assert g.result.outcome == "gammon"
