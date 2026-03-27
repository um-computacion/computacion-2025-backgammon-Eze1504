Chat, necesito implementar la función move_or_bear_off en la clase Board.
Tiene que permitir mover fichas dentro del tablero y también realizar el "bearing off" cuando todas las fichas del jugador están en el home board.
¿Podés darme una implementación completa que maneje ambos casos y valide los movimientos según las reglas del backgammon?

Claro, Eze. Acá tenés una implementación robusta para la función move_or_bear_off dentro de tu clase Board 👇

def move_or_bear_off(self, color: str, from_pos: int, steps: int) -> None:
    """
    Mueve una ficha desde 'from_pos' según el valor del dado 'steps'.
    Si el destino supera el punto 24 (para blancas) o es menor que 1 (para negras),
    se considera un movimiento de "bearing off".
    """
    if from_pos < 1 or from_pos > 24:
        raise ValueError(f"Posición inválida: {from_pos}")

    # Determinar dirección del movimiento
    direction = 1 if color == "white" else -1
    to_pos = from_pos + (steps * direction)

    # Validar si puede hacer bearing off
    if self.can_bear_off_from(color, from_pos, steps):
        self.remove_checker(from_pos, color)
        self.add_checker(self.OFF, color)
        return

    # Si el destino es válido dentro del tablero
    if 1 <= to_pos <= 24:
        # Movimiento normal
        self.move_checker(color, from_pos, steps)
    else:
        raise ValueError(f"No se puede mover fuera del tablero desde {from_pos} con dado {steps}")

⚙️ Explicación

La función revisa si el movimiento resulta en bearing off (salida de ficha).

Si no, realiza un movimiento normal dentro del tablero.

Usa can_bear_off_from para asegurarse de que el jugador está en la fase final.

Maneja correctamente dirección de movimiento según color.

💾 Commit sugerido
git add core/board.py
git commit -m "feat(board): implementa move_or_bear_off con soporte para bearing off y validaciones de tablero"


¿Querés que te prepare uno más, por ejemplo para una función dentro de BackgammonGame (como el manejo de _check_victory_after_move o la lógica de alternar turnos)?




Chat, necesito que la clase BackgammonGame valide correctamente si un jugador puede mover cuando hay fichas en el BAR.
Si hay fichas en el BAR, sólo debería poder mover desde ahí (from_pos == 0).
¿Podés mostrarme cómo implementar esa validación dentro de apply_player_move?



Claro, Eze. Podés agregar esta validación justo antes de ejecutar el movimiento en apply_player_move:

if self._has_bar(self.current_color) and from_pos != self.BAR:
    raise GameRuleError("Debés reingresar desde el BAR antes de mover otras fichas.")


🔍 Explicación:

self._has_bar(color) revisa si el jugador actual tiene fichas en el BAR.

Si las tiene, no se le permite mover otra ficha hasta que reingrese.

La validación se ejecuta antes de llamar a move_checker o reenter_checker.


Chat, quiero que la función _determine_outcome calcule correctamente el resultado de la partida: single, gammon o backgammon.
¿Cómo puedo implementarla para cubrir las tres reglas del backgammon clásico?


Perfecto. Acá tenés una versión clara y funcional para _determine_outcome:

def _determine_outcome(self, winner_color: str, loser_color: str) -> tuple[str, int]:
    loser_counts = self.board.count_checkers(loser_color)
    if loser_counts.get("off", 0) > 0:
        return ("single", 1)

    has_bar = self.board.get_checkers_in_bar(loser_color) != []
    home_start, home_end = self.board.get_home_board_range(winner_color)
    has_in_winner_home = any(
        any(ch.get_color() == loser_color for ch in self.board.get_point(p))
        for p in range(home_start, home_end + 1)
    )

    if has_bar or has_in_winner_home:
        return ("backgammon", 3)
    return ("gammon", 2)


🔍 Explicación:

Single (1 punto): el perdedor ya sacó al menos una ficha (off > 0).

Gammon (2 puntos): el perdedor no tiene fichas borneadas ni en el BAR ni en el home del ganador.

Backgammon (3 puntos): el perdedor no sacó fichas y además tiene al menos una en BAR o en el home del ganador.

💾 Commit:

git add core/game.py
git commit -m "feat(game): implementa cálculo completo del resultado de la partida (single, gammo


Chat, necesito una forma robusta de determinar cuántas fichas de un color quedan en el tablero o en el BAR.
¿Podés ayudarme a implementar _remaining_on_board_or_bar en la clase BackgammonGame?


Sí, esta función cuenta todas las fichas aún en juego (sin incluir las borneadas).
Podés implementarla así:

def _remaining_on_board_or_bar(self, color: str) -> int:
    left = 0

    # Contar en tablero
    if hasattr(self.board, "get_point"):
        for p in range(1, 25):
            stack = self.board.get_point(p) or []
            for ch in stack:
                ch_color = getattr(ch, "color", None)
                if ch_color is None and hasattr(ch, "get_color"):
                    try:
                        ch_color = ch.get_color()
                    except Exception:
                        pass
                if ch_color == color:
                    left += 1

    # Contar en BAR
    if hasattr(self.board, "get_checkers_in_bar"):
        left += len(self.board.get_checkers_in_bar(color) or [])
    elif hasattr(self.board, "count_bar"):
        left += int(self.board.count_bar(color) or 0)

    return left


🔍 Explicación:

Usa get_point(p) para contar las fichas activas en las 24 posiciones del tablero.

Incluye las que están en el BAR (por get_checkers_in_bar o count_bar).

Es tolerante a distintas estructuras de Board y evita errores con try/except.

💾 Commit:

git add core/game.py
git commit -m "feat(game): implementa cálculo robusto de fichas restantes en tablero y BAR"
