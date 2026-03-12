## 1. Export credentials

- [ ] 1.1 Export gws OAuth credentials: `gws auth export 2>/dev/null > /tmp/gws-oauth.json`
- [ ] 1.2 Verify the file contains `client_id`, `client_secret`, `refresh_token`, `type`

## 2. Recreate the k8s Secret

- [ ] 2.1 Delete and recreate `argocd-sheets-sync-secret` adding `--from-file=gws-oauth.json=/tmp/gws-oauth.json`; remove `OUTPUT_MODE` and `LOCAL_OUTPUT_PATH` (now in ConfigMap)
- [ ] 2.2 Shred the temp file: `shred -u /tmp/gws-oauth.json`

## 3. Dockerfile — add kubectl

- [ ] 3.1 Add `ARG INSTALL_KUBECTL=false` and a conditional install block: download `https://dl.k8s.io/release/v1.35.0/bin/linux/amd64/kubectl`, verify checksum, install to `/usr/local/bin/`

## 4. Update cronjob.yaml

- [ ] 4.1 Add `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` env var pointing to `/secrets/gws-oauth.json`
- [ ] 4.2 Add `gws-oauth.json` item to the existing `gws-credentials` volume mount
- [ ] 4.3 Remove `KUBECONFIG` env var (not needed in-cluster)

## 5. Apply RBAC + deploy

- [ ] 5.1 `kubectl apply -f k8s/clusterrole.yaml -f k8s/clusterrolebinding.yaml`
- [ ] 5.2 Build and push image with `INSTALL_KUBECTL=true`
- [ ] 5.3 Apply: `kubectl apply -f k8s/configmap.yaml -f k8s/cronjob.yaml`

## 6. Verify

- [ ] 6.1 Trigger manual run: `kubectl create job --from=cronjob/argocd-sheets-sync argocd-sheets-sync-test -n argocd`
- [ ] 6.2 Tail logs: `kubectl logs -f job/argocd-sheets-sync-test -n argocd`
- [ ] 6.3 Confirm both Deployments and Business sheets updated
- [ ] 6.4 Once verified, decommission the systemd timer: `make uninstall`

## 7. Documentation

- [ ] 7.1 Update `README.md` secret creation command to include `gws-oauth.json`
- [ ] 7.2 Document the credential rotation procedure (re-export + secret update)
