# Spec: Observability

## ADDED Requirements

### Requirement: Session status

The system SHALL support showing session status via `/status [session]`. When session is omitted, SHALL show the current session. Response SHALL include session name, provider, mode, and last output (or a summary).

#### Scenario: Status of current session

- **WHEN** user sends `/status` and current session is `api`
- **THEN** the bot replies with session name, provider, mode, and last output (e.g. "Session: api, Provider: shell, Mode: shell, Last output: ...")

#### Scenario: Status of specific session

- **WHEN** user sends `/status refactor`
- **THEN** the bot replies with status for session `refactor` only

### Requirement: Logs

The system SHALL support returning the last N lines of session output via `/logs [session]`. N SHALL be configurable (e.g. env or default 50).

#### Scenario: Logs of current session

- **WHEN** user sends `/logs`
- **THEN** the bot replies with the last N lines from the current session's tmux pane

#### Scenario: Logs of specific session

- **WHEN** user sends `/logs api`
- **THEN** the bot replies with the last N lines from session `api`

### Requirement: Command history

The system SHALL support returning command history for the session via `/history [session]`. History SHALL be stored in SQLite and SHALL be per session (and optionally per chat).

#### Scenario: History for current session

- **WHEN** user sends `/history`
- **THEN** the bot replies with stored command history for the current session

#### Scenario: History for specific session

- **WHEN** user sends `/history refactor`
- **THEN** the bot replies with stored command history for session `refactor`
