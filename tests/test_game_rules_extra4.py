import pytest
from types import SimpleNamespace

from core.board import Board
from core.player import Player
from core.game import BackgammonGame, GameRuleError


def _players():
    return Player("White", "white"), Player("Black", "black")


def _game_with(dice):
    b = Board()
    w, k = _players()
    return BackgammonGame(b, dice, (w, k), starting_color=w.color)


def test_end_turn_blocks_if_legal_moves_exist(monkeypatch):
    # has_moves True y existe AL MENOS una jugada legal -> debe bloquear end_turn
    dice = SimpleNamespace(available_moves=lambda: [3, 5], roll=lambda: None)
    g = _game_with(dice)
    g.start_turn()
    monkeypatch.setattr(g.dice, "has_moves", lambda: True, raising=False)
    monkeypatch.setattr(g, "_any_legal_move_exists_for_any_die", lambda color: True)
    with pytest.raises(GameRuleError):
        g.end_turn()  # hay jugadas -> no se puede cerrar


def test_bar_priority_blocks_non_bar_move(monkeypatch):
    # Si hay fichas en BAR, NO se puede mover desde otro punto
    dice = SimpleNamespace(available_moves=lambda: [2], roll=lambda: None, use_move=lambda v: None)
    g = _game_with(dice)
    g.start_turn()
    monkeypatch.setattr(g, "_has_bar", lambda color=None: True)  # hay fichas en BAR
    with pytest.raises(GameRuleError):
        g.apply_player_move(from_pos=13, steps=2)  # no es BAR -> debería bloquear


def test_high_die_rule_enforced(monkeypatch):
    """
    Quedan dos valores distintos (2 y 5) y SOLO el mayor (5) es jugable -> si intento con 2, debe fallar.
    """
    used = {"v": None}
    dice = SimpleNamespace(
        available_moves=lambda: [2, 5], roll=lambda: None, use_move=lambda v: used.__setitem__("v", v)
    )
    g = _game_with(dice)
    g.start_turn()
    monkeypatch.setattr(g, "_has_bar", lambda color=None: False)

    # Heurística: 2 NO jugable, 5 SÍ jugable
    monkeypatch.setattr(g, "_legal_single_move_exists", lambda color, steps: (steps == 5))

    with pytest.raises(GameRuleError):
        g.apply_player_move(from_pos=13, steps=2)  # intenta con el menor -> prohibido


def test_state_reports_moves_and_count(monkeypatch):
    dice = SimpleNamespace(available_moves=lambda: [6, 1], roll=lambda: None)
    g = _game_with(dice)
    # Forzamos el listado de dados que el state debe reflejar
    monkeypatch.setattr(g, "_get_available_moves", lambda: [6, 1])
    st = g.state()
    assert st.current_color == "white"
    assert tuple(st.dice_values) == (6, 1)
    assert st.moves_left == 2


def test_apply_calls_reenter_when_on_bar(monkeypatch):
    # Si hay BAR y from_pos == 0, debe invocar reenter_checker
    called = {"reenter": False, "used": None}

    def _reenter(color, steps):
        called["reenter"] = True
        assert color == "white" and steps == 3

    dice = SimpleNamespace(
        available_moves=lambda: [3],
        roll=lambda: None,
        use_move=lambda v: called.__setitem__("used", v),
    )
    g = _game_with(dice)
    g.start_turn()
    monkeypatch.setattr(g, "_has_bar", lambda color=None: True)
    monkeypatch.setattr(g.board, "reenter_checker", _reenter, raising=False)

    # Evitar finalización accidental: 0 off
    monkeypatch.setattr(g.board, "count_checkers", lambda color: {"off": 0}, raising=False)

    g.apply_player_move(from_pos=0, steps=3)
    assert called["reenter"] is True
    assert called["used"] == 3

def test_end_turn_allows_when_no_moves_and_switches_turn(monkeypatch):
    # has_moves=False y no hay jugadas -> end_turn debe permitir y cambiar el color
    dice = SimpleNamespace(available_moves=lambda: [2], roll=lambda: None)
    g = _game_with(dice)
    g.start_turn()
    assert g.current_color == "white"

    monkeypatch.setattr(g.dice, "has_moves", lambda: False, raising=False)
    monkeypatch.setattr(g, "_any_legal_move_exists_for_any_die", lambda color: False)

    g.end_turn()
    assert g.current_color == "black"  # alternó el turno


def test_end_turn_allows_when_has_moves_but_no_legal(monkeypatch):
    # has_moves=True pero NO hay jugadas legales -> end_turn debe permitir
    dice = SimpleNamespace(available_moves=lambda: [6], roll=lambda: None)
    g = _game_with(dice)
    g.start_turn()

    monkeypatch.setattr(g.dice, "has_moves", lambda: True, raising=False)
    monkeypatch.setattr(g, "_any_legal_move_exists_for_any_die", lambda color: False)

    g.end_turn()
    assert g.current_color == "black"


def test_apply_calls_move_or_bear_off_when_present(monkeypatch):
    # Si Board EXPONE move_or_bear_off, la usa en vez de move_checker
    called = {"mob": False, "used": None}

    def _mob(color, from_pos, steps):
        called["mob"] = True
        assert color == "white" and from_pos == 8 and steps == 2

    dice = SimpleNamespace(
        available_moves=lambda: [2],
        roll=lambda: None,
        use_move=lambda v: called.__setitem__("used", v),
    )
    g = _game_with(dice)
    g.start_turn()

    monkeypatch.setattr(g, "_has_bar", lambda color=None: False)
    # Inyectamos move_or_bear_off en el board (aunque originalmente no exista)
    monkeypatch.setattr(g.board, "move_or_bear_off", _mob, raising=False)
    # Evitar que finalice por victoria accidental
    monkeypatch.setattr(g.board, "count_checkers", lambda color: {"off": 0}, raising=False)

    g.apply_player_move(from_pos=8, steps=2)
    assert called["mob"] is True
    assert called["used"] == 2


def test_apply_consumes_die_and_updates_state(monkeypatch):
    # Luego de mover, el dado usado ya no debe estar en available_moves
    bag = {"moves": [3, 5]}
    dice = SimpleNamespace(
        available_moves=lambda: list(bag["moves"]),
        roll=lambda: None,
        use_move=lambda v: bag["moves"].remove(v),
    )
    g = _game_with(dice)
    g.start_turn()

    monkeypatch.setattr(g, "_has_bar", lambda color=None: False)
    monkeypatch.setattr(g.board, "move_checker", lambda *a, **k: None, raising=False)
    monkeypatch.setattr(g.board, "count_checkers", lambda color: {"off": 0}, raising=False)

    g.apply_player_move(from_pos=13, steps=5)
    # 5 se consumió
    assert bag["moves"] == [3]
    # state refleja lo que retorne _get_available_moves, lo forzamos:
    monkeypatch.setattr(g, "_get_available_moves", lambda: list(bag["moves"]))
    st = g.state()
    assert tuple(st.dice_values) == (3,)
    assert st.moves_left == 1


def test_finalize_via_count_off(monkeypatch):
    """
    Tras un movimiento normal, si count_off -> 15, el juego debe finalizar y setear result.
    Nos acoplamos a la implementación real que consulta count_off (y no count_checkers).
    """
    dice = SimpleNamespace(available_moves=lambda: [1], roll=lambda: None, use_move=lambda v: None)
    g = _game_with(dice)
    g.start_turn()

    monkeypatch.setattr(g, "_has_bar", lambda color=None: False)
    monkeypatch.setattr(g.board, "move_checker", lambda *a, **k: None, raising=False)

    # Forzamos la condición de victoria por OFF=15 para el color actual
    monkeypatch.setattr(g.board, "count_off", lambda color: 15 if color == g.current_color else 0, raising=False)

    # Evitamos depender de la lógica interna del outcome
    monkeypatch.setattr(g, "_determine_outcome", lambda wc, lc: ("single", 1))

    g.apply_player_move(from_pos=6, steps=1)

    assert g.game_over is True
    assert g.result is not None
    assert g.result.winner_color == "white"
    assert g.result.outcome == "single"
    assert g.result.points == 1



def test_high_die_rule_allows_when_both_playable(monkeypatch):
    # Si ambos dados son jugables, NO se fuerza el mayor: mover con el menor es válido
    used = {"v": None}
    dice = SimpleNamespace(
        available_moves=lambda: [2, 5],
        roll=lambda: None,
        use_move=lambda v: used.__setitem__("v", v),
    )
    g = _game_with(dice)
    g.start_turn()
    monkeypatch.setattr(g, "_has_bar", lambda color=None: False)
    # Ambos jugables
    monkeypatch.setattr(g, "_legal_single_move_exists", lambda color, steps: True)

    # Debe permitir usar el 2 sin explotar
    monkeypatch.setattr(g.board, "move_checker", lambda *a, **k: None, raising=False)
    monkeypatch.setattr(g.board, "count_checkers", lambda color: {"off": 0}, raising=False)

    g.apply_player_move(from_pos=13, steps=2)
    assert used["v"] == 2  # se consumió el menor y fue válido

def _players():
    return Player("W", "white"), Player("K", "black")


def _game_with(dice):
    b = Board()
    w, k = _players()
    return BackgammonGame(b, dice, (w, k), starting_color=w.color)


def test_bar_priority_blocks_move_from_non_bar(monkeypatch):
    # Si hay fichas en BAR, intentar mover desde otro punto debe fallar
    used = {"die": None}
    dice = SimpleNamespace(
        available_moves=lambda: [3],
        roll=lambda: None,
        use_move=lambda v: used.__setitem__("die", v),
    )
    g = _game_with(dice)
    g.start_turn()

    # Forzamos "hay fichas en BAR"
    monkeypatch.setattr(g, "_has_bar", lambda color=None: True)
    # No debería siquiera invocar movimiento: debe lanzar error antes
    with pytest.raises(GameRuleError):
        g.apply_player_move(from_pos=6, steps=3)
    assert used["die"] is None  # no consumió dado


def test_high_die_rule_enforced_when_only_high_playable(monkeypatch):
    # Dos dados (2,5): solo el 5 es jugable → si intenta usar 2, debe fallar
    used = {"die": None}
    dice = SimpleNamespace(
        available_moves=lambda: [2, 5],
        roll=lambda: None,
        use_move=lambda v: used.__setitem__("die", v),
    )
    g = _game_with(dice)
    g.start_turn()

    monkeypatch.setattr(g, "_has_bar", lambda color=None: False)
    # Solo el alto (5) es jugable
    def _legal(color, steps):
        return steps == 5
    monkeypatch.setattr(g, "_legal_single_move_exists", _legal)

    # Intentar con 2 debe explotar por regla del dado más alto
    with pytest.raises(GameRuleError):
        g.apply_player_move(from_pos=8, steps=2)

    # Con 5 debe pasar y consumirlo
    monkeypatch.setattr(g.board, "move_checker", lambda *a, **k: None, raising=False)
    monkeypatch.setattr(g.board, "count_off", lambda color: 0, raising=False)
    g.apply_player_move(from_pos=8, steps=5)
    assert used["die"] == 5


def test_state_reports_moves_left_and_color(monkeypatch):
    # state() refleja dice_values y moves_left calculados
    dice = SimpleNamespace(
        available_moves=lambda: [6, 3, 3],
        roll=lambda: None,
        use_move=lambda v: None,
    )
    g = _game_with(dice)
    g.start_turn()

    # Por las dudas, forzamos _get_available_moves a devolver la misma secuencia
    monkeypatch.setattr(g, "_get_available_moves", lambda: [6, 3, 3])
    st = g.state()
    assert st.current_color == "white"
    assert tuple(st.dice_values) == (6, 3, 3)
    assert st.moves_left == 3


def test_get_available_moves_accepts_list_attribute():
    # _get_available_moves debe soportar que dice.available_moves sea una LISTA (no solo callable)
    class _ListDice:
        def __init__(self):
            self.available_moves = [4, 4]
        def roll(self):  # para start_turn
            pass

    d = _ListDice()
    g = _game_with(d)
    g.start_turn()

    st = g.state()  # usa _get_available_moves
    assert tuple(st.dice_values) == (4, 4)
    assert st.moves_left == 2


def test_finalize_game_idempotent(monkeypatch):
    # Llamar _finalize_game dos veces no debe cambiar el resultado inicial (idempotencia)
    dice = SimpleNamespace(available_moves=lambda: [], roll=lambda: None, use_move=lambda v: None)
    g = _game_with(dice)

    # Outcome controlado
    monkeypatch.setattr(g, "_determine_outcome", lambda wc, lc: ("single", 1))
    # Primera finalización
    g._finalize_game("white")
    first = (g.game_over, g.result.winner_color, g.result.outcome, g.result.points)

    # Segunda finalización (no debe modificar)
    monkeypatch.setattr(g, "_determine_outcome", lambda wc, lc: ("backgammon", 3))
    g._finalize_game("white")
    second = (g.game_over, g.result.winner_color, g.result.outcome, g.result.points)

    assert first == second