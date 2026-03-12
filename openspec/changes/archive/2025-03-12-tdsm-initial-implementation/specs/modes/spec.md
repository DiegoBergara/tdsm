# Spec: Modes

## ADDED Requirements

### Requirement: Cycle mode

The system SHALL support cycling to the next assistant mode for the current session via `/mode` (no arguments). The next mode SHALL be determined by the session's provider (e.g. `next_mode(current)`).

#### Scenario: Cycle mode

- **WHEN** user sends `/mode` and current session has provider with modes [chat, edit, review] and current mode is edit
- **THEN** the mode SHALL change to review (or next in list) and the bot confirms

### Requirement: Set mode

The system SHALL support setting the assistant mode explicitly via `/mode <mode>`.

#### Scenario: Set mode

- **WHEN** user sends `/mode review`
- **THEN** the current session's mode is set to `review` and the bot confirms

#### Scenario: Set invalid mode

- **WHEN** user sends `/mode invalid` and the provider does not support `invalid`
- **THEN** the bot replies with an error and lists valid modes or suggests `/modes`

### Requirement: List modes

The system SHALL support listing available modes for the current session's provider via `/modes`.

#### Scenario: List modes

- **WHEN** user sends `/modes` and current session's provider supports chat, edit, review
- **THEN** the bot replies with "Available modes: chat, edit, review" (or equivalent)
