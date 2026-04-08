#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMP_FILE="$(mktemp /tmp/argocd_new_rows_XXXXXX.json)"
trap 'rm -f "$TMP_FILE"' EXIT

echo "[sync] Fetching ArgoCD application data..."
python3 "$SCRIPT_DIR/fetch.py" > "$TMP_FILE"

APP_COUNT="$(python3 -c "import json,sys; print(len(json.load(open('$TMP_FILE'))))")"
echo "[sync] Fetched ${APP_COUNT} apps."

OUTPUT_MODE="${OUTPUT_MODE:-local}"
BUSINESS_OUTPUT="${BUSINESS_OUTPUT:-}"

case "$OUTPUT_MODE" in
  local)
    echo "[sync] Mode: local (.xlsx)"
    python3 "$SCRIPT_DIR/output/local.py" "$TMP_FILE"
    ;;
  gws)
    echo "[sync] Mode: gws (Google Sheets)"
    python3 "$SCRIPT_DIR/output/gws.py" "$TMP_FILE"
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
      python3 "$SCRIPT_DIR/output/business_local.py" "$TMP_FILE"
      ;;
    gws)
      echo "[sync] Business mode: gws (Google Sheets)"
      python3 "$SCRIPT_DIR/output/business_gws.py" "$TMP_FILE"
      ;;
    *)
      echo "[sync] ERROR: Unknown BUSINESS_OUTPUT '${BUSINESS_OUTPUT}'. Use 'local' or 'gws'." >&2
      exit 1
      ;;
  esac
fi

echo "[sync] Done."
