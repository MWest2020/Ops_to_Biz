#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMP_FILE="$(mktemp /tmp/argocd_new_rows_XXXXXX.json)"
ENRICHED_FILE="$(mktemp /tmp/argocd_enriched_XXXXXX.json)"
trap 'rm -f "$TMP_FILE" "$ENRICHED_FILE"' EXIT

# Soft-fail wrapper: log a one-line skip message and exit 0 on transient
# failures (network, stale gws auth, ArgoCD blip). Audit trail stays in
# journald; we just don't want pipefail traces or OnFailure broadcasts.
skip_if_failed() {
  local step="$1"
  local rc="$2"
  if [ "$rc" -ne 0 ]; then
    echo "[sync] SKIP: ${step} exited ${rc} — likely transient (network/auth). See journal for trace."
    exit 0
  fi
}

echo "[sync] Fetching ArgoCD application data..."
set +e
python3 "$SCRIPT_DIR/fetch.py" > "$TMP_FILE"
rc=$?
set -e
skip_if_failed "fetch.py" "$rc"

APP_COUNT="$(python3 -c "import json,sys; print(len(json.load(open('$TMP_FILE'))))")"
echo "[sync] Fetched ${APP_COUNT} apps."

echo "[sync] Enriching with Nextcloud storage usage..."
set +e
python3 "$SCRIPT_DIR/enrich.py" "$TMP_FILE" "$ENRICHED_FILE"
rc=$?
set -e
skip_if_failed "enrich.py" "$rc"

OUTPUT_MODE="${OUTPUT_MODE:-local}"
BUSINESS_OUTPUT="${BUSINESS_OUTPUT:-}"

case "$OUTPUT_MODE" in
  local)
    echo "[sync] Mode: local (.xlsx)"
    set +e
    python3 "$SCRIPT_DIR/output/local.py" "$ENRICHED_FILE"
    rc=$?
    set -e
    skip_if_failed "output/local.py" "$rc"
    ;;
  gws)
    echo "[sync] Mode: gws (Google Sheets)"
    set +e
    python3 "$SCRIPT_DIR/output/gws.py" "$ENRICHED_FILE"
    rc=$?
    set -e
    skip_if_failed "output/gws.py" "$rc"
    ;;
  *)
    echo "[sync] ERROR: Unknown OUTPUT_MODE '${OUTPUT_MODE}'. Use 'local' or 'gws'." >&2
    exit 1
    ;;
esac

# Business view — runs after the ops sync when BUSINESS_OUTPUT is set.
if [ -n "$BUSINESS_OUTPUT" ]; then
  case "$BUSINESS_OUTPUT" in
    local)
      echo "[sync] Business mode: local (.xlsx)"
      set +e
      python3 "$SCRIPT_DIR/output/business_local.py" "$ENRICHED_FILE"
      rc=$?
      set -e
      skip_if_failed "output/business_local.py" "$rc"
      ;;
    gws)
      echo "[sync] Business mode: gws (Google Sheets)"
      set +e
      python3 "$SCRIPT_DIR/output/business_gws.py" "$ENRICHED_FILE"
      rc=$?
      set -e
      skip_if_failed "output/business_gws.py" "$rc"
      ;;
    *)
      echo "[sync] ERROR: Unknown BUSINESS_OUTPUT '${BUSINESS_OUTPUT}'. Use 'local' or 'gws'." >&2
      exit 1
      ;;
  esac
fi

echo "[sync] Done."
