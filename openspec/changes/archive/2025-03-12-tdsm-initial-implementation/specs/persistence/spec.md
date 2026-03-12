# Spec: Persistence

## ADDED Requirements

### Requirement: Managed sessions table

The system SHALL persist managed session metadata in SQLite. The table SHALL include: session_name (PRIMARY KEY), provider_id, mode, working_directory, created_at, updated_at.

#### Scenario: Session created is persisted

- **WHEN** a session is created via `/new api shell`
- **THEN** a row SHALL exist in the managed_sessions table with session_name=api, provider_id=shell, and timestamps

#### Scenario: Session killed is removed

- **WHEN** a session is killed via `/kill api`
- **THEN** the row for that session SHALL be removed from managed_sessions

### Requirement: Chat context table

The system SHALL persist the current session per chat in SQLite. The table SHALL allow storing chat_id and current_session so that the current session is restored after bot restart.

#### Scenario: Current session persisted

- **WHEN** user sends `/use api` in a chat
- **THEN** chat_context SHALL store (chat_id, current_session=api) for that chat

#### Scenario: Current session restored after restart

- **WHEN** the bot restarts and a chat had current_session=api
- **THEN** after restart, that chat's current session SHALL still be api (from DB)

### Requirement: Command history table and store

The system SHALL persist command history in SQLite (e.g. id, chat_id, session_name, command, timestamp). A history store module SHALL provide append and query (e.g. last N per session) operations.

#### Scenario: Command recorded

- **WHEN** a command is executed in a session (e.g. "npm run dev")
- **THEN** the command SHALL be recorded in command_history with session_name and chat_id

#### Scenario: History query returns stored commands

- **WHEN** `/history` or `/history <session>` is invoked
- **THEN** the system SHALL return commands from command_history for that session (and optionally chat)
