# Spec: welcome-on-start

## ADDED Requirements

### Requirement: Welcome message on /start

The system SHALL respond to the Telegram command `/start` with a single message that includes a brief description of the bot's purpose (Telegram Dev Session Manager: manage development sessions, run commands remotely, use CLI assistants) and the full list of available commands in the same format as `/help`. The system SHALL NOT reply with "Unknown command" for `/start`.

#### Scenario: User sends /start and receives welcome message

- **WHEN** the user sends the command `/start` to the bot
- **THEN** the system SHALL reply with a text message that includes (1) the purpose of the bot and (2) the list of all available commands with their short descriptions

#### Scenario: Welcome message includes same commands as /help

- **WHEN** the user sends `/start`
- **THEN** the list of commands in the welcome message SHALL be the same set and format as the list shown when the user sends `/help` (e.g. "help - Show this help", "new - Create session", etc.)

#### Scenario: /help unchanged

- **WHEN** the user sends `/help`
- **THEN** the system SHALL continue to reply with the list of commands as before; behavior of `/help` SHALL NOT be altered by this feature
