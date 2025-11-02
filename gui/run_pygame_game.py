# -*- coding: utf-8 -*-
"""
Pygame UI – Backgammon MVP
- Tablero con 24 puntos, BAR y OFF.
- Render de fichas por color (white/black) leyendo Board.count_at(pos, color).
- HUD con dados, turno y ayuda.
- Interacciones mínimas:
    * R: roll (start_turn)
    * H: hint (overlay)
    * E: end turn
    * S: save snapshot.json
    * Click izquierdo: seleccionar punto "from"
    * Tecla 1..6: mover "from" con steps (si los dados lo permiten)
    * ESC / cerrar: salir
Requiere:
    - core.board.Board
    - core.dice.Dice
    - core.player.Player
    - core.game.BackgammonGame
    - cli.hint_engine.suggest_move (opcional)
"""

import sys
from typing import Optional, Tuple

import pygame

from core.board import Board
from core.dice import Dice
from core.player import Player
from core.game import BackgammonGame
from core.exceptions import (
    BackgammonException,
    InvalidMoveException,
    NoMovesAvailableException,
    DiceNotRolledException,
)

# hint opcional (no rompe si no existe)
try:
    from cli.hint_engine import suggest_move  # type: ignore
except Exception:  # pragma: no cover
    def suggest_move(game):  # fallback mínimo
        return "Hint no disponible (módulo opcional ausente)."


# ----------- Config visual -----------
W, H = 1100, 700
MARGIN = 20
BOARD_W, BOARD_H = W - 2 * MARGIN, H - 2 * MARGIN
BAR_W = 60
OFF_W = 80
POINTS_PER_SIDE = 12

COL_BG = (32, 30, 28)
COL_BOARD = (184, 145, 104)
COL_TRI_A = (110, 78, 52)
COL_TRI_B = (230, 205, 175)
COL_BAR = (70, 55, 40)
COL_OFF = (60, 70, 85)
COL_TEXT = (240, 240, 240)
COL_HINT = (255, 240, 150)
COL_WHITE = (245, 245, 245)
COL_BLACK = (25, 25, 25)
COL_SELECT = (160, 210, 255)

FPS = 60
HUD_H = 90
CHECKER_RADIUS = 20
CHECKER_PAD = 6
MAX_STACK_RENDER = 5  # apilar hasta N visibles (como el ASCII)

# Posiciones especiales
BAR_POS = 0
OFF_POS = 25


# ----------- Helpers de Board tolerantes a distintas APIs -----------
def count_at(board, point, color):
    """
    Devuelve cantidad de fichas de 'color' en 'point'.
    Prioriza count_point / count_at; fallback con get_point.
    """
    if hasattr(board, "count_point"):
        return board.count_point(point, color)
    if hasattr(board, "count_at"):
        return board.count_at(point, color)
    if hasattr(board, "get_point"):
        try:
            return sum(1 for ch in board.get_point(point) if ch.get_color() == color)
        except Exception:
            return 0
    return 0


def count_bar(board, color):
    if hasattr(board, "count_bar"):
        return board.count_bar(color)
    if hasattr(board, "get_checkers_in_bar"):
        try:
            return len(board.get_checkers_in_bar(color))
        except Exception:
            return 0
    # Fallback común: BAR = 0
    return count_at(board, BAR_POS, color)


def count_off(board, color):
    if hasattr(board, "count_off"):
        return board.count_off(color)
    # Fallback común: OFF = 25
    return count_at(board, OFF_POS, color)


def init_game() -> BackgammonGame:
    board = Board()
    dice = Dice()
    white = Player("White", "white")
    black = Player("Black", "black")
    game = BackgammonGame(board, dice, (white, black), starting_color=white.color)
    return game


def build_point_layout(rect: pygame.Rect) -> Tuple[dict, pygame.Rect, pygame.Rect]:
    """
    Devuelve:
      - positions: {point_index: (center_x, is_top, half_rect)}
      - bar_rect
      - off_rect
    """
    # Área del tablero sin HUD:
    board_rect = pygame.Rect(rect.left, rect.top + HUD_H, rect.width, rect.height - HUD_H)
    # OFF a la derecha
    off_rect = pygame.Rect(board_rect.right - OFF_W, board_rect.top, OFF_W, board_rect.height)
    panel_rect = pygame.Rect(board_rect.left, board_rect.top, board_rect.width - OFF_W, board_rect.height)

    # Dentro del panel: 12 puntos arriba, 12 abajo con BAR en el centro (6 + BAR + 6)
    cols_left = POINTS_PER_SIDE // 2  # 6
    cols_right = POINTS_PER_SIDE // 2  # 6

    bar_rect = pygame.Rect(0, 0, BAR_W, panel_rect.height)
    points_area_w = panel_rect.width - BAR_W
    col_w = points_area_w // POINTS_PER_SIDE

    x0 = panel_rect.left
    xs_left = [x0 + i * col_w for i in range(cols_left)]                  # 0..5
    x_bar = x0 + cols_left * col_w                                       # BAR
    xs_right = [x_bar + BAR_W + i * col_w for i in range(cols_right)]    # 0..5 a derecha
    bar_rect.topleft = (x_bar, panel_rect.top)

    # Triángulos/puntos:
    positions = {}
    x_cols_bottom = list(reversed(xs_left + xs_right))  # abajo 1..12 (derecha→izquierda)
    x_cols_top = list(reversed(xs_left + xs_right))     # arriba 13..24 (derecha→izquierda)

    half_h = panel_rect.height // 2
    top_rect = pygame.Rect(panel_rect.left, panel_rect.top, panel_rect.width, half_h)
    bot_rect = pygame.Rect(panel_rect.left, panel_rect.top + half_h, panel_rect.width, half_h)

    for i in range(POINTS_PER_SIDE):  # 0..11
        # abajo: puntos 1..12
        pt_idx_bottom = i + 1
        cx_b = x_cols_bottom[i] + col_w // 2
        positions[pt_idx_bottom] = (cx_b, False, bot_rect)

        # arriba: puntos 13..24
        pt_idx_top = i + 13
        cx_t = x_cols_top[i] + col_w // 2
        positions[pt_idx_top] = (cx_t, True, top_rect)

    bar_rect = pygame.Rect(x_bar, panel_rect.top, BAR_W, panel_rect.height)
    return positions, bar_rect, off_rect


def draw_board(surface, rect, positions, bar_rect, off_rect, selected_from: Optional[int], font):
    # Fondo tablero
    pygame.draw.rect(surface, COL_BOARD, (rect.left, rect.top + HUD_H, rect.width, rect.height - HUD_H), border_radius=12)

    # Mitades:
    half_h = (rect.height - HUD_H) // 2
    top = pygame.Rect(rect.left, rect.top + HUD_H, rect.width, half_h)
    bottom = pygame.Rect(rect.left, rect.top + HUD_H + half_h, rect.width, half_h)

    # BAR y OFF
    pygame.draw.rect(surface, COL_BAR, bar_rect)
    pygame.draw.rect(surface, COL_OFF, off_rect)

    # Triángulos alternados arriba/abajo
    used_xs_top, used_xs_bottom = [], []
    for pt in range(13, 25):
        cx, _, _ = positions[pt]
        used_xs_top.append(cx)
    for pt in range(1, 13):
        cx, _, _ = positions[pt]
        used_xs_bottom.append(cx)

    used_xs_top.sort()
    used_xs_bottom.sort()

    def draw_triangles(xs, is_top):
        for i, cx in enumerate(xs):
            color = COL_TRI_A if i % 2 == 0 else COL_TRI_B
            if is_top:
                p1 = (cx, top.bottom)  # base
                p2 = (cx - 30, top.top)
                p3 = (cx + 30, top.top)
            else:
                p1 = (cx, bottom.top)  # base
                p2 = (cx - 30, bottom.bottom)
                p3 = (cx + 30, bottom.bottom)
            pygame.draw.polygon(surface, color, [p1, p2, p3])

    draw_triangles(used_xs_top, True)
    draw_triangles(used_xs_bottom, False)

    # Selección de origen
    if selected_from is not None:
        if selected_from in positions:
            cx, _, area = positions[selected_from]
            highlight = pygame.Rect(cx - 34, area.top, 68, area.height)
        elif selected_from == BAR_POS:
            highlight = bar_rect.inflate(-6, -6)
        elif selected_from == OFF_POS:
            highlight = off_rect.inflate(-6, -6)
        else:
            highlight = None
        if highlight:
            pygame.draw.rect(surface, COL_SELECT, highlight, width=3, border_radius=6)

    # Etiquetas
    txt = font.render("BAR", True, COL_TEXT)
    surface.blit(txt, (bar_rect.centerx - txt.get_width() // 2, bar_rect.top + 6))
    txt2 = font.render("OFF", True, COL_TEXT)
    surface.blit(txt2, (off_rect.centerx - txt2.get_width() // 2, off_rect.top + 6))


def draw_checkers(surface, positions, bar_rect, off_rect, board):
    """Dibuja stacks para cada punto + BAR + OFF."""
    def draw_stack_at(point, color):
        count = count_at(board, point, color) if point not in (BAR_POS, OFF_POS) else (
            count_bar(board, color) if point == BAR_POS else count_off(board, color)
        )
        if count <= 0:
            return

        if point in positions:
            cx, is_top, area = positions[point]
            for i in range(min(count, MAX_STACK_RENDER)):
                if is_top:
                    cy = area.bottom - (CHECKER_RADIUS + i * (2 * CHECKER_RADIUS + CHECKER_PAD))
                else:
                    cy = area.top + (CHECKER_RADIUS + i * (2 * CHECKER_RADIUS + CHECKER_PAD))
                fill = COL_WHITE if color == "white" else COL_BLACK
                pygame.draw.circle(surface, fill, (cx, cy), CHECKER_RADIUS)
                pygame.draw.circle(surface, (0, 0, 0), (cx, cy), CHECKER_RADIUS, 2)

            # contador +n
            if count > MAX_STACK_RENDER:
                font = pygame.font.SysFont(None, 16)
                txt = font.render(f"+{count - MAX_STACK_RENDER}", True, (255, 255, 255))
                surface.blit(txt, (cx - txt.get_width() // 2, area.centery - txt.get_height() // 2))

        elif point == BAR_POS:
            cx = bar_rect.centerx
            top = bar_rect.top + 40
            for i in range(min(count, MAX_STACK_RENDER)):
                cy = top + i * (2 * CHECKER_RADIUS + CHECKER_PAD)
                fill = COL_WHITE if color == "white" else COL_BLACK
                pygame.draw.circle(surface, fill, (cx, cy), CHECKER_RADIUS)
                pygame.draw.circle(surface, (0, 0, 0), (cx, cy), CHECKER_RADIUS, 2)
        elif point == OFF_POS:
            cx = off_rect.centerx
            top = off_rect.top + 40
            for i in range(min(count, MAX_STACK_RENDER)):
                cy = top + i * (2 * CHECKER_RADIUS + CHECKER_PAD)
                fill = COL_WHITE if color == "white" else COL_BLACK
                pygame.draw.circle(surface, fill, (cx, cy), CHECKER_RADIUS)
                pygame.draw.circle(surface, (0, 0, 0), (cx, cy), CHECKER_RADIUS, 2)

    # puntos
    for pt in range(1, 25):
        draw_stack_at(pt, "white")
        draw_stack_at(pt, "black")
    # bar/off
    draw_stack_at(BAR_POS, "white")
    draw_stack_at(BAR_POS, "black")
    draw_stack_at(OFF_POS, "white")
    draw_stack_at(OFF_POS, "black")


def draw_dice_and_hud(surface, rect, game: BackgammonGame, font, small, hint_msg: Optional[str]):
    pygame.draw.rect(surface, COL_BG, (rect.left, rect.top, rect.width, HUD_H))
    st = game.state()
    turn = getattr(st, "current_color", "white")
    dice_vals = getattr(st, "dice_values", [])
    moves_left = getattr(st, "moves_left", 0)

    label = f"Turno: {turn} | Dados: {tuple(dice_vals) if dice_vals else '—'} (movs: {moves_left})"
    txt = font.render(label, True, COL_TEXT)
    surface.blit(txt, (rect.left + 12, rect.top + 12))

    help_line = "R: roll  |  1-6: move desde seleccionado  |  Click: seleccionar  |  H: hint  |  E: end  |  S: save  |  ESC: salir"
    txt2 = small.render(help_line, True, (210, 210, 210))
    surface.blit(txt2, (rect.left + 12, rect.top + 46))

    # Dados (dos casillas)
    die_w = 54
    dpad = 10
    x0 = rect.right - (die_w * 2 + dpad) - 16
    y0 = rect.top + 12
    for i in range(2):
        r = pygame.Rect(x0 + i * (die_w + dpad), y0, die_w, die_w)
        pygame.draw.rect(surface, (220, 220, 220), r, border_radius=6)
        val = dice_vals[i] if (dice_vals and len(dice_vals) > i) else None
        t = font.render(str(val) if val else "-", True, (10, 10, 10))
        surface.blit(t, (r.centerx - t.get_width() // 2, r.centery - t.get_height() // 2))

    # Overlay de hint
    if hint_msg:
        pad = 12
        lines = []
        chunk = hint_msg
        if len(chunk) > 90:
            mid = len(chunk) // 2
            lines = [chunk[:mid], chunk[mid:]]
        else:
            lines = [chunk]
        h = 28 * len(lines) + 2 * pad
        w = max(font.size(s)[0] for s in lines) + 2 * pad
        box = pygame.Rect(rect.centerx - w // 2, rect.top + HUD_H + 10, w, h)
        pygame.draw.rect(surface, COL_HINT, box, border_radius=8)
        pygame.draw.rect(surface, (60, 55, 20), box, width=2, border_radius=8)
        y = box.top + pad
        for s in lines:
            t = font.render(s, True, (40, 40, 20))
            surface.blit(t, (box.left + pad, y))
            y += 28


def screen_to_point(mx, my, positions, bar_rect, off_rect) -> Optional[int]:
    # Click en bar/off?
    if bar_rect.collidepoint(mx, my):
        return BAR_POS
    if off_rect.collidepoint(mx, my):
        return OFF_POS
    # Buscar el punto por columna
    for pt, (cx, _is_top, area) in positions.items():
        col_rect = pygame.Rect(cx - 30, area.top, 60, area.height)
        if col_rect.collidepoint(mx, my):
            return pt
    return None


def try_move(game: BackgammonGame, from_pos: int, steps: int) -> str:
    """Ejecutar un movimiento y devolver mensaje corto."""
    try:
        game.apply_player_move(from_pos, steps)
        st = game.state()
        return f"OK: move {from_pos} {steps}. Dados: {tuple(getattr(st, 'dice_values', []))} (movs: {getattr(st, 'moves_left', 0)})"
    except (InvalidMoveException, NoMovesAvailableException) as ex:
        return f"Movimiento inválido: {ex}"
    except DiceNotRolledException as ex:
        return str(ex)
    except BackgammonException as ex:
        return str(ex)
    except Exception as ex:  # fallback defensivo
        return str(ex)


def main():
    pygame.init()
    pygame.display.set_caption("Backgammon – Pygame MVP")
    screen = pygame.display.set_mode((W, H))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 22)
    small = pygame.font.SysFont("arial", 18)

    game = init_game()
    root_rect = pygame.Rect(0, 0, W, H)
    positions, bar_rect, off_rect = build_point_layout(root_rect)

    selected_from: Optional[int] = None
    last_msg: Optional[str] = None
    hint_overlay: Optional[str] = None

    running = True
    while running:
        _dt = clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False

                elif ev.key == pygame.K_r:
                    # roll / start_turn
                    try:
                        game.start_turn()
                        st = game.state()
                        last_msg = f"Turno {getattr(st, 'current_color', 'white')} – Dados: {tuple(getattr(st, 'dice_values', []))}"
                        hint_overlay = None
                    except BackgammonException as ex:
                        last_msg = str(ex)

                elif ev.key == pygame.K_h:
                    # hint
                    try:
                        hint_overlay = suggest_move(game)
                        last_msg = "Sugerencia generada."
                    except Exception as ex:
                        hint_overlay = None
                        last_msg = str(ex)

                elif ev.key == pygame.K_e:
                    # end turn
                    try:
                        game.end_turn()
                        st = game.state()
                        last_msg = f"Turno finalizado. Ahora {getattr(st, 'current_color', 'white')}."
                        hint_overlay = None
                    except BackgammonException as ex:
                        last_msg = str(ex)

                elif ev.key == pygame.K_s:
                    # save snapshot.json
                    import json
                    from dataclasses import asdict, is_dataclass
                    st = game.state()

                    def _to_dict(obj):
                        if is_dataclass(obj):
                            return asdict(obj)
                        if isinstance(obj, (list, tuple)):
                            return list(obj)
                        if hasattr(obj, "__dict__"):
                            return dict(vars(obj))
                        return obj

                    payload = {"state": _to_dict(st)}
                    result = getattr(game, "result", None)
                    if result is not None:
                        payload["result"] = _to_dict(result)
                    with open("snapshot.json", "w", encoding="utf-8") as f:
                        json.dump(payload, f, ensure_ascii=False, indent=2)
                    last_msg = "Partida guardada en snapshot.json"

                elif pygame.K_1 <= ev.key <= pygame.K_6:
                    # intentar mover
                    steps = ev.key - pygame.K_0
                    if selected_from is None:
                        last_msg = "Seleccioná primero un punto de origen con el mouse."
                    else:
                        last_msg = try_move(game, selected_from, steps)
                        hint_overlay = None

            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my = ev.pos
                pt = screen_to_point(mx, my, positions, bar_rect, off_rect)
                if pt is not None:
                    selected_from = pt
                    last_msg = f"Origen seleccionado: {('BAR' if pt == BAR_POS else ('OFF' if pt == OFF_POS else pt))}"

        # Dibujo
        screen.fill(COL_BG)
        draw_board(screen, root_rect, positions, bar_rect, off_rect, selected_from, font)
        draw_checkers(screen, positions, bar_rect, off_rect, game.board)
        draw_dice_and_hud(screen, root_rect, game, font, small, hint_overlay)

        # Mensaje de estado
        if last_msg:
            t = small.render(last_msg, True, (220, 220, 220))
            screen.blit(t, (MARGIN, H - t.get_height() - 8))

        # Game over overlay (suave)
        if getattr(game, "game_over", False):
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))
            msg = "¡Juego terminado!"
            if getattr(game, "result", None):
                r = game.result
                msg = f"Ganó {getattr(r, 'winner_color', 'white')} – {getattr(r, 'outcome', '')} ({getattr(r, 'points', 0)} pts)"
            t = font.render(msg, True, (255, 240, 160))
            screen.blit(t, (W // 2 - t.get_width() // 2, H // 2 - t.get_height() // 2))

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
