Chat ayudame a documentar patrones utilizados para mi proyecto de backgammon

Documentación SOLID + Patrones (dos archivos listos)
✅ docs/ARQUITECTURA_SOLID.md (nuevo)
# ARQUITECTURA Y SOLID

## Single Responsibility (SRP)
- `Board`: Reglas y estado del tablero (puntos, bar, off, capturas, bearing off).
- `Game`: Reglas de turno, uso de dados, fin de juego y puntuación.
- `Dice`: Fuente de movimientos disponibles.
- `Player`: Información del jugador y utilidades.
- `Checker`: Entidad ficha.

## Open/Closed (OCP)
- Nuevas reglas o variantes se pueden incorporar extendiendo métodos de `Board` (p. ej. `move_or_bear_off`) sin modificar los existentes.
- `BackgammonGame` calcula resultado (single/gammon/backgammon) sin acoplarse a UI ni a persistencia.

## Liskov Substitution (LSP)
- Cualquier implementación de `Dice` (real o dummy) funciona con `BackgammonGame` porque la interfaz esperada es estable: `roll?`, `available_moves`, `use_move`, `has_moves`.

## Interface Segregation (ISP)
- `Dice` no obliga a implementar `roll()` (el juego chequea `hasattr(self.dice, "roll")`).
- `Board` no depende de API de UI; solo expone operaciones de dominio.

## Dependency Inversion (DIP)
- `Game` depende de abstracciones (contrato de `Dice`) y de `Board` como servicio de dominio. En tests, inyectamos `DummyDice`.

## Decisiones de diseño
- Uso de constantes de dominio (`BAR`, `OFF`, `HOME_RANGE`) y helper `opponent(color)` para reducir acoplamiento y literales mágicos.
- Helper `_get_available_moves()` en `Game` para tolerar `available_moves` como método o lista.

✅ docs/PATRONES.md (nuevo)
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


