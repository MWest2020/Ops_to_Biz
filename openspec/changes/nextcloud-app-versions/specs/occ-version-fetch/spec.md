## ADDED Requirements

### Requirement: Resolve namespace and deployment for each Business row
The system SHALL determine the correct k8s namespace and Nextcloud deployment name for each Business row using the following rules:
- If `environment` is non-empty: namespace = `{customer_name}-{environment}`, deployment = `nextcloud`
- If `environment` is empty: namespace = `customer_name`, deployment = the ArgoCD app name stored in the pivot row

#### Scenario: Namespace encodes environment
- **WHEN** row has `customer_name=noordwijk` and `environment=prod`
- **THEN** namespace is `noordwijk-prod` and deployment is `nextcloud`

#### Scenario: Namespace is org only
- **WHEN** row has `customer_name=beek` and `environment=` (empty)
- **THEN** namespace is `beek` and deployment is e.g. `beek-accept-nextcloud`

---

### Requirement: Fetch app versions via occ exec
The system SHALL exec into the Nextcloud deployment and run `php occ app:list --output=json`. It SHALL extract the version strings for `opencatalogi`, `openregister`, and `openconnector` from the JSON output.

#### Scenario: All three apps installed
- **WHEN** occ output contains all three apps under `enabled`
- **THEN** version columns contain the respective version strings

#### Scenario: App not installed
- **WHEN** occ output does not contain an app
- **THEN** the version column for that app is empty string

#### Scenario: Exec fails
- **WHEN** kubectl exec returns a non-zero exit code
- **THEN** all three version columns are empty string and the error is logged to stderr; the sync continues

---

### Requirement: Version fetch runs concurrently
The system SHALL fetch versions for all Business rows concurrently using a thread pool to minimise total sync time.

#### Scenario: Multiple rows fetched in parallel
- **WHEN** there are 50 nextcloud rows
- **THEN** exec calls are dispatched concurrently, not sequentially
