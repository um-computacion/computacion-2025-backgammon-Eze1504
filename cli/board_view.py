# -*- coding: utf-8 -*-
"""
Vista ASCII del tablero de Backgammon.
No muta estado. Intenta usar board.count_at(pos, color). Si no existe, asume 0.
"""

from typing import Iterable, Tuple

WHITE = "white"
BLACK = "black"

POINTS_TOP = list(range(13, 25))       # 13..24 (izq->der)
POINTS_BOT = list(range(12, 0, -1))    # 12..1  (izq->der)

MAX_STACK_RENDER = 5  # cuántas fichas se dibujan por columna antes de poner "+n"


def _count_at(board, pos: int, color: str) -> int:
    """
    Intenta board.count_at(pos, color). Si no existe, retorna 0.
    """
    fn = getattr(board, "count_at", None)
    if callable(fn):
        try:
            return int(fn(pos, color))
        except Exception:
            return 0
    return 0


def _counts_pair(board, pos: int) -> Tuple[int, int]:
    """(w, b) en el punto dado."""
    return _count_at(board, pos, WHITE), _count_at(board, pos, BLACK)


def _render_column(w: int, b: int, height: int = MAX_STACK_RENDER, top: bool = True) -> Iterable[str]:
    """
    Devuelve una lista de 'height' filas con caracteres:
      - 'W' por blancas, 'B' por negras, '.' vacío
      - Para exceso, la fila superior (si top) o inferior (si not top) muestra '+n'
    """
    cells = []
    total = w + b
    # Distribución simple: apilamos del borde hacia adentro
    # Para la fila de exceso:
    excess = max(0, total - height)

    # Construimos un vector con símbolos sin excedente
    symbols = (["W"] * min(w, height)) + (["B"] * min(b, height - min(w, height)))
    symbols += ["." for _ in range(max(0, height - len(symbols)))]

    # Convertimos en filas (top: de arriba a abajo; bottom: de abajo a arriba)
    if top:
        rows = symbols[::-1]  # arriba es el final de la pila
        if excess > 0:
            rows[0] = f"+{excess}"
    else:
        rows = symbols[:]     # abajo es el inicio de la pila
        if excess > 0:
            rows[-1] = f"+{excess}"

    # Aseguramos ancho homogéneo (2 chars) para +n
    fixed = []
    for s in rows:
        if len(s) == 1:
            fixed.append(f" {s}")
        else:
            # "+n" puede ser 2-3 chars; lo compactamos a 2 si n<10, si no truncamos visual
            if s.startswith("+") and len(s) > 2:
                fixed.append("+*")
            else:
                fixed.append(s)
    return fixed


def _render_row(points: Iterable[int], board, top: bool) -> str:
    """
    Dibuja las columnas verticales para una fila (top o bottom) en varias líneas.
    Retorna un bloque multilinea.
    """
    col_blocks = []
    for p in points:
        w, b = _counts_pair(board, p)
        col_blocks.append(list(_render_column(w, b, MAX_STACK_RENDER, top=top)))

    # rotamos para imprimir fila por fila
    # top: imprimir de 0..MAX-1; bottom: igual (los bloques ya vienen ordenados)
    lines = []
    for r in range(MAX_STACK_RENDER):
        parts = []
        for block in col_blocks:
            parts.append(block[r])
        lines.append(" ".join(parts))
    return "\n".join(lines)


def _render_header_footer(points: Iterable[int]) -> str:
    labels = [f"{p:>2}" for p in points]
    return " ".join(labels)


def _indent_block(block: str, prefix: str = "   ") -> str:
    """Agrega un prefijo a cada línea de un bloque multilinea."""
    return "\n".join(f"{prefix}{line}" for line in block.splitlines())


def _render_bar_and_off(board) -> str:
    w_bar = _count_at(board, 0, WHITE)
    b_bar = _count_at(board, 0, BLACK)
    w_off = _count_at(board, 25, WHITE)
    b_off = _count_at(board, 25, BLACK)
    return (
        f"BAR: W={w_bar} B={b_bar}    OFF: W={w_off} B={b_off}"
    )


def render_board(board) -> str:
    """
    Tablero en ASCII, con dos alas (top: 13..24, bottom: 12..1),
    más leyendas y BAR/OFF.
    """
    top_idx = _render_header_footer(POINTS_TOP)
    top_rows = _render_row(POINTS_TOP, board, top=True)

    sep = "-" * max(len(top_idx), 60)

    bot_rows = _render_row(POINTS_BOT, board, top=False)
    bot_idx = _render_header_footer(POINTS_BOT)

    meta = _render_bar_and_off(board)

    return (
        f"   {top_idx}\n"
        f"{_indent_block(top_rows)}\n"
        f"   {sep}\n"
        f"{_indent_block(bot_rows)}\n"
        f"   {bot_idx}\n"
        f"{meta}"
    )


def render_game(game) -> str:
    """
    Vista combinada: estado (color, dados, movimientos) + tablero.
    No depende de detalles internos más allá de game.state() y board.
    """
    st = game.state()
    color = getattr(st, "current_color", "white")
    dice = tuple(getattr(st, "dice_values", []) or [])
    moves = getattr(st, "moves_left", 0)

    header = f"Turno: {color} | Dados: {dice} | Movimientos: {moves}"
    board_txt = render_board(game.board)
    return f"{header}\n\n{board_txt}"
