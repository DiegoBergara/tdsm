# Proposal: Welcome message on /start

## Why

Cuando un usuario inicia una conversación con el bot mediante `/start`, actualmente el bot responde con "Unknown command: /start. Use /help for a list." Esto da una mala primera impresión y no comunica el propósito del bot ni qué puede hacer el usuario. Mostrar un mensaje de bienvenida con el propósito de TDSM y la lista de comandos mejora la experiencia de onboarding y reduce la fricción para nuevos usuarios.

## What Changes

- **Mensaje de bienvenida en `/start`**: al recibir el comando `/start`, el bot enviará un mensaje que incluya:
  - Breve descripción del propósito del bot (gestión de sesiones de desarrollo vía tmux, ejecución remota de comandos, integración con asistentes CLI).
  - Lista de comandos disponibles (la misma información que `/help`, o una versión adaptada para contexto de bienvenida).
- **Handler explícito para `/start`**: el router debe reconocer `start` como comando válido y delegar a un handler que construya y envíe el mensaje de bienvenida.
- No se modifica el comportamiento de `/help`; puede seguir mostrando la lista de comandos de forma aislada para consultas posteriores.

## Capabilities

### New Capabilities

- `welcome-on-start`: respuesta al comando `/start` con mensaje de bienvenida que incluye el propósito del bot y la lista de comandos disponibles.

### Modified Capabilities

- Ninguna.

## Impact

- **Código**: en `command_router.py` (o equivalente), añadir rama para `cmd == "start"` que invoque un handler de bienvenida; el contenido del mensaje puede vivir en un módulo de handlers (p. ej. `handlers/welcome.py`) o junto a `handle_help` para reutilizar la lista de comandos. Opcionalmente extraer la lista de comandos a un único lugar (constante o función) compartida por `/help` y `/start`.
- **APIs**: solo uso actual de la API de Telegram para enviar un mensaje de texto.
- **UX**: primera interacción con el bot pasa de error a mensaje útil; alineado con la convención de Telegram de usar `/start` para iniciar bots.
