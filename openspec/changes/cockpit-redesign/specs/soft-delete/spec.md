## ADDED Requirements

### Requirement: Mark removed apps as REMOVED
The system SHALL detect apps present in the sheet but absent from the current ArgoCD fetch. For each such app, the system SHALL set `sync_status` to `[REMOVED]` and write the current UTC date (ISO 8601, date-only: `YYYY-MM-DD`) to a `removed_at` column. The row SHALL NOT be deleted.

#### Scenario: App disappears from ArgoCD
- **WHEN** an app row exists in the sheet and is not returned by the current ArgoCD fetch
- **THEN** `sync_status` is set to `[REMOVED]` and `removed_at` is set to today's UTC date

#### Scenario: App was already marked removed
- **WHEN** an app row already has `sync_status = [REMOVED]` and is again absent from the fetch
- **THEN** the row is left unchanged (existing `removed_at` date is preserved)

---

### Requirement: Restore a previously removed app
The system SHALL clear `sync_status = [REMOVED]` and empty `removed_at` if a previously removed app reappears in the ArgoCD fetch. All owned columns SHALL be updated with the current ArgoCD values.

#### Scenario: Removed app reappears in ArgoCD
- **WHEN** a row has `sync_status = [REMOVED]` and the app is returned by the current fetch
- **THEN** all owned columns are updated to the current ArgoCD values, `removed_at` is cleared

---

### Requirement: removed_at column is owned
The system SHALL treat `removed_at` as an owned column — it is managed exclusively by the sync and SHALL NOT be editable by managers in a way that persists across runs for non-removed apps.

#### Scenario: Active app has no removed_at
- **WHEN** an app is present in ArgoCD (not removed)
- **THEN** `removed_at` is empty string in the output row
