# Spec: Bot setup

## ADDED Requirements

### Requirement: Bot commands list

The system SHALL document and support the BotFather command list so that users see the following (or equivalent) in Telegram: help, providers, new, list, use, current, send, status, logs, history, mode, modes, ctrlc, kill, rename, clear.

#### Scenario: Commands visible in Telegram

- **WHEN** an operator sets bot commands via BotFather using the documented list
- **THEN** users SHALL see the command menu with the listed commands

### Requirement: Environment variables documented

The system SHALL document required and optional environment variables: TELEGRAM_BOT_TOKEN (required), ALLOWED_USER_IDS (required), DATABASE_PATH (optional, default e.g. ./data/tdsm.db), LOG_LEVEL (optional), DEFAULT_LOG_LINES (optional). An `.env.example` or equivalent SHALL be provided.

#### Scenario: Example env file

- **WHEN** a deployer reads the repository
- **THEN** they SHALL find an .env.example (or docs) listing TELEGRAM_BOT_TOKEN, ALLOWED_USER_IDS, and optional variables with descriptions

### Requirement: BotFather setup instructions

The system SHALL provide instructions for creating a bot with BotFather and for setting the bot command list (e.g. /setcommands and the list to paste).

#### Scenario: Operator can create bot from docs

- **WHEN** an operator follows the documented BotFather setup
- **THEN** they SHALL be able to create a bot, obtain the token, and set the command list as described
