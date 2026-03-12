## ADDED Requirements

### Requirement: Classify app by product type from app name
The system SHALL classify each ArgoCD app into one of three canonical product types by checking if a known substring is present in the app name. Apps not matching any type SHALL be excluded from the business view.

| Substring | Canonical type |
|---|---|
| `nextcloud` | `nextcloud` |
| `react` | `react` |
| `tilburg` | `tilburg-ui` |

#### Scenario: App name contains nextcloud
- **WHEN** app name is `acato-accept-nextcloud`
- **THEN** canonical product type is `nextcloud`

#### Scenario: App name contains reactfront
- **WHEN** app name is `baarn-prod-reactfront`
- **THEN** canonical product type is `react`

#### Scenario: App name contains tilburg-woo-ui
- **WHEN** app name is `dimpact-prod-tilburg-woo-ui`
- **THEN** canonical product type is `tilburg-ui`

#### Scenario: App name matches no known product
- **WHEN** app name is `kube-system-something` or `monitoring-agent`
- **THEN** the app is excluded from the business view

---

### Requirement: Extract customer and environment from app name
The system SHALL derive `customer` and `environment` from the app name by scanning segments left-to-right for the first known environment token. Everything before the env token is the customer; the env token is the environment.

Known env tokens: `prod`, `accept`, `acc`, `staging`, `dev`, `test`, `uat`, `preprod`.

#### Scenario: Standard pattern with accept
- **WHEN** app name is `acato-accept-nextcloud`
- **THEN** customer is `acato` and environment is `accept`

#### Scenario: Standard pattern with prod
- **WHEN** app name is `alkmaar-prod-nextcloud`
- **THEN** customer is `alkmaar` and environment is `prod`

#### Scenario: Multi-segment customer name
- **WHEN** app name is `opencatalogi-prod-tilburg-ui`
- **THEN** customer is `opencatalogi` and environment is `prod`

#### Scenario: No env token found in app name
- **WHEN** app name has no recognised env token
- **THEN** customer is derived from namespace and environment is empty string

#### Scenario: REMOVED apps are excluded
- **WHEN** an app row has `sync_status = [REMOVED]`
- **THEN** the app is excluded from the business view
