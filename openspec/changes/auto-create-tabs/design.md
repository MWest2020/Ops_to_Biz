## Context

The gws `values.clear` and `values.batchUpdate` calls both fail with 400 if the tab doesn't exist. The fix is a lightweight existence check + conditional create before every write operation.

## Goals / Non-Goals

**Goals:**
- Auto-create missing tabs so the sync is fully self-sufficient.

**Non-Goals:**
- Managing tab order, colours, or formatting.
- Deleting tabs.

## Decisions

### D1 — Check via spreadsheets.get, create via batchUpdate addSheet

**Decision:** Call `gws sheets spreadsheets get` with `--params {"spreadsheetId": ..., "fields": "sheets.properties.title"}` to get the list of existing tab titles. If the target tab is not in the list, call `batchUpdate` with `addSheet`.

**Why:** Single read before each write. The `fields` filter keeps the response small.

## Risks / Trade-offs

- **[Risk]** Race condition if two jobs run simultaneously and both try to create the same tab. Mitigated by `concurrencyPolicy: Forbid` on the CronJob.
