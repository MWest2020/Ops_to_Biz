## ADDED Requirements

### Requirement: Create tab if missing before writing
The system SHALL check whether the target tab exists in the spreadsheet before any clear or write operation. If the tab does not exist, it SHALL be created automatically.

#### Scenario: Tab does not exist
- **WHEN** the target tab name is not present in the spreadsheet
- **THEN** the tab is created before the write proceeds

#### Scenario: Tab already exists
- **WHEN** the target tab name is already present
- **THEN** no create operation is performed and the write proceeds normally
