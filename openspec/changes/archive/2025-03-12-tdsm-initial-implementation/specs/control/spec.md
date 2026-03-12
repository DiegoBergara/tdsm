# Spec: Control

## ADDED Requirements

### Requirement: Interrupt process (Ctrl+C)

The system SHALL support sending Ctrl+C to the current session via `/ctrlc` and to a specific session via `/ctrlc [session]`.

#### Scenario: Interrupt current session

- **WHEN** user sends `/ctrlc`
- **THEN** Ctrl+C is sent to the current session for that chat

#### Scenario: Interrupt specific session

- **WHEN** user sends `/ctrlc frontend`
- **THEN** Ctrl+C is sent to session `frontend` regardless of current session

### Requirement: Clear terminal

The system SHALL support clearing the terminal (e.g. send clear command or equivalent) for the current session via `/clear` and for a specific session via `/clear [session]`.

#### Scenario: Clear current session

- **WHEN** user sends `/clear`
- **THEN** the terminal of the current session is cleared

#### Scenario: Clear specific session

- **WHEN** user sends `/clear api`
- **THEN** the terminal of session `api` is cleared
