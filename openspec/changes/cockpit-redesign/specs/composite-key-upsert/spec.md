## ADDED Requirements

### Requirement: Upsert key is name and namespace composite
The system SHALL identify each application row by the composite key `name|namespace`. Two rows with the same `name` but different `namespace` values SHALL be treated as distinct apps.

#### Scenario: Same name different namespace
- **WHEN** ArgoCD returns two apps with the same `name` but different `namespace` values
- **THEN** both are written as separate rows in the sheet

#### Scenario: Exact match on both name and namespace
- **WHEN** an app matches an existing row on both `name` and `namespace`
- **THEN** the existing row is updated in place (not duplicated)

#### Scenario: New app not in sheet
- **WHEN** an app's `name|namespace` combination does not match any existing row
- **THEN** a new row is appended to the sheet

---

### Requirement: Owned columns are updated on match; extra columns preserved
The system SHALL update only the owned columns on a matched row. Any columns not in the owned set (e.g. manager-added notes, subscription tier, cost centre) SHALL be preserved exactly as-is.

Owned columns: `customer_name`, `environment`, `is_frontend`, `name`, `namespace`, `cluster`, `repo_url`, `target_revision`, `sync_status`, `health_status`, `last_synced`, `images`, `app_type`, `team`, `removed_at`.

#### Scenario: Manager has added a custom column
- **WHEN** a row has an extra column not in the owned set (e.g. `notes`)
- **THEN** the `notes` value is unchanged after a sync run

#### Scenario: Owned column has changed value in ArgoCD
- **WHEN** `sync_status` changes in ArgoCD for an existing app
- **THEN** the sheet row reflects the new `sync_status` after the sync run

---

### Requirement: GWS write clears stale rows before writing
The system SHALL clear the full sheet tab range before writing the new data set, to prevent stale rows from persisting when the total row count decreases between runs.

#### Scenario: Row count decreases between runs
- **WHEN** a previous run wrote 50 rows and the current run produces 40 rows
- **THEN** the sheet contains exactly 40 data rows plus the header row after the sync (no stale rows from the previous run)
