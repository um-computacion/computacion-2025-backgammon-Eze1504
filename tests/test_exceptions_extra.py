import pytest
from core.board import Board
from core.game import BackgammonGame, GameRuleError
from core.dice import Dice
from core.player import Player

def test_invalid_move_raises():
    board = Board()
    # Origen fuera de rango: debe fallar
    with pytest.raises(Exception):
        board.move_checker("white", 30, 1)

def test_start_turn_twice_raises():
    b = Board()
    d = Dice()
    p1, p2 = Player("P1", "white"), Player("P2", "black")
    g = BackgammonGame(b, d, (p1, p2))
    g.start_turn()
    with pytest.raises(GameRuleError):
        g.start_turn()  # turno ya activo

def test_end_turn_without_start_raises():
    b = Board()
    d = Dice()
    p1, p2 = Player("P1", "white"), Player("P2", "black")
    g = BackgammonGame(b, d, (p1, p2))
    with pytest.raises(GameRuleError):
        g.end_turn()  # sin turno activo

# Dummy dice controlado para “dado no disponible”
class _DummyDice:
    def __init__(self, vals):
        # vals es la lista de movimientos disponibles (e.g., [1, 2])
        self._vals = list(vals)
    def roll(self):
        # No hace nada; ya tenemos los valores cargados
        pass
    def available_moves(self):
        return list(self._vals)
    def use_move(self, v):
        self._vals.remove(v)
    def has_moves(self):
        return bool(self._vals)

def test_apply_move_with_invalid_die():
    b = Board()
    # Dados fijos: 1 y 2 disponibles → 6 NO disponible
    d = _DummyDice([1, 2])
    p1, p2 = Player("P1", "white"), Player("P2", "black")
    g = BackgammonGame(b, d, (p1, p2), starting_color="white")
    g.start_turn()
    # Pedimos mover con 6 que no está disponible → debe explotar
    with pytest.raises(GameRuleError):
        g.apply_player_move(from_pos=1, steps=6)
