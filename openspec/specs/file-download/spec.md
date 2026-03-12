# file-download Specification

## Purpose
TBD - created by archiving change file-managment. Update Purpose after archive.
## Requirements
### Requirement: Download file by path

The system SHALL allow the user to download a single file from the host by providing a path. The path SHALL be resolved relative to the current session's working directory, or as an absolute path within the allowed base path(s). The bot SHALL respond with the file as a Telegram document.

#### Scenario: Download file with relative path

- **WHEN** the user sends `/download src/main.py` (or equivalent) in a chat with an active session whose cwd is `/home/user/project`
- **THEN** the system resolves the path to `/home/user/project/src/main.py`, validates it is under the allowed base path, and sends that file to the user as a document

#### Scenario: Download file with absolute path under allowed base

- **WHEN** the user sends `/download /home/user/project/out/build.jar` and that path is under the configured allowed base path
- **THEN** the system validates the path and sends the file as a document

#### Scenario: Path outside allowed base is rejected

- **WHEN** the user sends `/download /etc/passwd` (or any path outside the allowed base)
- **THEN** the system SHALL reject the request and respond with an error message indicating that the path is not allowed

#### Scenario: Non-existent file returns error

- **WHEN** the user sends `/download missing.txt` and the file does not exist
- **THEN** the system SHALL respond with an error message and SHALL NOT send a document

#### Scenario: Directory path returns error for file download

- **WHEN** the user sends `/download some_dir` and `some_dir` is a directory
- **THEN** the system SHALL respond with an error message directing the user to use folder download (ZIP) for directories, and SHALL NOT send a document

#### Scenario: File size over limit is rejected

- **WHEN** the requested file size exceeds the configured download max size
- **THEN** the system SHALL reject the request and respond with an error message indicating the size limit

