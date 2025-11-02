# --- Cobertura dirigida para core/game.py ---
import pytest
from types import SimpleNamespace
from core.game import BackgammonGame, GameRuleError
from core.board import Board
from core.player import Player

# Helpers
def _players():
    return Player("W", "white"), Player("K", "black")

def _game_with(dice):
    b = Board()
    w, k = _players()
    return BackgammonGame(b, dice, (w, k), starting_color=w.color)

# --- (L65, L68): _other_color, current_player, opponent_player ---
def test_other_color_and_current_opponent_player():
    dice = SimpleNamespace(roll=lambda: None, available_moves=lambda: [], use_move=lambda v: None, has_moves=lambda: False)
    g = _game_with(dice)
    # _other_color + current/opponent
    assert g._other_color("white") == "black"
    assert g._other_color("black") == "white"
    assert g.current_player().color == "white"
    assert g.opponent_player().color == "black"

# --- (L134): can_player_move True/False en base a dice.has_moves() ---
def test_can_player_move_true_false(monkeypatch):
    dice = SimpleNamespace(roll=lambda: None, available_moves=lambda: [], use_move=lambda v: None, has_moves=lambda: True)
    g = _game_with(dice)
    assert g.can_player_move() is True
    monkeypatch.setattr(g.dice, "has_moves", lambda: False, raising=False)
    assert g.can_player_move() is False

# --- (L150-151): apply: dado no disponible y prioridad BAR ---
def test_apply_rejects_unavailable_die_and_bar_priority(monkeypatch):
    # available=[3]; intento usar 5 → error
    used = {"die": None}
    dice = SimpleNamespace(
        roll=lambda: None,
        available_moves=lambda: [3],
        use_move=lambda v: used.__setitem__("die", v),
        has_moves=lambda: True,
    )
    g = _game_with(dice)
    g.start_turn()
    with pytest.raises(GameRuleError):
        g.apply_player_move(from_pos=6, steps=5)

    # Hay fichas en BAR y se intenta mover desde otro punto → error
    monkeypatch.setattr(g, "_has_bar", lambda color=None: True)
    with pytest.raises(GameRuleError):
        g.apply_player_move(from_pos=6, steps=3)

# --- (L249-251): victoria inmediata por left == 0 tras consumir dado ---
def test_finalize_when_left_zero(monkeypatch):
    dice = SimpleNamespace(
        roll=lambda: None,
        available_moves=lambda: [2],
        use_move=lambda v: None,
        has_moves=lambda: True,
    )
    g = _game_with(dice)
    g.start_turn()
    # Forzar que no haya fichas restantes en tablero+bar tras el movimiento
    monkeypatch.setattr(g, "_has_bar", lambda color=None: False)
    monkeypatch.setattr(g.board, "move_checker", lambda *a, **k: None, raising=False)
    monkeypatch.setattr(g, "_remaining_on_board_or_bar", lambda color: 0)
    # Outcome controlado para no depender de _determine_outcome
    monkeypatch.setattr(g, "_determine_outcome", lambda wc, lc: ("single", 1))
    g.apply_player_move(from_pos=6, steps=2)
    assert g.game_over is True
    assert g.result.outcome == "single"
    assert g.result.points == 1

# --- (L291-292, 296-299): regla del dado alto cuando solo uno es jugable ---
def test_high_die_rule_forces_only_playable(monkeypatch):
    # available=[2,5], pero solo 5 es jugable → intentar 2 debe explotar
    used = {"die": None}
    dice = SimpleNamespace(
        roll=lambda: None,
        available_moves=lambda: [2, 5],
        use_move=lambda v: used.__setitem__("die", v),
        has_moves=lambda: True,
    )
    g = _game_with(dice)
    g.start_turn()
    monkeypatch.setattr(g, "_has_bar", lambda color=None: False)

    # Solo 5 es jugable
    def _legal(color, steps): return steps == 5
    monkeypatch.setattr(g, "_legal_single_move_exists", _legal)

    with pytest.raises(GameRuleError):
        g.apply_player_move(from_pos=8, steps=2)

    # Con 5 funciona
    monkeypatch.setattr(g.board, "move_checker", lambda *a, **k: None, raising=False)
    monkeypatch.setattr(g.board, "count_off", lambda color: 0, raising=False)
    g.apply_player_move(from_pos=8, steps=5)
    assert used["die"] == 5

# --- (L303-306): camino con BAR (reenter_checker) ---
def test_apply_from_bar_calls_reenter_checker(monkeypatch):
    called = {"reenter": 0, "used": None}
    dice = SimpleNamespace(
        roll=lambda: None,
        available_moves=lambda: [6],
        use_move=lambda v: called.__setitem__("used", v),
        has_moves=lambda: True,
    )
    g = _game_with(dice)
    g.start_turn()
    monkeypatch.setattr(g, "_has_bar", lambda color=None: True)
    monkeypatch.setattr(g.board, "reenter_checker", lambda *a, **k: called.__setitem__("reenter", called["reenter"]+1), raising=False)
    monkeypatch.setattr(g.board, "count_off", lambda color: 0, raising=False)

    g.apply_player_move(from_pos=0, steps=6)
    assert called["reenter"] == 1
    assert called["used"] == 6

# --- (L310-326): camino sin BAR con move_or_bear_off si existe; y fallback a move_checker ---
def test_apply_prefers_move_or_bear_off_else_falls_to_move_checker(monkeypatch):
    used = {"mb": 0, "mc": 0}

    dice = SimpleNamespace(
        roll=lambda: None,
        available_moves=lambda: [3, 4],
        use_move=lambda v: None,
        has_moves=lambda: True,
    )
    g = _game_with(dice)
    g.start_turn()
    monkeypatch.setattr(g, "_has_bar", lambda color=None: False)

    # 1) Con move_or_bear_off presente
    monkeypatch.setattr(g.board, "move_or_bear_off", lambda *a, **k: used.__setitem__("mb", used["mb"]+1), raising=False)
    monkeypatch.setattr(g.board, "count_off", lambda color: 0, raising=False)

    g.apply_player_move(from_pos=6, steps=3)
    assert used["mb"] == 1

    # 2) Sin move_or_bear_off -> fallback a move_checker
    if hasattr(g.board, "move_or_bear_off"):
        delattr(g.board, "move_or_bear_off")
    monkeypatch.setattr(g.board, "move_checker", lambda *a, **k: used.__setitem__("mc", used["mc"]+1), raising=False)
    g.apply_player_move(from_pos=6, steps=4)
    assert used["mc"] == 1

# --- (L348-401): _check_victory_after_move con 4 estrategias de 'off' ---

# 1) count_off(color) disponible
def test_check_victory_after_move_by_count_off(monkeypatch):
    dice = SimpleNamespace(available_moves=lambda: [], roll=lambda: None, use_move=lambda v: None, has_moves=lambda: False)
    g = _game_with(dice)
    # count_off retorna 15
    monkeypatch.setattr(g.board, "count_off", lambda color: 15, raising=False)
    # evitar otras rutas
    monkeypatch.setattr(g.board, "count_at", lambda pos, col: 0, raising=False)
    monkeypatch.setattr(g.board, "count_checkers", lambda c: {"off": 0}, raising=False)
    monkeypatch.setattr(g.board, "get_point", lambda p: [], raising=False)
    monkeypatch.setattr(g.board, "get_checkers_in_bar", lambda c=None: [], raising=False)
    monkeypatch.setattr(g, "_determine_outcome", lambda wc, lc: ("single", 1))
    g._check_victory_after_move("white")
    assert g.game_over is True and g.result.points == 1

# 2) count_at(OFF, color) como fallback
def test_check_victory_after_move_by_count_at_fallback(monkeypatch):
    dice = SimpleNamespace(available_moves=lambda: [], roll=lambda: None, use_move=lambda v: None, has_moves=lambda: False)
    g = _game_with(dice)
    # count_off falla -> None
    monkeypatch.setattr(g.board, "count_off", lambda color: (_ for _ in ()).throw(Exception("x")), raising=False)
    # count_at(25, color) = 15
    monkeypatch.setattr(g.board, "count_at", lambda pos, color: 15 if (pos == g.OFF and color == "white") else 0, raising=False)
    monkeypatch.setattr(g, "_determine_outcome", lambda wc, lc: ("single", 1))
    g._check_victory_after_move("white")
    assert g.game_over is True

# 3) count_checkers(color)['off'] como fallback
def test_check_victory_after_move_by_count_checkers_dict(monkeypatch):
    dice = SimpleNamespace(available_moves=lambda: [], roll=lambda: None, use_move=lambda v: None, has_moves=lambda: False)
    g = _game_with(dice)
    monkeypatch.setattr(g.board, "count_off", lambda color: (_ for _ in ()).throw(Exception("x")), raising=False)
    monkeypatch.setattr(g.board, "count_at", lambda pos, color: (_ for _ in ()).throw(Exception("y")), raising=False)
    monkeypatch.setattr(g.board, "count_checkers", lambda c: {"off": 15}, raising=False)
    monkeypatch.setattr(g, "_determine_outcome", lambda wc, lc: ("single", 1))
    g._check_victory_after_move("white")
    assert g.game_over is True

# 4) Deducción (15 - (on_board + in_bar))
def test_check_victory_after_move_by_deduction(monkeypatch):
    dice = SimpleNamespace(available_moves=lambda: [], roll=lambda: None, use_move=lambda v: None, has_moves=lambda: False)
    g = _game_with(dice)

    # rompo count_off / count_at / count_checkers para forzar deducción
    monkeypatch.setattr(g.board, "count_off", lambda color: (_ for _ in ()).throw(Exception("x")), raising=False)
    monkeypatch.setattr(g.board, "count_at", lambda pos, color: (_ for _ in ()).throw(Exception("y")), raising=False)
    monkeypatch.setattr(g.board, "count_checkers", lambda c: (_ for _ in ()).throw(Exception("z")), raising=False)

    # on_board = 0, in_bar = 0 -> off = 15
    monkeypatch.setattr(g.board, "get_point", lambda p: [], raising=False)
    monkeypatch.setattr(g.board, "get_checkers_in_bar", lambda c=None: [], raising=False)

    monkeypatch.setattr(g, "_determine_outcome", lambda wc, lc: ("gammon", 2))
    g._check_victory_after_move("white")
    assert g.game_over is True and g.result.points == 2

# --- (L419-422, 425-426, 432-438): _get_off_count con sus 4 rutas ---

def test_get_off_count_by_count_off():
    dice = SimpleNamespace(available_moves=lambda: [], roll=lambda: None, use_move=lambda v: None, has_moves=lambda: False)
    g = _game_with(dice)
    # count_off directo
    setattr(g.board, "count_off", lambda color: 7)
    assert g._get_off_count("white") == 7

def test_get_off_count_by_count_at_fallback():
    dice = SimpleNamespace(available_moves=lambda: [], roll=lambda: None, use_move=lambda v: None, has_moves=lambda: False)
    g = _game_with(dice)
    setattr(g.board, "count_off", lambda color: (_ for _ in ()).throw(Exception("x")))
    setattr(g.board, "count_at", lambda pos, color: 9 if (pos == g.OFF and color == "white") else 0)
    assert g._get_off_count("white") == 9

def test_get_off_count_by_count_checkers_dict():
    dice = SimpleNamespace(available_moves=lambda: [], roll=lambda: None, use_move=lambda v: None, has_moves=lambda: False)
    g = _game_with(dice)
    setattr(g.board, "count_off", lambda color: (_ for _ in ()).throw(Exception("x")))
    setattr(g.board, "count_at", lambda pos, color: (_ for _ in ()).throw(Exception("y")))
    setattr(g.board, "count_checkers", lambda c: {"off": 11})
    assert g._get_off_count("white") == 11

def test_get_off_count_by_deduction_with_bar_and_points(monkeypatch):
    """
    Verifica la deducción de fichas borneadas cuando no se pueden usar count_off,
    count_at ni count_checkers. Solo cuenta fichas del color indicado.
    """
    dice = SimpleNamespace(available_moves=lambda: [], roll=lambda: None, use_move=lambda v: None, has_moves=lambda: False)
    g = _game_with(dice)

    # Rompemos todos los métodos previos para forzar la deducción manual
    setattr(g.board, "count_off", lambda color: (_ for _ in ()).throw(Exception("x")))
    setattr(g.board, "count_at", lambda pos, color: (_ for _ in ()).throw(Exception("y")))
    setattr(g.board, "count_checkers", lambda c: (_ for _ in ()).throw(Exception("z")))

    class _Chk:
        def __init__(self, col): self._c = col
        def get_color(self): return self._c

    # Caso 1: 2 blancas en tablero (p5) + 2 en BAR -> 15 - (2 + 2) = 11
    def _get_point_case1(p):
        if p == 5:
            return [_Chk("white"), _Chk("white")]
        if p == 8:
            return [_Chk("black")]  # no cuentan
        return []

    monkeypatch.setattr(g.board, "get_point", _get_point_case1, raising=False)
    monkeypatch.setattr(g.board, "get_checkers_in_bar", lambda c=None: [object(), object()], raising=False)
    assert g._get_off_count("white") == 11

    # Caso 2: 2 blancas en tablero + **3** en BAR -> 15 - (2 + 3) = 10
    def _get_point_case2(p):
        if p == 5:
            return [_Chk("white"), _Chk("white")]
        if p == 8:
            return [_Chk("black")]
        return []

    monkeypatch.setattr(g.board, "get_point", _get_point_case2, raising=False)
    monkeypatch.setattr(g.board, "get_checkers_in_bar", lambda c=None: [object(), object(), object()], raising=False)
    assert g._get_off_count("white") == 10
