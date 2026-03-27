import pytest
from types import SimpleNamespace

from core.board import Board
from core.player import Player
from core.game import BackgammonGame, GameRuleError


def _players():
    return Player("White", "white"), Player("Black", "black")


def test_highest_die_rule_enforced(monkeypatch):
    """
    Cuando quedan exactamente dos dados distintos y solo uno tiene jugada legal,
    debe obligar a usar el dado más alto. Si intento usar el otro -> GameRuleError.
    """
    b = Board()
    w, k = _players()
    # Dice "dummy": available_moves dos valores distintos
    dice = SimpleNamespace(available_moves=lambda: [2, 5], roll=lambda: None, use_move=lambda v: None)
    g = BackgammonGame(b, dice, (w, k), starting_color=w.color)
    g.start_turn()

    # Sin fichas en BAR
    monkeypatch.setattr(g, "_has_bar", lambda color=None: False)

    # Solo el 5 tiene movimiento legal
    monkeypatch.setattr(g, "_legal_single_move_exists", lambda color, steps: steps == 5)

    # Evitar acoplar a Board: no importa si ejecuta move_checker o move_or_bear_off
    monkeypatch.setattr(g.board, "move_checker", lambda *a, **k: None, raising=False)
    monkeypatch.setattr(g.board, "move_or_bear_off", lambda *a, **k: None, raising=False)

    # Intento usar el 2 (el no-legal) -> debe exigir el más alto (5)
    with pytest.raises(GameRuleError) as ei:
        g.apply_player_move(from_pos=13, steps=2)

    # Mensaje: no depende exactamente del texto, pero chequeamos que mencione dado requerido
    assert "Debés usar el dado" in str(ei.value)


def test_bar_priority_blocks_non_bar_moves(monkeypatch):
    """
    Si hay fichas en BAR, solo se puede jugar desde BAR (from_pos == 0).
    """
    b = Board()
    w, k = _players()
    dice = SimpleNamespace(available_moves=lambda: [1], roll=lambda: None, use_move=lambda v: None)
    g = BackgammonGame(b, dice, (w, k), starting_color=w.color)
    g.start_turn()

    # Fuerzo presencia en BAR
    monkeypatch.setattr(g, "_has_bar", lambda color=None: True)

    with pytest.raises(GameRuleError) as ei:
        g.apply_player_move(from_pos=6, steps=1)

    assert "BAR" in str(ei.value) or "bar" in str(ei.value).lower()


def test_state_returns_tuple_and_moves_count(monkeypatch):
    """
    Cubre 'state()' y la conversión de available_moves a tupla + conteo.
    """
    b = Board()
    w, k = _players()
    # available_moves como lista (no callable) para cubrir rama alternativa
    dice = SimpleNamespace(available_moves=[3, 3], roll=lambda: None)
    g = BackgammonGame(b, dice, (w, k), starting_color=w.color)

    st = g.state()
    assert isinstance(st.dice_values, tuple)
    assert st.dice_values == (3, 3)
    assert st.moves_left == 2


def test_end_turn_blocks_when_moves_still_legal(monkeypatch):
    """
    end_turn() debe bloquear si aún existen jugadas legales con los dados.
    (Cubre rama de chequeo de 'has_moves' + '_any_legal_move_exists_for_any_die')
    """
    b = Board()
    w, k = _players()
    dice = SimpleNamespace(available_moves=lambda: [4], roll=lambda: None)
    g = BackgammonGame(b, dice, (w, k), starting_color=w.color)
    g.start_turn()

    # Simulamos que todavía hay jugadas posibles
    # Si tu Dice no tiene has_moves, lo inyectamos en la instancia.
    monkeypatch.setattr(g.dice, "has_moves", lambda: True, raising=False)
    monkeypatch.setattr(g, "_any_legal_move_exists_for_any_die", lambda color: True)

    with pytest.raises(GameRuleError):
        g.end_turn()
