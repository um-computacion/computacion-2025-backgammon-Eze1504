# PATRONES UTILIZADOS

## Template Method (Board.move_or_bear_off)
- Define el esqueleto: si el destino queda dentro de 1..24 => `move_checker`; si “sale” y `can_bear_off_from` => `bear_off_checker`.
- Permite extender comportamiento sin tocar `move_checker`.

## Strategy / Policy (Dice)
- `BackgammonGame` interactúa con un “estrategia” de dados. `DummyDice` o `Dice` real se intercambian sin cambiar reglas de juego.

## Command-lite (movimientos)
- Cada jugada se modela como “aplicar movimiento y consumir dado”. La transición de estado es atómica y validada.

## Guard Clauses
- Validaciones tempranas: turnos, bar prioritario, dado disponible, “dado más alto si solo uno es jugable”.

## Value Objects (constantes de dominio)
- `BAR`, `OFF`, `HOME_RANGE` y `opponent(color)` encapsulan reglas y significados del dominio, evitando números mágicos.
