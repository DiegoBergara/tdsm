# folder-upload Specification

## Purpose
TBD - created by archiving change file-managment. Update Purpose after archive.
## Requirements
### Requirement: Upload folder as ZIP and extract at destination

The system SHALL allow the user to upload a folder by sending a ZIP file. The user SHALL specify a destination path (or use the current session's working directory). The system SHALL extract the ZIP contents at the destination path. Extraction SHALL validate that every member path in the ZIP resolves under the destination path to prevent path traversal (e.g. malicious entries like `../../../etc/passwd`).

#### Scenario: Upload ZIP and extract to explicit path

- **WHEN** the user sends `/upload --extract ./vendor` (or equivalent) and then sends a document that is a ZIP file
- **THEN** the system SHALL resolve the destination path, validate it is under the allowed base, extract the ZIP so that all members are under that destination, and confirm success

#### Scenario: Upload ZIP without path extracts to cwd

- **WHEN** the user sends a command to upload and extract (e.g. `/upload --extract`) with no path and then sends a ZIP document
- **THEN** the system SHALL extract the ZIP into the current session's working directory

#### Scenario: ZIP member path traversal is rejected

- **WHEN** the user sends a ZIP that contains a member with a path that would resolve outside the destination (e.g. `../../etc/passwd`)
- **THEN** the system SHALL NOT extract that member (or SHALL abort the extraction) and SHALL respond with an error message indicating a security rejection

#### Scenario: ZIP size over limit is rejected

- **WHEN** the uploaded ZIP file exceeds the configured maximum size for upload or for ZIP extraction
- **THEN** the system SHALL reject the upload and respond with an error message

#### Scenario: Non-ZIP document with extract flag returns error

- **WHEN** the user sends `/upload --extract` and then sends a document that is not a ZIP file
- **THEN** the system SHALL respond with an error message indicating that the file must be a ZIP for folder upload

#### Scenario: No active session returns error

- **WHEN** the user attempts folder upload and there is no current session for the chat
- **THEN** the system SHALL respond with an error message asking the user to select or create a session first

