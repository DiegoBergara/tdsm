# Spec: Providers

## ADDED Requirements

### Requirement: Provider interface

The system SHALL define a shared provider interface (e.g. base class or protocol) with: identifier, display name, `is_available()`, `get_modes()`, `default_mode()`, `next_mode(current)`, `bootstrap_commands()`, and `format_user_command(command)`. All built-in and future providers SHALL implement this interface.

#### Scenario: Provider reports availability

- **WHEN** the registry checks a provider's `is_available()`
- **THEN** it returns True or False (e.g. based on PATH or env) and the system uses this for `/providers` and session creation

#### Scenario: Provider formats command

- **WHEN** the system needs to run a user command in a session with a given provider
- **THEN** it SHALL call `format_user_command(command)` and send the result to the tmux session

### Requirement: Provider registry

The system SHALL maintain a provider registry that holds all known providers and allows lookup by id. The registry SHALL be used by session creation and by the `/providers` command.

#### Scenario: List providers from registry

- **WHEN** the bot needs to list providers (e.g. for `/providers` or for `/new` completion)
- **THEN** it SHALL obtain the list from the registry with availability status

### Requirement: List providers command

The system SHALL support listing available and unavailable providers via `/providers`, indicating availability (e.g. "available" / "unavailable") per provider.

#### Scenario: List providers

- **WHEN** user sends `/providers`
- **THEN** the bot replies with a list of providers (e.g. "shell (available), claude-code (available), codex (unavailable), ...")

### Requirement: Built-in providers

The system SHALL ship built-in providers for: shell, claude-code, codex, cursor-cli, gemini-cli. Support MAY be shallow initially (e.g. correct id, display name, availability check, and basic command formatting).

#### Scenario: Shell provider always available

- **WHEN** the shell provider's `is_available()` is called
- **THEN** it SHALL return True (shell is always available in a tmux environment)
