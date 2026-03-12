# Design: Welcome message on /start

## Context

TDSM es un bot de Telegram que gestiona sesiones de desarrollo (tmux) y permite ejecutar comandos y usar asistentes CLI. El router actual (`command_router.py`) trata todos los comandos con prefijo `/`; `/start` no está contemplado y cae en el caso por defecto, mostrando "Unknown command: /start. Use /help for a list." La lista de comandos ya existe en `handle_help`. Se quiere que la primera interacción con el bot sea un mensaje de bienvenida con el propósito del bot y la lista de comandos.

## Goals / Non-Goals

**Goals:**

- Responder al comando `/start` con un mensaje de bienvenida que incluya el propósito del bot y la lista de comandos.
- Mantener un único punto de verdad para la lista de comandos (reutilizable por `/help` y `/start`).
- No cambiar el comportamiento de `/help`.

**Non-Goals:**

- Personalizar el mensaje por usuario o idioma.
- Registrar el comando `/start` en el menú de comandos de Telegram (set_my_commands); puede considerarse en otro cambio.
- Onboarding conversacional o flujos guiados más allá del mensaje estático.

## Decisions

### 1. Dónde implementar el handler de bienvenida

- **Opción A**: Añadir `handle_start` en `command_router.py` junto a `handle_help` y llamarlo cuando `cmd == "start"`.
- **Opción B**: Crear `handlers/welcome.py` con `handle_start` e importarlo en el router.

**Decisión**: Opción A por simplicidad y porque el mensaje de bienvenida es solo texto y la lista de comandos ya está en el mismo módulo. Si en el futuro se añaden más flujos de onboarding, se puede extraer a un módulo dedicado.

### 2. Contenido del mensaje y reutilización con /help

- **Opción A**: Duplicar la lista de comandos en el mensaje de bienvenida y en `/help`.
- **Opción B**: Definir la lista de comandos en una constante o función (p. ej. `get_commands_text()`) y usarla tanto en el mensaje de bienvenida como en `handle_help`.

**Decisión**: Opción B. Se extrae la lista de comandos a una función o constante compartida; el mensaje de `/start` será un bloque de texto fijo (propósito) más la salida de esa función. Así cualquier cambio en comandos se refleja en ambos sitios.

### 3. Formato del mensaje de bienvenida

- Texto en español (alineado con el resto del proyecto).
- Estructura: una o dos frases de propósito (qué es TDSM y para qué sirve), luego una línea en blanco o separador, luego la lista de comandos con el mismo formato que `/help` (p. ej. "Comandos:" seguido de líneas "comando - descripción").

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|------------|
| Mensaje muy largo en pantalla | Mantener el propósito en 2–3 líneas; la lista ya existe y es aceptable en Telegram. |
| Desincronización entre /help y /start | Una única fuente (función/constante) para la lista de comandos. |

## Migration Plan

- No hay migración de datos ni cambios de configuración.
- Despliegue: añadir la rama `start` en el router y la función/constante compartida; desplegar.
- Rollback: eliminar la rama `start` y, si se extrajo la lista, revertir `handle_help` a la lista inline.

## Open Questions

- Ninguno crítico. Opcional: valorar usar `set_my_commands` en el bot para que Telegram muestre la lista de comandos en el menú (fuera de este cambio).
