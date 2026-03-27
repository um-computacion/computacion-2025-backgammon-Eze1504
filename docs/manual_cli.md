🧭 Manual de Usuario – Backgammon CLI

Versión: v1.0
Ubicación: run_cli_game.py

La interfaz de línea de comandos (CLI) permite jugar una partida completa de Backgammon directamente desde la consola.

🧩 Inicio del juego

Ejecutar desde la raíz del proyecto:

python run_cli_game.py


La consola mostrará:

🎲 Bienvenido al Backgammon CLI 🎲
Escribí 'help' para ver los comandos disponibles.
>

⚙️ Comandos disponibles
Comando	Alias	Descripción	Ejemplo
help	h, ?	Muestra la lista de comandos disponibles.	help
quit	q, exit	Sale del juego.	quit
show	status	Muestra el tablero actual, los dados y el turno.	show
roll	r	Lanza los dados e inicia el turno del jugador actual.	roll
move	—	Mueve una ficha desde una posición usando el valor de un dado.	move 13 5 o move bar 4
end	—	Finaliza el turno si ya no hay movimientos válidos.	end
hint	—	Sugiere una jugada posible basada en el estado actual.	hint
undo	—	Deshace el último movimiento (si el motor lo permite).	undo
save	—	Guarda la partida actual en un archivo JSON. Se puede especificar una ruta.	save partida.json o save
💡 Ejemplos de uso
Iniciar y mostrar el tablero
> roll
Turno de white. Dados: (3, 5)
> show

Mover fichas
> move 13 5
OK: moviste desde 13 5 paso(s).

Terminar turno
> end
Turno finalizado. Ahora juega black.

Obtener ayuda
> help

Guardar partida
> save backup.json
Partida guardada en: backup.json

Pedir una sugerencia
> hint
Sugerencia: Probá mover desde un punto alto (24..19) usando el 6.

⚠️ Errores comunes y soluciones
Situación	Mensaje mostrado	Solución
Intentar mover sin tirar los dados	Los dados no han sido lanzados.	Ejecutar roll antes de move.
Usar un dado no disponible	Movimiento inválido: Dado X no disponible	Verificar los valores actuales de los dados con show.
Escribir un comando incorrecto	Comando desconocido: xyz.	Revisar help para ver los comandos válidos.
Intentar “undo” sin soporte	Deshacer no está disponible en este motor.	Continuar el juego normalmente; la función es opcional.
Guardar en una ruta inválida	💥 Ocurrió un error: ...	Revisar permisos o ruta de guardado.
📄 Notas

Los comandos no distinguen mayúsculas/minúsculas.

bar equivale al punto 0, off equivale a 25.

El juego termina automáticamente cuando un jugador borneó todas sus fichas.
