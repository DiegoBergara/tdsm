# Spec: Execution

## ADDED Requirements

### Requirement: Run command in current session

The system SHALL treat any message that does not start with `/` as a command and SHALL execute it in the current session for that chat.

#### Scenario: Execute command in current session

- **WHEN** current session is `api` and user sends `npm run dev`
- **THEN** the command `npm run dev` is executed in the tmux session `api` (via provider formatting if applicable)

#### Scenario: No current session

- **WHEN** the chat has no current session set and user sends a non-command message
- **THEN** the bot replies with an error asking the user to select or create a session

### Requirement: Send command to another session

The system SHALL support sending a command to a specific session without changing the current session via `/send <session> <command>`.

#### Scenario: Send to another session

- **WHEN** user sends `/send frontend pnpm dev`
- **THEN** the command `pnpm dev` is executed in session `frontend` and the current session for the chat remains unchanged

#### Scenario: Send to nonexistent session

- **WHEN** user sends `/send missing cmd` and session `missing` does not exist
- **THEN** the bot replies with an error and does not execute the command
