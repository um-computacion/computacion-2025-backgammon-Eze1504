import pytest
from types import SimpleNamespace

from core.board import Board
from core.player import Player
from core.game import BackgammonGame, GameRuleError


def _players():
    return Player("White", "white"), Player("Black", "black")


def test_highest_die_rule_enforces_lower_when_only_lower_legal(monkeypatch):
    """
    Caso complementario: si quedan dos dados distintos y SOLO el menor tiene jugada,
    debe obligar a usar el menor. Intentar usar el mayor -> error.
    """
    b = Board()
    w, k = _players()
    dice = SimpleNamespace(available_moves=lambda: [2, 5], roll=lambda: None, use_move=lambda v: None)
    g = BackgammonGame(b, dice, (w, k), starting_color=w.color)
    g.start_turn()

    # Sin BAR y SOLO el 2 es legal
    monkeypatch.setattr(g, "_has_bar", lambda color=None: False)
    monkeypatch.setattr(g, "_legal_single_move_exists", lambda color, steps: steps == 2)

    # No importa si usa move_checker o move_or_bear_off
    monkeypatch.setattr(g.board, "move_checker", lambda *a, **k: None, raising=False)
    monkeypatch.setattr(g.board, "move_or_bear_off", lambda *a, **k: None, raising=False)

    with pytest.raises(GameRuleError) as ei:
        g.apply_player_move(from_pos=13, steps=5)  # intenta usar el MAYOR (no permitido)
    assert "Debés usar el dado" in str(ei.value)


def test_bar_reentry_happy_path_consumes_die(monkeypatch):
    """
    Con fichas en BAR y from_pos == 0, debe llamar reenter_checker y consumir el dado.
    """
    b = Board()
    w, k = _players()

    used = {"v": None}
    dice = SimpleNamespace(
        available_moves=lambda: [3],
        roll=lambda: None,
        use_move=lambda v: used.__setitem__("v", v),
    )
    g = BackgammonGame(b, dice, (w, k), starting_color=w.color)
    g.start_turn()

    monkeypatch.setattr(g, "_has_bar", lambda color=None: True)
    called = {"reenter": False}

    def reenter_checker(color, steps):
        called["reenter"] = True
        assert color == "white" and steps == 3

    monkeypatch.setattr(g.board, "reenter_checker", reenter_checker, raising=False)
    # Evitar rutas alternativas
    monkeypatch.setattr(g.board, "move_checker", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no debe llamarse")), raising=False)
    monkeypatch.setattr(g.board, "move_or_bear_off", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no debe llamarse")), raising=False)

    # Tras el movimiento, simulamos que NO ha terminado (para no depender de outcome)
    monkeypatch.setattr(g.board, "count_checkers", lambda color: {"off": 0}, raising=False)

    g.apply_player_move(from_pos=0, steps=3)
    assert called["reenter"] is True
    assert used["v"] == 3


def test_end_turn_allows_when_has_moves_but_no_legal_moves(monkeypatch):
    """
    Si dice.has_moves() es True pero NO hay jugadas legales, end_turn debe permitir y cambiar el turno.
    """
    b = Board()
    w, k = _players()
    dice = SimpleNamespace(available_moves=lambda: [4], roll=lambda: None)
    g = BackgammonGame(b, dice, (w, k), starting_color=w.color)
    g.start_turn()

    # Inyectamos has_moves True, pero ninguna jugada legal
    monkeypatch.setattr(g.dice, "has_moves", lambda: True, raising=False)
    monkeypatch.setattr(g, "_any_legal_move_exists_for_any_die", lambda color: False)

    current = g.current_color
    g.end_turn()
    assert g.current_color != current


def test_finalize_uses_count_at25_fallback(monkeypatch):
    b = Board()
    w, k = _players()
    dice = SimpleNamespace(available_moves=lambda: [1], roll=lambda: None, use_move=lambda v: None)
    g = BackgammonGame(b, dice, (w, k), starting_color=w.color)
    g.start_turn()

    # Sin BAR, movimiento no-op
    monkeypatch.setattr(g, "_has_bar", lambda color=None: False)
    monkeypatch.setattr(g.board, "move_checker", lambda *a, **k: None, raising=False)
    monkeypatch.setattr(g.board, "move_or_bear_off", lambda *a, **k: None, raising=False)

    # Reportamos 15 off por cualquier fuente que el core consulte:
    monkeypatch.setattr(g.board, "count_at",
                        lambda pos, color: 15 if (pos == 25 and color == "white") else 0,
                        raising=False)
    monkeypatch.setattr(g.board, "count_off", lambda color: 15 if color == "white" else 0, raising=False)
    monkeypatch.setattr(g.board, "count_checkers", lambda color: {"off": 15 if color == "white" else 0}, raising=False)
    monkeypatch.setattr(g.board, "get_checkers_in_bar", lambda color=None: [], raising=False)

    # Evitamos depender de la lógica exacta del outcome
    monkeypatch.setattr(g, "_determine_outcome", lambda wc, lc: ("single", 1))

    g.apply_player_move(from_pos=6, steps=1)
    assert g.game_over is True
    assert g.result.winner_color == "white"
    assert g.result.outcome == "single"
    assert g.result.points == 1
