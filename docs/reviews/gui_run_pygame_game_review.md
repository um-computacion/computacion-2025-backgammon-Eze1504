# Review de `gui/run_pygame_game.py`

## Complejidad y organización
- El archivo concentra más de 800 líneas de lógica de UI, renderizado, animación, entrada y reglas. Esto dificulta la mantenibilidad y las pruebas. Sería conveniente dividir responsabilidades (por ejemplo, componentes de render, controles del HUD y manejo de entradas).【F:gui/run_pygame_game.py†L1-L808】

## Manejo de excepciones demasiado amplio
- Varias funciones capturan `Exception` de forma genérica (`try_move`, `_own_checker_on`, `_get_available_moves`). Esto oculta errores reales y complica el debugging; debería limitarse a excepciones esperadas o, al menos, registrar los fallos.【F:gui/run_pygame_game.py†L469-L505】
- En `_legal_steps_from` también se silencian fallos al validar movimientos, lo que puede enmascarar errores de lógica en el motor del juego.【F:gui/run_pygame_game.py†L508-L536】

## Lógica duplicada
- El bloque para guardar la partida (`action == "save"`) es prácticamente idéntico al manejado en el atajo de teclado `K_s`. Esta duplicación incrementa el riesgo de inconsistencias; debería extraerse a una función auxiliar.【F:gui/run_pygame_game.py†L614-L646】【F:gui/run_pygame_game.py†L676-L708】

## Supresiones de dobles en `_legal_steps_from`
- El método usa `sorted(set(dice_vals))`, lo que elimina tiradas duplicadas (por ejemplo, dobles). Si `_get_available_moves` devolviera múltiples instancias para reflejar movimientos disponibles, esta operación los descarta, pudiendo mostrar menos opciones de las reales.【F:gui/run_pygame_game.py†L508-L521】

## Salida del proceso desde el módulo
- `main()` llama a `sys.exit(0)` después de `pygame.quit()`. Si la función se usa como parte de una aplicación mayor o se ejecuta en pruebas, terminará el proceso completo. Sería mejor devolver limpiamente y dejar que el llamador decida cómo finalizar.【F:gui/run_pygame_game.py†L788-L808】

## Experiencia de usuario
- No se deshabilitan botones según estado (por ejemplo, `Roll` mientras hay animación, `End Turn` cuando no hay movimientos). Hay lógica para `Button.disabled`, pero nunca se ajusta; aprovecharla mejoraría la claridad de la interfaz.【F:gui/run_pygame_game.py†L227-L318】【F:gui/run_pygame_game.py†L600-L666】

## Recomendaciones
1. Extraer helpers de guardado, sugerencias y reinicio a funciones reutilizables para reducir duplicación.
2. Sustituir capturas genéricas por excepciones específicas o, al menos, registrar los errores.
3. Revisar `_legal_steps_from` para preservar la información de tiradas dobles o usar la API del motor para validar movimientos disponibles.
4. Gestionar el estado de `Button.disabled` para comunicar mejor las acciones permitidas y evitar inputs inválidos.
5. Evitar `sys.exit` en `main()` para facilitar la integración en otras herramientas.

