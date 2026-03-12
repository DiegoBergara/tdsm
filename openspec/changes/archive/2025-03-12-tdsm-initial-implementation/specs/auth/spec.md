# Spec: Auth

## ADDED Requirements

### Requirement: User allowlist

The system SHALL restrict access to bot commands and message handling to users whose Telegram user ID is in the allowlist. The allowlist SHALL be configured via the environment variable `ALLOWED_USER_IDS` (e.g. comma-separated list).

#### Scenario: Allowlisted user can use bot

- **WHEN** a user with ID in ALLOWED_USER_IDS sends any command or message
- **THEN** the bot SHALL process the request normally

#### Scenario: Non-allowlisted user is rejected

- **WHEN** a user whose ID is not in ALLOWED_USER_IDS sends a command or message
- **THEN** the bot SHALL not execute the command and SHALL respond with an access-denied message (or silent ignore, as configured)

### Requirement: Auth layer before routing

The system SHALL perform the allowlist check before command routing or execution. Unauthorized users SHALL not trigger session creation, command execution, or access to session data.

#### Scenario: Unauthorized user cannot create session

- **WHEN** a non-allowlisted user sends `/new test shell`
- **THEN** the bot SHALL reject the request and SHALL not create a session
