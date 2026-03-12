## ADDED Requirements

### Requirement: Pivot rows to one row per customer and environment
The system SHALL aggregate classified app rows into one row per `(customer, environment)` pair. Each row SHALL have a boolean column for each known product type indicating whether that product is deployed for that customer+environment combination.

Output columns: `customer_name`, `environment`, `nextcloud`, `react`, `tilburg-ui`.

#### Scenario: Customer has one product in accept
- **WHEN** only `acato-accept-nextcloud` exists for customer `acato`
- **THEN** output row is `customer=acato, environment=accept, nextcloud=True, react=False, tilburg-ui=False`

#### Scenario: Customer has multiple products in same environment
- **WHEN** both `baarn-prod-nextcloud` and `baarn-prod-reactfront` exist
- **THEN** output row is `customer=baarn, environment=prod, nextcloud=True, react=True, tilburg-ui=False`

#### Scenario: Customer has same product in two environments
- **WHEN** `noordwijk-accept-nextcloud` and `noordwijk-prod-nextcloud` both exist
- **THEN** two rows are produced: one for accept, one for prod

#### Scenario: Output is sorted
- **WHEN** rows are produced
- **THEN** they are sorted by `customer_name` ascending, then `environment` ascending

---

### Requirement: Business output is written independently of ops output
The system SHALL support `OUTPUT_MODE=business` as a separate mode. Running in business mode SHALL NOT modify the ops `Deployments` tab or file.

#### Scenario: Business mode writes to Business tab
- **WHEN** `OUTPUT_MODE=business` and gws mode is active
- **THEN** the `Business` tab in the spreadsheet is written; `Deployments` tab is untouched

#### Scenario: Business mode writes to separate local file
- **WHEN** `OUTPUT_MODE=business` and local mode is active
- **THEN** a separate xlsx file is written (path from `BUSINESS_OUTPUT_PATH` env var)
