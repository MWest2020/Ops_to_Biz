## 1. Confirm app names

- [x] 1.1 Exec into a live Nextcloud pod and run `php occ app:list --output=json | python3 -m json.tool` to confirm the exact key names for opencatalogi, openregister, openconnector

## 2. RBAC manifests

- [x] 2.1 Create `k8s/clusterrole.yaml` — ClusterRole `argocd-sheets-sync-exec` with `pods` get/list and `pods/exec` create
- [x] 2.2 Create `k8s/clusterrolebinding.yaml` — bind to `argocd-sheets-sync` ServiceAccount in `argocd` namespace

## 3. versions.py

- [x] 3.1 Create `versions.py` with `_resolve_target(row)` → `(namespace, deployment)` using the two-convention rule
- [x] 3.2 Implement `fetch_versions(row)` → dict with keys `opencatalogi`, `openregister`, `openconnector`; runs `kubectl exec deploy/{deployment} -n {namespace} -- php occ app:list --output=json`; returns empty strings on failure
- [x] 3.3 Implement `enrich_with_versions(rows)` → runs `fetch_versions` concurrently via `ThreadPoolExecutor`; merges version dicts into each row
- [x] 3.4 Write unit tests for `_resolve_target` covering both namespace conventions

## 4. Wire into sync

- [x] 4.1 In `output/business_local.py`: after `pivot()`, call `enrich_with_versions()`; add `opencatalogi`, `openregister`, `openconnector` to `HEADERS`
- [x] 4.2 In `output/business_gws.py`: same — call `enrich_with_versions()` and extend headers
- [x] 4.3 Add `KUBECONFIG` to `.env.example` with comment (for local use; not needed in-cluster)

## 5. Deploy RBAC

- [x] 5.1 Apply manifests: `kubectl apply -f k8s/clusterrole.yaml -f k8s/clusterrolebinding.yaml`
- [x] 5.2 Update `README.md` with the new RBAC manifests and `KUBECONFIG` env var
