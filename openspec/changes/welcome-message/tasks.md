## 1. Lista de comandos compartida

- [x] 1.1 Extraer la lista de comandos y descripciones a una constante o función compartida (p. ej. `get_commands_text()`) en `command_router.py`
- [x] 1.2 Hacer que `handle_help` use esa fuente compartida para mostrar la lista

## 2. Handler de bienvenida y enrutado

- [x] 2.1 Implementar `handle_start` que construya el mensaje de bienvenida (propósito del bot + lista de comandos compartida) y lo envíe como respuesta
- [x] 2.2 En el `dispatch` del router, añadir la rama `cmd == "start"` que invoque `handle_start`
