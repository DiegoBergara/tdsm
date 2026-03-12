# folder-download-zip Specification

## Purpose
TBD - created by archiving change file-managment. Update Purpose after archive.
## Requirements
### Requirement: Download folder as ZIP by path

The system SHALL allow the user to download a directory from the host as a single ZIP file by providing a path. The path SHALL be resolved relative to the current session's working directory, or as an absolute path within the allowed base path(s). The server SHALL generate a ZIP archive of the directory contents and send it as a Telegram document.

#### Scenario: Download folder with relative path

- **WHEN** the user sends a command to download a folder (e.g. `/download dir/` or `/downloadzip dir`) and the session cwd is `/home/user/project`
- **THEN** the system resolves the path to the directory, validates it is under the allowed base path, creates a ZIP of that directory, and sends the ZIP as a document

#### Scenario: Folder path outside allowed base is rejected

- **WHEN** the user requests download of a directory whose resolved path is outside the allowed base path
- **THEN** the system SHALL reject the request and respond with an error message

#### Scenario: Non-existent or file path returns error

- **WHEN** the user requests folder download for a path that does not exist or is a file (not a directory)
- **THEN** the system SHALL respond with an error message and SHALL NOT send a document

#### Scenario: ZIP size over limit is rejected

- **WHEN** the generated ZIP size would exceed the configured maximum (e.g. for download or for Telegram document limit)
- **THEN** the system SHALL reject the operation and respond with an error message indicating the size limit

#### Scenario: Empty folder produces valid ZIP

- **WHEN** the user requests download of an empty directory
- **THEN** the system SHALL produce a valid ZIP file (containing no files or only the directory entry) and send it as a document

