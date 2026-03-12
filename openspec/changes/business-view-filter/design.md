## Context

The raw fetch produces one row per ArgoCD app. The business view needs one row per customer+environment, with a column per product type. This requires filtering, classifying, and pivoting — none of which belong in the existing ops pipeline.

App names follow the pattern `{customer}-{env}-{product}` (e.g. `acato-accept-nextcloud`, `dimpact-prod-tilburg-woo-ui`). The namespace sometimes encodes the env (`epe-accept`) but often does not (`acato`). The app name is the reliable source for both env and product type in the business view.

## Goals / Non-Goals

**Goals:**
- Filter to only business-relevant apps (nextcloud, react, tilburg-ui).
- Derive customer and environment from the app name.
- Pivot to one row per customer+environment.
- Keep the existing ops pipeline untouched.

**Non-Goals:**
- Replacing the ops sheet — both outputs run independently via `OUTPUT_MODE`.
- Sync status detail in the business view — presence/absence is sufficient.
- Handling product types beyond the three known ones.

## Decisions

### D1 — Parse customer and environment from app name, not namespace

**Decision:** Strip the known product suffix from the app name, then find the first segment matching a known env token. Everything before that segment is the customer name.

```
acato-accept-nextcloud
  → strip 'nextcloud'    → acato-accept
  → find env token       → 'accept' at index 1
  → customer = 'acato', env = 'accept'

dimpact-prod-tilburg-woo-ui
  → strip 'tilburg-woo-ui' → dimpact-prod
  → find env token          → 'prod' at index 1
  → customer = 'dimpact', env = 'prod'
```

**Why:** Namespace-derived env is empty for ~60% of rows (namespace is just `{org}`). The app name always carries the env for business apps.

**Alternative considered:** Use namespace env when available, fall back to app name. Rejected — mixing two sources for the same field creates inconsistency in the pivot key.

---

### D2 — Product type canonicalisation

**Decision:** Map app name substrings to canonical product types:

| Substring in app name | Canonical type |
|---|---|
| `nextcloud` | `nextcloud` |
| `react` (matches `react`, `reactfront`) | `react` |
| `tilburg` (matches `tilburg-ui`, `tilburg-woo-ui`) | `tilburg-ui` |

Apps not matching any of these are excluded from the business view entirely.

**Why:** The three products map cleanly onto distinct substrings with no ambiguity. Using substring matching (not exact suffix match) handles all variants without an exhaustive list.

---

### D3 — Pivot key is customer + environment

**Decision:** One row per `(customer, environment)` pair. Product columns are boolean (`True`/`False`).

**Why:** A customer with both accept and prod deployments needs two rows to give management a clear accept vs prod status split. Collapsing to one row per customer would require multi-value cells, which are harder to filter/sort in Sheets.

---

### D4 — Separate output mode `business`, separate tab `Business`

**Decision:** `OUTPUT_MODE=business` runs `output/business.py`, which writes to a `Business` tab (gws) or a separate file (local). The existing `Deployments` tab/file is untouched.

**Why:** The two views serve different audiences and update independently. Merging them into one sheet would complicate both.

## Risks / Trade-offs

- **[Risk] New product types go untracked silently** → If a new product is deployed that doesn't match the three known substrings, it simply won't appear. **Mitigation:** Document the known product list; operators add new entries to `transform.py` when a new product is introduced.
- **[Risk] Customer name parsed incorrectly if org name contains an env token** → An org named `prod-something` would be misclassified. **Mitigation:** Env token matching scans left-to-right and stops at the first match; org names containing env tokens would need to be handled as edge cases if they arise.

## Open Questions

- Should `[REMOVED]` apps be excluded from the business view, or shown as a blank cell (product not deployed)? Proposed: exclude — blank and removed look the same; removed is ops concern.
