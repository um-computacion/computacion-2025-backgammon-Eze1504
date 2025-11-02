# -*- coding: utf-8 -*-
"""
Backgammon – Pygame UI completa
--------------------------------
- Tablero con 24 puntos, BAR y OFF.
- Render de fichas (white/black), HUD con dados animados, indicador de turno, mensajes de estado.
- Interacciones:
    * Botones (HUD): New Game, Roll, End Turn, Hint, Save, Quit
    * Click en dados o botón Roll: animar tirada y, al finalizar, start_turn()
    * Click izquierdo: seleccionar punto "from" (solo si hay ficha propia)
    * Drag & drop: al soltar, aplica una jugada legal (prioriza dado más alto)
    * Teclas: R (roll), H (hint), E (end), S (save), 1..6 (mover), ESC (salir)
"""

from __future__ import annotations

import sys
import time
import random
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

COL_BG     = (22, 24, 29)
COL_BOARD  = (198, 164, 110)
COL_TRI_A  = (184, 146, 94)
COL_TRI_B  = (225, 201, 158)
COL_BAR    = (60, 62, 68)
COL_OFF    = (60, 62, 68)
COL_TEXT   = (240, 240, 240)
COL_HINT   = (255, 240, 150)
COL_WHITE  = (245, 245, 245)
COL_BLACK  = (30, 32, 36)
COL_EDGEW  = (200, 200, 200)
COL_EDGEB  = (65, 68, 73)
COL_SELECT = (160, 210, 255)

# Dados
COL_DIE_FACE   = (245, 245, 245)
COL_DIE_EDGE   = (205, 205, 205)
COL_DIE_DOT    = (35, 35, 35)
COL_DIE_SHADOW = (0, 0, 0, 60)

# Botones
BTN_BG     = (50, 54, 62)
BTN_EDGE   = (95, 99, 108)
BTN_HOVER  = (70, 74, 83)
BTN_TEXT   = (235, 235, 235)
BTN_DISABLE= (90, 92, 98)

FPS = 60
HUD_H = 100  # un poquito más alto para botones

# Parámetros fichas
CHECKER_RADIUS = 16
STACK_SPACING  = 4
MAX_STACK_RENDER = 5

# Posiciones especiales
BAR_POS = 0
OFF_POS = 25


# ------------- Helpers robustos de acceso al Board -------------
def count_at(board: Board, point: int, color: str) -> int:
    if hasattr(board, "count_at"):
        try:
            return int(board.count_at(point, color))
        except Exception:
            pass
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
def build_point_layout(rect: pygame.Rect):
    board_rect = pygame.Rect(rect.left, rect.top + HUD_H, rect.width, rect.height - HUD_H)

    total_w = board_rect.width - OFF_W
    panel_rect = pygame.Rect(board_rect.left, board_rect.top, total_w, board_rect.height)
    off_rect = pygame.Rect(board_rect.right - OFF_W, board_rect.top, OFF_W, board_rect.height)

    bar_rect = pygame.Rect(0, 0, BAR_W, panel_rect.height)
    points_area_w = panel_rect.width - BAR_W
    col_w = points_area_w // POINTS_PER_SIDE

    cols_left = POINTS_PER_SIDE // 2
    cols_right = POINTS_PER_SIDE // 2

    x0 = panel_rect.left
    xs_left  = [x0 + i * col_w for i in range(cols_left)]
    x_bar    = x0 + cols_left * col_w
    xs_right = [x_bar + BAR_W + i * col_w for i in range(cols_right)]
    bar_rect.topleft = (x_bar, panel_rect.top)

    positions = {}

    half_h = panel_rect.height // 2
    top_rect = pygame.Rect(panel_rect.left, panel_rect.top, panel_rect.width, half_h)
    bot_rect = pygame.Rect(panel_rect.left, panel_rect.top + half_h, panel_rect.width, half_h)

    x_cols_bottom = list(reversed(xs_left + xs_right))
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


# ------------- Dibujo base -------------
def draw_board(surface, rect, positions, bar_rect, off_rect, selected_from: Optional[int], font):
    pygame.draw.rect(surface, COL_BOARD, rect, border_radius=12)

    half_h = (rect.height - HUD_H) // 2
    top = pygame.Rect(rect.left, rect.top + HUD_H, rect.width, half_h)
    bottom = pygame.Rect(rect.left, rect.top + HUD_H + half_h, rect.width, half_h)

    pygame.draw.rect(surface, COL_BAR, bar_rect)
    pygame.draw.rect(surface, COL_OFF, off_rect)

    used_xs_top = sorted([positions[pt][0] for pt in range(13, 25)])
    used_xs_bottom = sorted([positions[pt][0] for pt in range(1, 13)])

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

    # Selección (resalta la columna)
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


# ------------- HUD + Dados + Botones -------------
class DiceAnimator:
    """Controla animación de tirada antes de llamar a start_turn()."""
    def __init__(self, duration_ms: int = 600):
        self.duration = duration_ms
        self.running = False
        self.start_t = 0.0
        self.preview = (None, None)  # caras temporales

    def start(self):
        self.running = True
        self.start_t = time.time()
        self.preview = (random.randint(1, 6), random.randint(1, 6))

    def update(self):
        if not self.running:
            return
        elapsed = (time.time() - self.start_t) * 1000.0
        if elapsed >= self.duration:
            self.running = False
        else:
            # velocidad de cambio decreciente (ease-out)
            step_ms = max(40, 200 - int(160 * (elapsed / self.duration)))
            if int(elapsed) % step_ms < 20:
                self.preview = (random.randint(1, 6), random.randint(1, 6))

    def faces(self) -> Tuple[Optional[int], Optional[int]]:
        return self.preview


def draw_die(surface: pygame.Surface, rect: pygame.Rect, value: Optional[int]):
    # sombra
    shadow = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shadow, COL_DIE_SHADOW, shadow.get_rect(), border_radius=8)
    surface.blit(shadow, (rect.x + 2, rect.y + 3))

    pygame.draw.rect(surface, COL_DIE_FACE, rect, border_radius=10)
    pygame.draw.rect(surface, COL_DIE_EDGE, rect, width=2, border_radius=10)

    if not value:
        cx, cy = rect.center
        w = rect.width * 0.4
        pygame.draw.line(surface, COL_DIE_DOT, (cx - w/2, cy), (cx + w/2, cy), width=3)
        return

    cx, cy = rect.center
    off = rect.width * 0.22
    dots = {
        1: [(cx, cy)],
        2: [(cx - off, cy - off), (cx + off, cy + off)],
        3: [(cx - off, cy - off), (cx, cy), (cx + off, cy + off)],
        4: [(cx - off, cy - off), (cx + off, cy - off), (cx - off, cy + off), (cx + off, cy + off)],
        5: [(cx - off, cy - off), (cx + off, cy - off), (cx, cy), (cx - off, cy + off), (cx + off, cy + off)],
        6: [(cx - off, cy - off), (cx + off, cy - off), (cx - off, cy), (cx + off, cy),
            (cx - off, cy + off), (cx + off, cy + off)],
    }
    r = int(rect.width * 0.09)
    for (x, y) in dots[int(value)]:
        pygame.draw.circle(surface, COL_DIE_DOT, (int(x), int(y)), r)


class Button:
    def __init__(self, rect: pygame.Rect, label: str, action: str):
        self.rect = rect
        self.label = label
        self.action = action
        self.hover = False
        self.disabled = False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        bg = BTN_DISABLE if self.disabled else (BTN_HOVER if self.hover else BTN_BG)
        pygame.draw.rect(surface, bg, self.rect, border_radius=8)
        pygame.draw.rect(surface, BTN_EDGE, self.rect, width=2, border_radius=8)
        t = font.render(self.label, True, BTN_TEXT if not self.disabled else (200, 200, 200))
        surface.blit(t, (self.rect.centerx - t.get_width() // 2, self.rect.centery - t.get_height() // 2))

    def handle_event(self, ev: pygame.event.Event) -> Optional[str]:
        if self.disabled:
            return None
        if ev.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(ev.pos)
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.rect.collidepoint(ev.pos):
                return self.action
        return None


def draw_turn_indicator(surface, area: pygame.Rect, game: BackgammonGame, font: pygame.font.Font):
    """Muestra el color del turno con un chip y texto."""
    st = game.state()
    color = getattr(st, "current_color", "white")
    chip_color = COL_WHITE if color == "white" else COL_BLACK
    chip_edge  = COL_EDGEW if color == "white" else COL_EDGEB
    cx = area.left + 16 + CHECKER_RADIUS
    cy = area.top + HUD_H // 2
    pygame.draw.circle(surface, chip_color, (cx, cy), CHECKER_RADIUS + 2)
    pygame.draw.circle(surface, chip_edge, (cx, cy), CHECKER_RADIUS + 2, 2)
    label = f"Turno: {color}"
    t = font.render(label, True, COL_TEXT)
    surface.blit(t, (cx + CHECKER_RADIUS + 10, cy - t.get_height() // 2))


def draw_dice_and_hud(surface, rect, game: BackgammonGame, font, small,
                      hint_msg: Optional[str],
                      die_rects: Tuple[pygame.Rect, pygame.Rect],
                      anim: DiceAnimator,
                      buttons: List[Button]):
    # barra HUD
    hud_rect = pygame.Rect(rect.left, rect.top, rect.width, HUD_H)
    pygame.draw.rect(surface, COL_BG, hud_rect)

    # Indicador de turno
    turn_area = pygame.Rect(hud_rect.left + 10, hud_rect.top, 250, HUD_H)
    draw_turn_indicator(surface, turn_area, game, font)

    # Línea de ayuda
    help_line = "Click/Drag: mover | 1-6: paso | H: hint | E: end | S: save | ESC: salir"
    txt2 = small.render(help_line, True, (210, 210, 210))
    surface.blit(txt2, (turn_area.left, hud_rect.bottom - txt2.get_height() - 8))

    # Dados
    r1, r2 = die_rects
    st = game.state()
    dice_vals = list(getattr(st, "dice_values", []))
    while len(dice_vals) < 2:
        dice_vals.append(None)

    if anim.running:
        f1, f2 = anim.faces()
        draw_die(surface, r1, f1)
        draw_die(surface, r2, f2)
    else:
        draw_die(surface, r1, dice_vals[0])
        draw_die(surface, r2, dice_vals[1])

    # Botones
    for b in buttons:
        b.draw(surface, small)

    # Overlay hint
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
    color = game.current_color
    dice_vals = _get_available_moves(game)
    if not dice_vals:
        return []
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
            if from_pos == BAR_POS and hasattr(game.board, "validate_reentry"):
                game.board.validate_reentry(color, steps)
                legal.append(steps)
                continue
            if hasattr(game.board, "validate_basic_move"):
                game.board.validate_basic_move(color, from_pos, steps)
                legal.append(steps)
                continue
            if hasattr(game.board, "can_bear_off_from") and game.board.can_bear_off_from(color, from_pos, steps):
                legal.append(steps)
                continue
            legal.append(steps)
        except Exception:
            pass
    return sorted(legal)


def draw_legal_badges(surface, font_small, positions, selected_from: int, legal_steps: List[int]):
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
        pygame.draw.rect(surface, (160, 215, 120), box, border_radius=12)
        pygame.draw.rect(surface, (30, 80, 30), box, width=2, border_radius=12)
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

    # Dados (HUD derecha)
    die_w = 60
    dpad = 12
    dice_x0 = root_rect.right - (die_w * 2 + dpad) - 20
    dice_y0 = root_rect.top + 16
    die_rects = (
        pygame.Rect(dice_x0, dice_y0, die_w, die_w),
        pygame.Rect(dice_x0 + die_w + dpad, dice_y0, die_w, die_w),
    )

    # Botones (HUD centro-derecha)
    btn_font = small
    btn_w, btn_h, btn_gap = 110, 30, 8
    btn_y = root_rect.top + 60
    btn_labels = [("New Game", "new"), ("Roll", "roll"), ("End Turn", "end"),
                  ("Hint", "hint"), ("Save", "save"), ("Quit", "quit")]
    buttons: List[Button] = []
    bx = dice_x0 - (btn_w + btn_gap) * len(btn_labels) - 20
    for label, action in btn_labels:
        r = pygame.Rect(bx, btn_y, btn_w, btn_h)
        buttons.append(Button(r, label, action))
        bx += btn_w + btn_gap

    # Animador de dados
    anim = DiceAnimator(duration_ms=600)
    pending_roll = False

    running = True
    while running:
        dt = clock.tick(FPS)

        # actualizar animación
        if anim.running:
            anim.update()
            if not anim.running and pending_roll:
                try:
                    game.start_turn()
                    st = game.state()
                    last_msg = f"Turno {getattr(st, 'current_color', 'white')} – Dados: {tuple(getattr(st, 'dice_values', []))}"
                except BackgammonException as ex:
                    last_msg = str(ex)
                pending_roll = False

        # Update hover de botones por defecto
        mx, my = pygame.mouse.get_pos()
        for b in buttons:
            b.hover = b.rect.collidepoint(mx, my)

        for ev in pygame.event.get():
            # Botones
            for b in buttons:
                action = b.handle_event(ev)
                if action:
                    if action == "new":
                        game = init_game()
                        selected_from = None
                        dragging = False
                        drag_from = None
                        hint_overlay = None
                        last_msg = "Nueva partida."
                    elif action == "roll":
                        if not anim.running:
                            anim.start()
                            pending_roll = True
                            hint_overlay = None
                    elif action == "end":
                        try:
                            game.end_turn()
                            st = game.state()
                            last_msg = f"Turno finalizado. Ahora {getattr(st, 'current_color', 'white')}."
                            hint_overlay = None
                        except BackgammonException as ex:
                            last_msg = str(ex)
                    elif action == "hint":
                        try:
                            hint_overlay = suggest_move(game)
                            last_msg = "Sugerencia generada."
                        except Exception as ex:
                            hint_overlay = None
                            last_msg = str(ex)
                    elif action == "save":
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
                    elif action == "quit":
                        running = False

            if ev.type == pygame.QUIT:
                running = False

            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                elif ev.key == pygame.K_r:
                    if not anim.running:
                        anim.start()
                        pending_roll = True
                        hint_overlay = None
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

                # Click en dados → animación
                if die_rects[0].collidepoint(mx, my) or die_rects[1].collidepoint(mx, my):
                    if not anim.running:
                        anim.start()
                        pending_roll = True
                        hint_overlay = None
                    continue

                # Selección / drag si clic en un punto válido
                pt = screen_to_point(mx, my, positions, bar_rect, off_rect)
                if pt is not None:
                    # permitir seleccionar BAR/OFF por conveniencia (aunque no muevan)
                    if _own_checker_on(game.board, pt, game.current_color) or (pt in (BAR_POS, OFF_POS)):
                        selected_from = pt
                        last_msg = f"Origen seleccionado: {('BAR' if pt == BAR_POS else ('OFF' if pt == OFF_POS else pt))}"
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
                        chosen = max(legal)
                        last_msg = try_move(game, drag_from, chosen)
                        hint_overlay = None
                    dragging = False
                    drag_from = None

        # Dibujo
        screen.fill(COL_BG)
        draw_board(screen, root_rect, positions, bar_rect, off_rect, selected_from, font)
        draw_checkers(screen, positions, bar_rect, off_rect, game.board)
        draw_dice_and_hud(screen, root_rect, game, font, small, hint_overlay, die_rects, anim, buttons)

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

        # Mensaje de estado (barra inferior)
        if last_msg:
            msg_rect = pygame.Rect(MARGIN, H - 28, W - 2 * MARGIN, 24)
            t = small.render(last_msg, True, (220, 220, 220))
            screen.blit(t, (msg_rect.left, msg_rect.top))

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
