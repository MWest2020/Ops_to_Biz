## ADDED Requirements

### Requirement: Derive customer_name from namespace
The system SHALL extract `customer_name` from the ArgoCD application namespace. The namespace follows the convention `{org}` or `{org}-{environment}`. The customer name is the portion before the first `-{env}` suffix. If no known environment suffix is present, the entire namespace is the customer name.

Known environment suffixes: `prod`, `accept`, `acc`, `staging`, `dev`, `test`, `uat`.

#### Scenario: Namespace is org only
- **WHEN** namespace is `acme`
- **THEN** `customer_name` is `acme` and `environment` is empty string

#### Scenario: Namespace includes prod suffix
- **WHEN** namespace is `acme-prod`
- **THEN** `customer_name` is `acme` and `environment` is `prod`

#### Scenario: Namespace includes accept suffix
- **WHEN** namespace is `acme-accept`
- **THEN** `customer_name` is `acme` and `environment` is `accept`

#### Scenario: Namespace includes multi-part org name with env suffix
- **WHEN** namespace is `big-corp-staging`
- **THEN** `customer_name` is `big-corp` and `environment` is `staging`

#### Scenario: Namespace suffix is not a known environment token
- **WHEN** namespace is `acme-internal`
- **THEN** `customer_name` is `acme-internal` and `environment` is empty string

---

### Requirement: Derive environment from namespace
The system SHALL extract `environment` from the ArgoCD application namespace using the same suffix-detection logic as `customer_name`. The value SHALL be the matched environment token, or an empty string if no known token is found.

#### Scenario: Known env suffix present
- **WHEN** namespace ends with a known environment suffix (e.g. `-prod`)
- **THEN** `environment` column contains that suffix value

#### Scenario: No known env suffix
- **WHEN** namespace has no recognised environment suffix
- **THEN** `environment` column is empty string

---

### Requirement: Derive is_frontend from app-type label
The system SHALL set `is_frontend` to `true` when the ArgoCD application has the label `app-type=frontend`, and `false` otherwise.

#### Scenario: app-type label is frontend
- **WHEN** ArgoCD application has label `app-type=frontend`
- **THEN** `is_frontend` is `true`

#### Scenario: app-type label is not frontend
- **WHEN** ArgoCD application has label `app-type=backend` or no `app-type` label
- **THEN** `is_frontend` is `false`
