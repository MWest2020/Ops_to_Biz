# argocd-sheets-sync

Daily sync of ArgoCD application data to a spreadsheet.
Supports two output modes via `OUTPUT_MODE`: **local** (`.xlsx`) and **gws** (Google Sheets).

---

## Project structure

```
fetch.py          ArgoCD API → deduplicated JSON rows
upsert.py         Merge logic (owned columns only; preserves extra columns)
transform.py      Filter, classify and pivot rows into the business view
output/
  local.py        Write ops rows to .xlsx via openpyxl
  gws.py          Read/write ops rows to Google Sheets via gws CLI
  business_local.py  Write business pivot view to .xlsx
  business_gws.py    Write business pivot view to Google Sheets
sync.sh           Entrypoint — runs fetch, ops output, and optional business output
Dockerfile        python:3.12-slim; gws included when INSTALL_GWS=true
requirements.txt  Pinned Python dependencies
k8s/
  serviceaccount.yaml
  configmap.yaml  Non-secret config (OUTPUT_MODE, LOCAL_OUTPUT_PATH)
  cronjob.yaml    Daily 06:00 UTC CronJob, namespace argocd
.env.example      All required/optional environment variables
```

---

## Environment variables

**Secret** (`argocd-sheets-sync-secret`):

| Variable | Required | Description |
|---|---|---|
| `ARGOCD_URL` | yes | Base URL of your ArgoCD instance |
| `ARGOCD_TOKEN` | yes | ArgoCD bearer token (see below) |
| `ARGOCD_LABEL_SELECTORS` | no | Comma-separated label selectors, e.g. `app-type=frontend,app-type=backend`. Omit to fetch all apps. |
| `GOOGLE_SPREADSHEET_ID` | gws mode | ID from the Sheets URL |
| `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` | gws mode | Path to the service account JSON key |

**ConfigMap** (`argocd-sheets-sync-config`):

| Variable | Required | Description |
|---|---|---|
| `OUTPUT_MODE` | yes | `local` or `gws` |
| `LOCAL_OUTPUT_PATH` | local mode | Path for the output `.xlsx` file |

Copy `.env.example` and fill in your values:

```bash
cp .env.example .env
```

---

## ArgoCD token setup

Create a dedicated ArgoCD service account with read-only access:

```bash
# In argocd-cm (or via OIDC) add a local account:
#   accounts.sheets-sync: apiKey

# Generate a token:
argocd account generate-token --account sheets-sync
```

The token needs only `applications, get` permission. Add this to `argocd-rbac-cm`:

```yaml
p, role:sheets-sync-ro, applications, get, */*, allow
g, sheets-sync, role:sheets-sync-ro
```

---

## GCP service account setup (gws mode)

1. Create a service account in GCP:
   ```bash
   gcloud iam service-accounts create argocd-sheets-sync \
     --display-name "ArgoCD Sheets Sync"
   ```

2. Grant it Editor access on the target spreadsheet (via the Sheets UI — share the sheet with the service account's email).

3. Enable the Sheets API on your GCP project:
   ```bash
   gcloud services enable sheets.googleapis.com
   ```

4. Download a JSON key:
   ```bash
   gcloud iam service-accounts keys create gws-credentials.json \
     --iam-account=argocd-sheets-sync@<your-project>.iam.gserviceaccount.com
   ```

5. Store the key in the Kubernetes secret (see below).

> **Security note:** Rotate service account keys regularly and prefer Workload Identity Federation if your cluster supports it, to avoid long-lived key files entirely.

---

## Switching output modes

### local

```bash
export OUTPUT_MODE=local
export LOCAL_OUTPUT_PATH=/tmp/argocd_apps.xlsx
./sync.sh
```

### gws

```bash
export OUTPUT_MODE=gws
export GOOGLE_SPREADSHEET_ID=<id>
export GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE=/path/to/gws-credentials.json
./sync.sh
```

The target tab must be named **`Deployments`** and exist before the first run (gws CLI will error if the tab is missing).

---

## Docker

### local mode (no Node.js)

```bash
docker build -t argocd-sheets-sync:local .
docker run --env-file .env argocd-sheets-sync:local
```

### gws mode (includes Node.js + gws CLI)

```bash
docker build --build-arg INSTALL_GWS=true -t argocd-sheets-sync:gws .
docker run --env-file .env \
  -v /path/to/gws-credentials.json:/secrets/gws-credentials.json:ro \
  argocd-sheets-sync:gws
```

> Pin the image to a digest in production (`image: your-registry/argocd-sheets-sync@sha256:...`).

---

## Kubernetes deployment

### Create the secret

```bash
kubectl create secret generic argocd-sheets-sync-secret \
  --namespace argocd \
  --from-literal=ARGOCD_URL=https://argocd.your-domain.com \
  --from-literal=ARGOCD_TOKEN=<token> \
  --from-literal=ARGOCD_LABEL_SELECTORS=app-type=frontend,app-type=backend \
  --from-literal=GOOGLE_SPREADSHEET_ID=<spreadsheet-id> \
  --from-file=gws-credentials.json=/path/to/gws-credentials.json
```

### Apply manifests

```bash
kubectl apply -f k8s/serviceaccount.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/cronjob.yaml
```

### Trigger a manual run

```bash
kubectl create job --from=cronjob/argocd-sheets-sync argocd-sheets-sync-manual \
  -n argocd
kubectl logs -f job/argocd-sheets-sync-manual -n argocd
```

---

## Namespace convention

Namespaces follow one of two patterns:

| Pattern | Example | Derived customer | Derived environment |
|---|---|---|---|
| `{org}` | `acme` | `acme` | _(empty)_ |
| `{org}-{env}` | `acme-prod` | `acme` | `prod` |

Known environment suffixes: `prod`, `accept`, `acc`, `staging`, `dev`, `test`, `uat`.

If the suffix after the last `-` is not in that list, the full namespace is used as the customer name with no environment.

---

## Upsert behaviour

`upsert.py` owns the following columns — these are updated on every run:

```
customer_name, environment, is_frontend,
name, namespace, cluster, repo_url, target_revision,
sync_status, health_status, last_synced, images, app_type, team, removed_at
```

**Composite key:** rows are matched on `name + namespace`. Two apps with the same name in different namespaces are treated as distinct.

**Soft-delete:** apps no longer returned by ArgoCD have `sync_status` set to `[REMOVED]` and a `removed_at` date written. The row is never deleted. If the app reappears, it is restored automatically.

**Preserved columns:** any extra columns added manually to the sheet (e.g. notes, subscription tier, cost centre) are never overwritten.

---

## Business view

Set `BUSINESS_OUTPUT` to produce a second, management-facing sheet alongside the ops sheet.

| Variable | Required | Description |
|---|---|---|
| `BUSINESS_OUTPUT` | no | `local` or `gws` — enables the business pivot output |
| `BUSINESS_OUTPUT_PATH` | local mode | Path for the business `.xlsx` file |

The business sheet has one row per **customer + environment**, with boolean columns per product:

| customer_name | environment | nextcloud | react | tilburg-ui |
|---|---|---|---|---|
| acato | accept | True | False | False |
| baarn | prod | True | True | False |

**Product detection:** app names are scanned for `nextcloud`, `react` (also `reactfront`), and `tilburg` (also `tilburg-woo-ui`). Apps not matching any of these are excluded (infra, platform tools, etc.).

**Customer and environment** are derived from the app name pattern `{customer}-{env}-{product}`. `[REMOVED]` apps are excluded from this view.

In gws mode the business view writes to a tab named **`Business`** — the `Deployments` tab is untouched.
