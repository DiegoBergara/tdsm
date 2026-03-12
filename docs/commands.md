# Commands

All commands require the user to be in the allowlist (`ALLOWED_USER_IDS`). Messages not starting with `/` are executed as a command in the current session.

## Session lifecycle

| Command | Description |
|--------|-------------|
| `/new <name> [provider]` | Create a named session. Default provider: `shell`. |
| `/list` | List all sessions; current session for this chat is marked. |
| `/use <name>` | Set the current session for this chat. |
| `/current` | Show the current session. |
| `/rename <old> <new>` | Rename a session. |
| `/kill <session>` | Terminate a session. |

## Execution

| Command | Description |
|--------|-------------|
| _(plain text)_ | Run as command in the current session. |
| `/send <session> <command>` | Run command in another session without changing current. |

## File transfer

| Command | Description |
|--------|-------------|
| `/download <path>` or `/dl <path>` | Download a file from the session’s working tree, or a folder as a ZIP. Path is relative to session cwd or absolute within the allowed base. |
| `/upload [path]` | Set upload destination (default: session cwd). Then send file(s) as document(s). |
| `/upload --extract [path]` | Same as `/upload` but the next document must be a ZIP; it will be extracted at the destination. |

## Control

| Command | Description |
|--------|-------------|
| `/ctrlc [session]` | Send Ctrl+C to current or specified session. |
| `/clear [session]` | Clear the terminal. |

## Observability

| Command | Description |
|--------|-------------|
| `/status [session]` | Session name, provider, mode, last output. |
| `/logs [session]` | Last N lines (configurable). |
| `/history [session]` | Command history from SQLite. |

## Providers and modes

| Command | Description |
|--------|-------------|
| `/providers` | List providers and availability. |
| `/mode` | Cycle to next assistant mode. |
| `/mode <mode>` | Set mode explicitly. |
| `/modes` | List available modes for current session's provider. |

## Help

| Command | Description |
|--------|-------------|
| `/help` | List all commands. |
