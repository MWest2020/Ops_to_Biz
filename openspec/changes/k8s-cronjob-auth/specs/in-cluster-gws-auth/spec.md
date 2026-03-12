## ADDED Requirements

### Requirement: gws authenticates via mounted credentials file in-cluster
The system SHALL configure the CronJob to set `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` pointing to a mounted Secret file containing exported OAuth2 credentials. No keyring SHALL be required.

#### Scenario: CronJob authenticates to Google Sheets
- **WHEN** the CronJob pod starts and `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` points to a valid `authorized_user` JSON file
- **THEN** gws authenticates successfully without accessing a keyring

#### Scenario: Credentials file missing
- **WHEN** the mounted file does not exist
- **THEN** gws returns an auth error and the job fails with a non-zero exit code

---

### Requirement: OAuth credentials are stored in the existing k8s Secret
The system SHALL add `gws-oauth.json` as a key in `argocd-sheets-sync-secret`. The file SHALL contain the output of `gws auth export` (format: `authorized_user` JSON).

#### Scenario: Secret contains gws-oauth.json
- **WHEN** the secret is created with `--from-file=gws-oauth.json`
- **THEN** the CronJob pod can mount it at `/secrets/gws-oauth.json`
