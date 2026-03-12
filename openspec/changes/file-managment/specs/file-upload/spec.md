# Spec: file-upload

## ADDED Requirements

### Requirement: Upload one or more files to destination path

The system SHALL allow the user to upload one or more files to the host by sending document(s) in Telegram. The destination path SHALL be given as an argument or default to the current session's working directory. Each file SHALL be written with its original filename under the destination path. The destination path SHALL be validated to be under the allowed base path.

#### Scenario: Upload single file with explicit path

- **WHEN** the user sends `/upload ./scripts` and then sends a document named `deploy.sh`
- **THEN** the system SHALL resolve the destination to the session cwd plus `scripts`, validate it is under the allowed base, and write the file as `scripts/deploy.sh` (or the equivalent under the resolved path)

#### Scenario: Upload single file without path uses cwd

- **WHEN** the user sends `/upload` (no path) and then sends one document
- **THEN** the system SHALL write the file to the current session's working directory using the document's file name

#### Scenario: Upload multiple documents in one message

- **WHEN** the user sends `/upload ./dist` and then sends a message with multiple documents (e.g. `app.js`, `style.css`)
- **THEN** the system SHALL write each file under the resolved destination path (e.g. `dist/app.js`, `dist/style.css`) with original names

#### Scenario: Destination path outside allowed base is rejected

- **WHEN** the user sends `/upload /etc` or any destination outside the allowed base path
- **THEN** the system SHALL reject the request and respond with an error message

#### Scenario: File size over limit is rejected

- **WHEN** an uploaded document exceeds the configured upload max size
- **THEN** the system SHALL reject that file and respond with an error message indicating the size limit

#### Scenario: No active session returns error

- **WHEN** the user sends `/upload` or `/upload <path>` and there is no current session for the chat
- **THEN** the system SHALL respond with an error message asking the user to select or create a session first
