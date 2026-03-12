## Context

`gws` resolves credentials in this order:
1. `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` env var → reads from that file path
2. Encrypted keyring at `~/.config/gws/credentials.enc`

In-cluster there is no keyring. Setting `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` to a mounted Secret file bypasses the keyring entirely. `gws auth export` produces exactly the right format (`authorized_user` JSON with `client_id`, `client_secret`, `refresh_token`, `type`).

The CronJob also needs `kubectl` to exec into Nextcloud pods. Currently the image has Python + gws but no kubectl.

## Goals / Non-Goals

**Goals:**
- CronJob runs fully in-cluster with no human interaction.
- `kubectl exec` works from inside the pod via the existing RBAC.
- gws authenticates via mounted credentials file, no keyring.

**Non-Goals:**
- Automating credential rotation (refresh tokens are long-lived; manual re-export when revoked).
- Migrating to a service account for Sheets auth — OAuth2 user credentials are what's already set up.

## Decisions

### D1 — Store gws OAuth credentials in the existing Secret

**Decision:** Add `gws-oauth.json` as a key in `argocd-sheets-sync-secret` alongside the existing keys. Mount it at `/secrets/gws-oauth.json`.

**Why:** Reuses the existing Secret and volume mount pattern already in `cronjob.yaml`. Keeps all credentials in one place.

---

### D2 — Install kubectl via official binary in Dockerfile

**Decision:** Download the kubectl binary from `dl.k8s.io` during the Docker build, pinned to a specific version. Add only when `INSTALL_KUBECTL=true` build arg is set, keeping the local-mode image lean.

**Why:** `apt`/`dnf` kubectl packages lag behind releases. The official binary is the most reliable source. Pinning the version prevents unexpected upgrades.

**Alternative considered:** Install via package manager. Rejected — adds complexity and a package repo to the image.

---

### D3 — Remove KUBECONFIG from CronJob env

**Decision:** Remove `KUBECONFIG` from both the Secret and the CronJob manifest. In-cluster, `kubectl` automatically uses the ServiceAccount token at `/var/run/secrets/kubernetes.io/serviceaccount/`.

**Why:** `KUBECONFIG` pointing to a local file path is meaningless inside the pod. Removing it prevents confusion and ensures kubectl falls back to in-cluster config.

## Risks / Trade-offs

- **[Risk] OAuth refresh token revoked** → sync fails silently until re-exported. **Mitigation:** failure is logged to the job journal; set up a Prometheus alert on CronJob failure (future work).
- **[Risk] kubectl version skew** → if the cluster upgrades, a pinned kubectl may be too old. **Mitigation:** pin to the cluster's current minor version; update as part of cluster upgrades.

## Migration Plan

1. Export gws credentials: `gws auth export 2>/dev/null > /tmp/gws-oauth.json`
2. Recreate the Secret adding `gws-oauth.json`.
3. Build and push the new image with `INSTALL_KUBECTL=true`.
4. Apply updated `cronjob.yaml`.
5. Apply RBAC: `kubectl apply -f k8s/clusterrole.yaml -f k8s/clusterrolebinding.yaml`
6. Trigger manual job: `kubectl create job --from=cronjob/argocd-sheets-sync argocd-sheets-sync-test -n argocd`
7. Verify logs: `kubectl logs -f job/argocd-sheets-sync-test -n argocd`

## Open Questions

- Which kubectl minor version to pin? Should match the cluster's current version. Run `kubectl version` to confirm.
