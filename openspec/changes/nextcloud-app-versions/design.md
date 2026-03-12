## Context

Each Business row represents a customer+environment combination. For rows with `nextcloud=True`, we can exec into the Nextcloud pod and call `php occ app:list --output=json`. The output lists all installed apps and their versions.

Two k8s namespace/deployment naming conventions exist:

| Namespace type | Example | Deployment |
|---|---|---|
| `{org}` (env in app name) | `beek` | `beek-accept-nextcloud` (= ArgoCD app name) |
| `{org}-{env}` | `noordwijk-prod` | `nextcloud` |

Rule: if `environment` column is empty → namespace = `customer_name`, deployment = ArgoCD app name stored in the row; if `environment` is set → namespace = `{customer_name}-{environment}`, deployment = `nextcloud`.

## Goals / Non-Goals

**Goals:**
- Fetch versions for `opencatalogi`, `openregister`, `openconnector` per Business row where `nextcloud=True`.
- Add version columns to Business sheet output.
- Provide RBAC manifests for in-cluster execution.

**Non-Goals:**
- Fetching versions for non-Nextcloud rows.
- Fetching all installed apps — only the three target apps.
- Version history or change tracking.

## Decisions

### D1 — Deployment name resolution

**Decision:** The Business pivot row already carries `customer_name` and `environment`. Namespace and deployment are resolved as:
```python
if environment:
    namespace = f"{customer_name}-{environment}"
    deployment = "nextcloud"
else:
    namespace = customer_name
    deployment = f"{customer_name}-{env_from_app}-nextcloud"  # stored in pivot
```

To support this, `pivot()` in `transform.py` stores the resolved `nextcloud_namespace` and `nextcloud_deployment` on each row.

**Why:** Avoids a second ArgoCD API call. All information is already in the fetched rows.

---

### D2 — exec target: deployment (not pod name)

**Decision:** Use `kubectl exec deploy/{deployment} -n {namespace}` rather than targeting a specific pod.

**Why:** Pod names change on restart. Targeting the deployment is stable and kubectl picks a running pod automatically.

---

### D3 — Graceful failure per row

**Decision:** If the exec fails (pod not ready, app not installed, RBAC error), the version columns for that row are set to empty string. The sync continues. Errors are logged to stderr.

**Why:** A single unavailable pod should not abort the entire sync. The sheet shows blank for that row — visible to management as "unknown".

---

### D4 — In-cluster vs local kubeconfig

**Decision:** Use the `KUBECONFIG` env var when set (local development). In-cluster, kubectl automatically uses the ServiceAccount token mounted at `/var/run/secrets/kubernetes.io/serviceaccount/`.

**Why:** Standard kubectl behaviour — no code branching needed.

---

### D5 — RBAC: ClusterRole scoped to exec only

**Decision:** Grant `get`, `list` on `pods` and `create` on `pods/exec` across all namespaces. No other permissions.

**Why:** Least privilege. The sync only needs to find pods and exec into them.

## Risks / Trade-offs

- **[Risk] occ exec adds latency** — 190 apps, but only ~50-60 nextcloud rows. Each exec takes ~1-3s. Total added time: ~1-3 minutes. Acceptable for a daily sync. **Mitigation:** Run execs concurrently with `concurrent.futures.ThreadPoolExecutor`.
- **[Risk] ClusterRole grants exec across all namespaces** — broad but minimal. **Mitigation:** Document explicitly; consider namespace-scoped Roles if customer list is stable.

## Open Questions

- ~~What is the exact app name key in `occ app:list` output?~~ **Confirmed:** `opencatalogi`, `openregister`, `openconnector` — all under `enabled` in the JSON output.
- Command: `su -s /bin/bash www-data -c 'php occ app:list --output=json'` — `--output=json` must be inside the quoted string.
- Container name inside the pod is `nextcloud` — must specify `-c nextcloud` on exec.
