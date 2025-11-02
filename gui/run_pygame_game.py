# -*- coding: utf-8 -*-
"""
Backgammon – Pygame MVP con interacción de mouse
------------------------------------------------
- Tablero con 24 puntos, BAR y OFF.
- Render de fichas por color leyendo el Board (count_at / fallbacks).
- HUD con dados, turno y ayuda.
- Interacciones:
    * R: roll/start_turn
    * H: hint (si existe cli.hint_engine.suggest_move)
    * E: end_turn
    * S: save snapshot.json
    * Click izquierdo: seleccionar punto "from" (solo si hay ficha propia)
    * Drag & drop: al soltar, aplica automáticamente la mejor jugada legal
      (prioriza dado más alto si corresponde)
    * Tecla 1..6: mover "from" con steps (si los dados lo permiten)
    * ESC / cerrar: salir

Requiere:
    - core.board.Board
    - core.dice.Dice
    - core.player.Player
    - core.game.BackgammonGame
"""

from __future__ import annotations

import sys
from typing import Optional, Tuple, List

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

# hint opcional
try:
    from cli.hint_engine import suggest_move  # type: ignore
except Exception:
    def suggest_move(_game: BackgammonGame) -> str:
        return "Hint no disponible."

# ----------- Config visual -----------
W, H = 1100, 700
MARGIN = 20
BOARD_W, BOARD_H = W - 2 * MARGIN, H - 2 * MARGIN
BAR_W = 60
OFF_W = 80
POINTS_PER_SIDE = 12

COL_BG   = (22, 24, 29)
COL_BOARD= (198, 164, 110)
COL_TRI_A= (184, 146, 94)
COL_TRI_B= (225, 201, 158)
COL_BAR  = (60, 62, 68)
COL_OFF  = (60, 62, 68)
COL_TEXT = (240, 240, 240)
COL_HINT = (255, 240, 150)
COL_WHITE= (245, 245, 245)
COL_BLACK= (30, 32, 36)
COL_EDGEW= (200, 200, 200)
COL_EDGEB= (65, 68, 73)
COL_SELECT = (160, 210, 255)

FPS = 60
HUD_H = 90

# Parámetros fichas
CHECKER_RADIUS = 16
STACK_SPACING  = 4
MAX_STACK_RENDER = 5  # si hay más, se muestra +n

# Mapeos de posiciones:
# - Puntos 1..24
# - BAR = 0, OFF = 25
BAR_POS = 0
OFF_POS = 25


# ------------- Helpers robustos de acceso al Board -------------
def count_at(board: Board, point: int, color: str) -> int:
    """Cuenta fichas en 'point' de 'color'. Intenta API conocida y cae a fallbacks."""
    # API ideal
    if hasattr(board, "count_at"):
        try:
            return int(board.count_at(point, color))
        except Exception:
            pass

    # OFF/BAR como ubicaciones especiales
    if point == OFF_POS:
        for name in ("count_off", "get_off_count", "off_count", "get_off"):
            if hasattr(board, name):
                try:
                    return int(getattr(board, name)(color))
                except Exception:
                    pass
    if point == BAR_POS:
        for name in ("count_bar", "get_bar_count", "bar_count", "get_bar"):
            if hasattr(board, name):
                try:
                    return int(getattr(board, name)(color))
                except Exception:
                    pass

    # Puntos comunes
    for name in ("count_point", "get_count_at", "point_count", "count", "get_count"):
        if hasattr(board, name):
            fn = getattr(board, name)
            try:
                return int(fn(point, color))
            except TypeError:
                try:
                    return int(fn(color, point))
                except Exception:
                    continue
            except Exception:
                continue

    # Fallback via get_point()
    if hasattr(board, "get_point"):
        try:
            arr = board.get_point(point)
            return sum(1 for ch in arr if getattr(ch, "get_color", lambda: None)() == color)
        except Exception:
            pass

    return 0


def count_bar(board: Board, color: str) -> int:
    if hasattr(board, "count_bar"):
        try:
            return int(board.count_bar(color))
        except Exception:
            pass
    if hasattr(board, "get_checkers_in_bar"):
        try:
            return len(board.get_checkers_in_bar(color))
        except Exception:
            pass
    return count_at(board, BAR_POS, color)


def count_off(board: Board, color: str) -> int:
    if hasattr(board, "count_off"):
        try:
            return int(board.count_off(color))
        except Exception:
            pass
    return count_at(board, OFF_POS, color)


# ------------- Layout del tablero -------------
def build_point_layout(rect: pygame.Rect) -> Tuple[dict, pygame.Rect, pygame.Rect]:
    """
    Devuelve:
      - positions: {point_index: (center_x, is_top, half_rect)}
      - bar_rect: rect del BAR
      - off_rect: rect del OFF
    """
    board_rect = pygame.Rect(rect.left, rect.top + HUD_H, rect.width, rect.height - HUD_H)

    total_w = board_rect.width - OFF_W
    panel_rect = pygame.Rect(board_rect.left, board_rect.top, total_w, board_rect.height)
    off_rect = pygame.Rect(board_rect.right - OFF_W, board_rect.top, OFF_W, board_rect.height)

    bar_rect = pygame.Rect(0, 0, BAR_W, panel_rect.height)
    points_area_w = panel_rect.width - BAR_W
    col_w = points_area_w // POINTS_PER_SIDE

    cols_left = POINTS_PER_SIDE // 2  # 6
    cols_right = POINTS_PER_SIDE // 2 # 6

    x0 = panel_rect.left
    xs_left  = [x0 + i * col_w for i in range(cols_left)]
    x_bar    = x0 + cols_left * col_w
    xs_right = [x_bar + BAR_W + i * col_w for i in range(cols_right)]
    bar_rect.topleft = (x_bar, panel_rect.top)

    positions = {}

    half_h = panel_rect.height // 2
    top_rect = pygame.Rect(panel_rect.left, panel_rect.top, panel_rect.width, half_h)
    bot_rect = pygame.Rect(panel_rect.left, panel_rect.top + half_h, panel_rect.width, half_h)

    # Abajo 1..12 (derecha a izquierda)
    x_cols_bottom = list(reversed(xs_left + xs_right))
    # Arriba 13..24 (derecha a izquierda)
    x_cols_top = list(reversed(xs_left + xs_right))

    for i in range(POINTS_PER_SIDE):
        pt_idx_bottom = i + 1
        cx_b = x_cols_bottom[i] + col_w // 2
        positions[pt_idx_bottom] = (cx_b, False, bot_rect)

        pt_idx_top = i + 13
        cx_t = x_cols_top[i] + col_w // 2
        positions[pt_idx_top] = (cx_t, True, top_rect)

    bar_rect = pygame.Rect(x_bar, panel_rect.top, BAR_W, panel_rect.height)
    return positions, bar_rect, off_rect


# ------------- Dibujo de tablero, fichas y HUD -------------
def draw_board(surface, rect, positions, bar_rect, off_rect, selected_from: Optional[int], font):
    pygame.draw.rect(surface, COL_BOARD, rect, border_radius=12)

    half_h = (rect.height - HUD_H) // 2
    top = pygame.Rect(rect.left, rect.top + HUD_H, rect.width, half_h)
    bottom = pygame.Rect(rect.left, rect.top + HUD_H + half_h, rect.width, half_h)

    pygame.draw.rect(surface, COL_BAR, bar_rect)
    pygame.draw.rect(surface, COL_OFF, off_rect)

    used_xs_top = []
    used_xs_bottom = []
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
                p1 = (cx, top.bottom)
                p2 = (cx - 30, top.top)
                p3 = (cx + 30, top.top)
            else:
                p1 = (cx, bottom.top)
                p2 = (cx - 30, bottom.bottom)
                p3 = (cx + 30, bottom.bottom)
            pygame.draw.polygon(surface, color, [p1, p2, p3])

    draw_triangles(used_xs_top, True)
    draw_triangles(used_xs_bottom, False)

    # Selección
    highlight = None
    if selected_from is not None:
        if selected_from in positions:
            cx, _, area = positions[selected_from]
            highlight = pygame.Rect(cx - 34, area.top, 68, area.height)
        elif selected_from == BAR_POS:
            highlight = bar_rect.inflate(-6, -6)
        elif selected_from == OFF_POS:
            highlight = off_rect.inflate(-6, -6)
    if highlight:
        pygame.draw.rect(surface, COL_SELECT, highlight, width=3, border_radius=6)

    # Etiquetas
    txt = font.render("BAR", True, COL_TEXT)
    surface.blit(txt, (bar_rect.centerx - txt.get_width() // 2, bar_rect.top + 6))
    txt2 = font.render("OFF", True, COL_TEXT)
    surface.blit(txt2, (off_rect.centerx - txt2.get_width() // 2, off_rect.top + 6))


def _draw_checker(surface, center, fill, edge):
    x, y = center
    pygame.draw.circle(surface, fill, (int(x), int(y)), CHECKER_RADIUS)
    pygame.draw.circle(surface, edge, (int(x), int(y)), CHECKER_RADIUS, 2)


def draw_checkers(surface, positions, bar_rect, off_rect, board: Board):
    def draw_stack_at(point, color):
        cnt = count_at(board, point, color)
        if cnt <= 0:
            return
        if point in positions:
            cx, is_top, area = positions[point]
            for i in range(min(cnt, MAX_STACK_RENDER)):
                if is_top:
                    cy = area.bottom - (CHECKER_RADIUS + i * (2 * CHECKER_RADIUS + STACK_SPACING))
                else:
                    cy = area.top + (CHECKER_RADIUS + i * (2 * CHECKER_RADIUS + STACK_SPACING))
                fill = COL_WHITE if color == "white" else COL_BLACK
                edge = COL_EDGEW if color == "white" else COL_EDGEB
                _draw_checker(surface, (cx, cy), fill, edge)
        elif point == BAR_POS:
            cx = bar_rect.centerx
            top = bar_rect.top + 40
            for i in range(min(cnt, MAX_STACK_RENDER)):
                cy = top + i * (2 * CHECKER_RADIUS + STACK_SPACING)
                fill = COL_WHITE if color == "white" else COL_BLACK
                edge = COL_EDGEW if color == "white" else COL_EDGEB
                _draw_checker(surface, (cx, cy), fill, edge)
        elif point == OFF_POS:
            cx = off_rect.centerx
            top = off_rect.top + 40
            for i in range(min(cnt, MAX_STACK_RENDER)):
                cy = top + i * (2 * CHECKER_RADIUS + STACK_SPACING)
                fill = COL_WHITE if color == "white" else COL_BLACK
                edge = COL_EDGEW if color == "white" else COL_EDGEB
                _draw_checker(surface, (cx, cy), fill, edge)

    for pt in range(1, 25):
        draw_stack_at(pt, "white")
        draw_stack_at(pt, "black")
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

    help_line = "R: roll  |  1-6: mover desde seleccionado  |  Click/Drag: seleccionar/mover  |  H: hint  |  E: end  |  S: save  |  ESC: salir"
    txt2 = small.render(help_line, True, (210, 210, 210))
    surface.blit(txt2, (rect.left + 12, rect.top + 46))

    # Dados como cajitas simples (display de 2 valores)
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

    # Overlay de hint si existe
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


# ------------- Picking y movimientos -------------
def screen_to_point(mx, my, positions, bar_rect, off_rect) -> Optional[int]:
    if bar_rect.collidepoint(mx, my):
        return BAR_POS
    if off_rect.collidepoint(mx, my):
        return OFF_POS
    for pt, (cx, _, area) in positions.items():
        col_rect = pygame.Rect(cx - 30, area.top, 60, area.height)
        if col_rect.collidepoint(mx, my):
            return pt
    return None


def try_move(game: BackgammonGame, from_pos: int, steps: int) -> str:
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
    except Exception as ex:
        return str(ex)


def _own_checker_on(board: Board, point: int, color: str) -> bool:
    try:
        return (count_at(board, point, color) or 0) > 0
    except Exception:
        return False


def _get_available_moves(game: BackgammonGame) -> List[int]:
    """Robusto acceso a dados disponibles."""
    if hasattr(game, "_get_available_moves"):
        try:
            return list(getattr(game, "_get_available_moves")())
        except Exception:
            pass
    am = getattr(game.dice, "available_moves", None)
    if callable(am):
        try:
            return list(am()) or []
        except Exception:
            return []
    if isinstance(am, (list, tuple)):
        return list(am)
    return []


def _legal_steps_from(game: BackgammonGame, from_pos: int) -> List[int]:
    """
    Devuelve qué valores de dado (steps) son LEGALES desde 'from_pos' para el color actual.
    No muta el estado. Tolera boards sin todos los validadores (hace best-effort).
    """
    color = game.current_color
    dice_vals = _get_available_moves(game)
    if not dice_vals:
        return []

    # ¿Hay fichas en BAR?
    try:
        has_bar = bool(game.board.get_checkers_in_bar(color))
    except Exception:
        try:
            has_bar = (getattr(game.board, "count_at", lambda p, c: 0)(BAR_POS, color) > 0)
        except Exception:
            has_bar = False

    legal: List[int] = []
    for steps in sorted(set(dice_vals)):
        try:
            if has_bar and from_pos != BAR_POS:
                continue
            # Reingreso
            if from_pos == BAR_POS and hasattr(game.board, "validate_reentry"):
                game.board.validate_reentry(color, steps)
                legal.append(steps)
                continue
            # Movimiento básico
            if hasattr(game.board, "validate_basic_move"):
                game.board.validate_basic_move(color, from_pos, steps)
                legal.append(steps)
                continue
            # Bearing off
            if hasattr(game.board, "can_bear_off_from") and game.board.can_bear_off_from(color, from_pos, steps):
                legal.append(steps)
                continue
            # Último recurso: permitimos el intento y que falle en apply si no corresponde
            legal.append(steps)
        except Exception:
            pass

    return sorted(legal)


def draw_legal_badges(surface, font_small, positions, selected_from: int, legal_steps: List[int]):
    """Burbujas sobre el punto seleccionado con steps legales. Rojo si no hay jugadas."""
    if selected_from not in positions:
        return
    cx, is_top, area = positions[selected_from]
    y = area.top + 8 if is_top else area.bottom - 28

    if not legal_steps:
        msg = "sin jugada"
        t = font_small.render(msg, True, (255, 255, 255))
        box = pygame.Rect(0, 0, t.get_width() + 12, t.get_height() + 8)
        box.center = (cx, y)
        pygame.draw.rect(surface, (180, 40, 40), box, border_radius=10)
        surface.blit(t, (box.left + 6, box.top + 4))
        return

    gap = 8
    w = sum(font_small.size(str(v))[0] + 16 for v in legal_steps) + gap * (len(legal_steps) - 1)
    x = cx - w // 2
    for v in legal_steps:
        label = str(v)
        t = font_small.render(label, True, (20, 20, 20))
        bw = t.get_width() + 16
        box = pygame.Rect(x, 0, bw, t.get_height() + 8)
        box.centery = y
        pygame.draw.rect(surface, (160, 215, 120), box, border_radius=12)         # verde suave
        pygame.draw.rect(surface, (30, 80, 30), box, width=2, border_radius=12)   # borde
        surface.blit(t, (box.left + 8, box.top + 4))
        x += bw + gap


# ------------- Inicialización de juego -------------
def init_game() -> BackgammonGame:
    board = Board()
    dice = Dice()
    white = Player("White", "white")
    black = Player("Black", "black")
    game = BackgammonGame(board, dice, (white, black), starting_color=white.color)
    return game


# ------------- Main loop -------------
def main():
    pygame.init()
    pygame.display.set_caption("Backgammon – Pygame")
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

    # estado de drag
    dragging: bool = False
    drag_from: Optional[int] = None
    mouse_x = mouse_y = 0

    running = True
    while running:
        dt = clock.tick(FPS)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                elif ev.key == pygame.K_r:
                    try:
                        game.start_turn()
                        st = game.state()
                        last_msg = f"Turno {getattr(st, 'current_color', 'white')} – Dados: {tuple(getattr(st, 'dice_values', []))}"
                        hint_overlay = None
                    except BackgammonException as ex:
                        last_msg = str(ex)
                elif ev.key == pygame.K_h:
                    try:
                        hint_overlay = suggest_move(game)
                        last_msg = "Sugerencia generada."
                    except Exception as ex:
                        hint_overlay = None
                        last_msg = str(ex)
                elif ev.key == pygame.K_e:
                    try:
                        game.end_turn()
                        st = game.state()
                        last_msg = f"Turno finalizado. Ahora {getattr(st, 'current_color', 'white')}."
                        hint_overlay = None
                    except BackgammonException as ex:
                        last_msg = str(ex)
                elif ev.key == pygame.K_s:
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
                    steps = ev.key - pygame.K_0
                    if selected_from is None:
                        last_msg = "Seleccioná primero un punto de origen con el mouse."
                    else:
                        last_msg = try_move(game, selected_from, steps)
                        hint_overlay = None

            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my = ev.pos
                mouse_x, mouse_y = mx, my
                pt = screen_to_point(mx, my, positions, bar_rect, off_rect)
                if pt is not None:
                    # solo seleccionar si hay ficha propia (o si clickeás BAR/OFF)
                    if _own_checker_on(game.board, pt, game.current_color) or (pt in (BAR_POS, OFF_POS)):
                        selected_from = pt
                        last_msg = f"Origen seleccionado: {('BAR' if pt == BAR_POS else ('OFF' if pt == OFF_POS else pt))}"
                        # iniciar drag
                        dragging = True
                        drag_from = pt
                    else:
                        selected_from = pt
                        last_msg = "Punto sin fichas propias."

            elif ev.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = ev.pos

            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                if dragging and drag_from is not None:
                    legal = _legal_steps_from(game, drag_from)
                    if not legal:
                        last_msg = "No hay jugadas disponibles desde ese punto."
                    else:
                        # Si hay varias, elegimos el dado más alto (regla común).
                        chosen = max(legal)
                        last_msg = try_move(game, drag_from, chosen)
                        hint_overlay = None
                    dragging = False
                    drag_from = None

        # Dibujo
        screen.fill(COL_BG)
        draw_board(screen, root_rect, positions, bar_rect, off_rect, selected_from, font)
        draw_checkers(screen, positions, bar_rect, off_rect, game.board)
        draw_dice_and_hud(screen, root_rect, game, font, small, hint_overlay)

        # Badges de validación
        font_badge = pygame.font.SysFont("arial", 16)
        if selected_from is not None:
            legal = _legal_steps_from(game, selected_from)
            draw_legal_badges(screen, font_badge, positions, selected_from, legal)

        # Ghost de drag
        if dragging and drag_from is not None:
            fill = COL_WHITE if game.current_color == "white" else COL_BLACK
            edge = COL_EDGEW if game.current_color == "white" else COL_EDGEB
            pygame.draw.circle(screen, fill, (mouse_x, mouse_y), CHECKER_RADIUS)
            pygame.draw.circle(screen, edge, (mouse_x, mouse_y), CHECKER_RADIUS, 2)

        # Mensaje de estado
        if last_msg:
            t = small.render(last_msg, True, (220, 220, 220))
            screen.blit(t, (MARGIN, H - t.get_height() - 8))

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
