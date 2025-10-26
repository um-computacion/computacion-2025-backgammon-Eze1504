import sys, os, pytest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.board import Board
from core.checker import Checker

class TestBoardCaptures:
    def setup_method(self):
        self.b = Board()

    def test_can_capture_and_capture_at(self):
        # Dejar blot negro en 5
        self.b._Board__points[5].clear()
        self.b._Board__points[5].append(Checker("black", 5))
        assert self.b.can_capture(5, "white") is True
        captured = self.b._capture_at(5, "white")
        assert captured and captured.get_color() == "black"
        assert captured.get_position() == 0  # en BAR
        assert len(self.b.get_point(5)) == 0
        assert captured in self.b.get_point(0)

    def test_move_checker_with_capture(self):
        # blot negro en 5; mover white de 6 con 1 paso
        self.b._Board__points[5].clear()
        self.b._Board__points[5].append(Checker("black", 5))
        from_pos, to_pos, cap = self.b.move_checker("white", 6, 1)
        assert (from_pos, to_pos) == (6, 5)
        assert cap and cap.get_color() == "black" and cap.get_position() == 0
        pts = self.b.get_point(5)
        assert any(ch.get_color() == "white" for ch in pts)
