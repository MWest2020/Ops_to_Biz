## Why

Management needs to know which version of each in-house product (opencatalogi, openregister, openconnector) is running per customer per environment. This is the core reconciliation check — subscription vs deployed version.

## What Changes

- For each row in the Business sheet, the sync execs into the Nextcloud pod and runs `php occ app:list --output=json` to retrieve installed app versions.
- Three new columns added to the Business sheet: `opencatalogi`, `openregister`, `openconnector` (version string or empty if not installed).
- A dedicated Kubernetes ServiceAccount with a ClusterRole granting `pods/exec` and `pods` get/list across all customer namespaces is added.
- The CronJob is updated to use this ServiceAccount (replacing the current one with no API access).
- For local development, the sync uses the local kubeconfig.

## Capabilities

### New Capabilities

- `occ-version-fetch`: For each Business row, determine the correct namespace and deployment name, exec into the pod, parse `occ app:list` JSON output, extract versions for the three target apps.
- `k8s-exec-rbac`: ClusterRole + ClusterRoleBinding granting the CronJob ServiceAccount exec access to pods in customer namespaces.

### Modified Capabilities

*(none — Business sheet columns are extended, not changed)*

## Impact

- New file: `k8s/clusterrole.yaml` — grants pods/exec.
- New file: `k8s/clusterrolebinding.yaml` — binds ClusterRole to the existing ServiceAccount.
- `output/business_local.py` and `output/business_gws.py` — extended to accept and write version columns.
- New file: `versions.py` — kubectl exec logic and occ output parsing.
- `transform.py` — `pivot()` result extended with version columns after fetch.
- `sync.sh` — pass kubeconfig path via `KUBECONFIG` env var for local use.
