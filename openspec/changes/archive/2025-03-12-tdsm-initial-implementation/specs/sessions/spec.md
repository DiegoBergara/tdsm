# Spec: Sessions

## ADDED Requirements

### Requirement: Create session

The system SHALL support creating a named tmux session with an optional provider via `/new <name> [provider]`. Default provider SHALL be `shell` when omitted.

#### Scenario: Create session with default provider

- **WHEN** user sends `/new api`
- **THEN** a tmux session named `api` is created with provider `shell`

#### Scenario: Create session with explicit provider

- **WHEN** user sends `/new refactor claude-code`
- **THEN** a tmux session named `refactor` is created with provider `claude-code`

### Requirement: List sessions

The system SHALL support listing all managed sessions via `/list`, showing session name, provider, and which session is current for the chat.

#### Scenario: List sessions

- **WHEN** user sends `/list`
- **THEN** the bot replies with a list of sessions (e.g. "Sessions: - api [shell] (current) - refactor [claude-code]")

### Requirement: Select current session

The system SHALL support setting the current session for the chat via `/use <name>`. Only one session SHALL be current per chat at a time.

#### Scenario: Set current session

- **WHEN** user sends `/use api`
- **THEN** the current session for that chat is set to `api` and the bot confirms

#### Scenario: Use with nonexistent session

- **WHEN** user sends `/use nonexistent` and no session named `nonexistent` exists
- **THEN** the bot replies with an error and does not change the current session

### Requirement: Show current session

The system SHALL support showing the current session for the chat via `/current`.

#### Scenario: Show current session

- **WHEN** user sends `/current` and current session is `api`
- **THEN** the bot replies with "Current session: api" (or equivalent)

### Requirement: Rename session

The system SHALL support renaming a session via `/rename <old> <new>`.

#### Scenario: Rename session

- **WHEN** user sends `/rename api backend`
- **THEN** the session `api` is renamed to `backend` and metadata is updated; if `api` was current, current becomes `backend`

### Requirement: Kill session

The system SHALL support terminating a session via `/kill <session>`.

#### Scenario: Kill session

- **WHEN** user sends `/kill refactor`
- **THEN** the tmux session `refactor` is terminated and removed from managed sessions
