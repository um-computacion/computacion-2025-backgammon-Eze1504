import pytest
from core.board import Board
from core.game import BackgammonGame, GameRuleError
from core.checker import Checker

# -------------------- Infra de tests --------------------

class DummyDice:
    """Dado controlado: no tira solo; se programa por turno con reset()."""
    def __init__(self):
        self._vals = []
    def reset(self, pair):
        a, b = pair
        if a == b:
            self._vals = [a, a, a, a]
        else:
            self._vals = [a, b]
    def available_moves(self):
        return list(self._vals)
    def use_move(self, v):
        self._vals.remove(v)
    def has_moves(self):
        return bool(self._vals)

class _P:
    def __init__(self, color): self.color = color

@pytest.fixture
def W(): return _P("white")

@pytest.fixture
def B(): return _P("black")

@pytest.fixture
def board():
    return Board()

def clear_board(board: Board):
    for p in range(26):
        board.set_count_at(p, "white", 0)
        board.set_count_at(p, "black", 0)

def put_on_bar(board: Board, color: str, n=1):
    for _ in range(n):
        board.place_checker(Checker(color, 0), 0)

# -------------------- Tests de integración --------------------

def test_full_finish_with_doubles_and_result_backgammon(board, W, B):
    """
    Partida 'corta' pero completa:
      - White tiene 13 off y 2 en punto 1 (falta bornear 2).
      - Black no tiene ninguna borneada y tiene fichas en BAR => backgammon si White gana.
      - White usa dobles de 1 para terminar el juego en su turno.
    """
    clear_board(board)
    # Estado ganador para white en 1 jugada múltiple
    board.set_count_at(25, "white", 13)   # 13 borneadas
    board.set_count_at(1, "white", 2)     # faltan 2 en el punto 1

    # Black: 0 off y 2 en BAR -> califica como backgammon si pierde
    board.set_count_at(0, "black", 2)
    board.set_count_at(12, "black", 13)

    dice = DummyDice()
    g = BackgammonGame(board, dice, (W, B), starting_color=W.color)

    # Turno de white: dobles de 1 (4 movimientos disponibles)
    dice.reset((1, 1))
    g.start_turn()

    # Bornear dos veces desde punto 1 con '1'
    g.apply_player_move(from_pos=1, steps=1)
    g.apply_player_move(from_pos=1, steps=1)

    # Quedarán 2 movimientos de '1' sin jugada posible -> el juego ya debería marcar fin
    assert g.game_over is True
    assert g.result is not None
    assert g.result.winner_color == "white"
    assert g.result.outcome == "backgammon"
    assert g.result.points == 3

def test_blocked_reentry_then_unblocked_next_turn(board, W, B):
    """
    Escenario multi-turno:
      - White tiene 1 ficha en BAR y quiere reingresar con '1' (destino 24).
      - Black tiene 2 fichas en 24 -> reingreso de white bloqueado.
      - White NO puede mover -> puede terminar turno aunque queden dados.
      - Turno de Black: usa '1' para bornear 2 veces desde 24 (desbloquea) y
        luego consume los dos '1' restantes con movimientos 19->20.
      - Siguiente turno de White: ahora puede reingresar con '1'.
    """
    clear_board(board)

    # White: 1 ficha en BAR
    put_on_bar(board, "white", 1)

    # Black: bloquear 24 con 2 fichas
    board.set_count_at(24, "black", 2)
    # El resto de negras dentro del home (19..24) para permitir bearing off
    board.set_count_at(19, "black", 13)

    dice = DummyDice()
    g = BackgammonGame(board, dice, (W, B), starting_color=W.color)

    # Turno de White: dados (1,1) pero reingreso a 24 bloqueado
    dice.reset((1, 1))
    g.start_turn()
    # No hay movimiento legal (con BAR bloqueado); debe permitir cerrar turno
    g.end_turn()
    assert g.current_color == B.color

    # Turno de Black: (1,1) puede bornear desde 24 dos veces
    dice.reset((1, 1))
    g.start_turn()
    g.apply_player_move(from_pos=24, steps=1)
    g.apply_player_move(from_pos=24, steps=1)

    # Consumir los dos '1' restantes con movimientos dentro del home
    g.apply_player_move(from_pos=19, steps=1)  # 19 -> 20
    g.apply_player_move(from_pos=19, steps=1)  # otro 19 -> 20

    # Ahora sí puede terminar el turno
    g.end_turn()
    assert g.current_color == W.color
    assert board.count_checkers_at(24, "black") < 2  # 24 ya no bloquea

    # Turno de White otra vez: (1,1) ahora sí puede reingresar desde BAR a 24
    dice.reset((1, 1))
    g.start_turn()
    g.apply_player_move(from_pos=0, steps=1)  # reingreso a 24
    assert not board.has_checkers_in_bar("white")  # ya reingresó


def test_use_all_dice_across_turn_cannot_end_early(board, W, B):
    """
    Integración de 'usar todos los dados':
      - White con 2 fichas en BAR y dados (2,5).
      - Reingresa con 2.
      - Intentar cerrar el turno con 5 restante (y jugable) debe fallar.
      - Luego reingresa con 5 y ahora sí puede terminar.
    """
    clear_board(board)
    put_on_bar(board, "white", 2)

    dice = DummyDice()
    g = BackgammonGame(board, dice, (W, B), starting_color=W.color)

    dice.reset((2, 5))
    g.start_turn()

    # Reingresa con 2 (destino 23 para white)
    g.apply_player_move(from_pos=0, steps=2)

    # Queda '5' que todavía es jugable (destino 20) -> no debe permitir terminar
    with pytest.raises(GameRuleError):
        g.end_turn()

    # Usamos el '5'
    g.apply_player_move(from_pos=0, steps=5)

    # Ahora sí puede terminar
    g.end_turn()
    assert g.current_color == B.color
