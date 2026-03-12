## Why

The k8s CronJob cannot use the laptop's user keyring. The systemd timer is interim. `gws auth export` produces a portable `authorized_user` JSON file (`client_id`, `client_secret`, `refresh_token`, `type`) that gws accepts via `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` — no keyring required. Storing this in a k8s Secret gives the CronJob everything it needs to run fully in-cluster, taking the human out of the loop.

## What Changes

- `gws auth export` output is stored as a k8s Secret key alongside the existing ArgoCD and Sheets credentials.
- `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` is re-added to the CronJob env, pointing to the mounted credentials file.
- `KUBECONFIG` env var is removed from the CronJob — kubectl uses in-cluster ServiceAccount token automatically.
- The existing `k8s/clusterrole.yaml` and `k8s/clusterrolebinding.yaml` (from `nextcloud-app-versions`) are applied to grant the CronJob pod exec access.
- `kubectl` is added to the container image (currently missing).
- The CronJob is tested with a manual job trigger.

## Capabilities

### New Capabilities

- `in-cluster-gws-auth`: Export OAuth credentials to a file, store in k8s Secret, mount into CronJob, configure `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE`.
- `in-cluster-kubectl`: Add `kubectl` to the Dockerfile so the CronJob pod can exec into Nextcloud pods.

### Modified Capabilities

*(none)*

## Impact

- `k8s/secret` — add `gws-oauth.json` key (operator step, not in git).
- `k8s/cronjob.yaml` — add `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` env + volume mount; remove `KUBECONFIG`; add `kubectl` install to Dockerfile.
- `Dockerfile` — install `kubectl` binary.
- `README.md` — add k8s deployment section update with secret creation command.
