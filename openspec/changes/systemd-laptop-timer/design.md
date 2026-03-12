## Context

The sync runs fine interactively. The only missing piece is scheduling. systemd user units are the standard Linux mechanism for per-user scheduled tasks — no cron, no root, no new processes.

Key constraint: `gws` reads OAuth tokens from the user keyring. This works in interactive sessions but fails in system services. User units (with lingering) solve this because they run inside the user's session manager, which initialises the keyring.

## Goals / Non-Goals

**Goals:**
- Nightly automated run at 06:00 local time.
- No root access required.
- Logs available via `journalctl --user`.
- Easy install/uninstall via `make`.

**Non-Goals:**
- Running when the laptop is off or not connected — accepted limitation.
- Retry on failure — single attempt per night, failures visible in journal.
- k8s CronJob replacement — this is interim until OAuth credentials are solved for in-cluster.

## Decisions

### D1 — User unit with EnvironmentFile

**Decision:** Use `EnvironmentFile=%h/projects/Ops_to_Biz/.env` in the service unit. The `%h` specifier expands to the home directory.

**Why:** Keeps secrets out of the unit file. The `.env` file already has all required variables.

**Note:** Lines starting with `#` in the `.env` are ignored by systemd's `EnvironmentFile`. The commented-out `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` line is safe.

---

### D2 — Lingering enabled for keyring access

**Decision:** Document `loginctl enable-linger $USER` as a required setup step. This ensures the user session (and keyring) starts at boot even without an interactive login.

**Why:** Without lingering, user units only run when the user is logged in interactively. With lingering, the user session manager starts at boot.

---

### D3 — OnCalendar=*-*-* 06:00 with RandomizedDelaySec

**Decision:** Timer fires at 06:00 daily with a `RandomizedDelaySec=300` (5 min jitter).

**Why:** Avoids hammering the ArgoCD API and Google Sheets exactly at 06:00 if multiple services are scheduled at the same time.

## Risks / Trade-offs

- **[Risk] Laptop off at 06:00** → sync skipped that night. No catch-up. Acceptable for a cockpit updated daily.
- **[Risk] `.env` tilde in KUBECONFIG** → `KUBECONFIG=~/.kube/config` — systemd does NOT expand `~` in EnvironmentFile values. Must use full path. Document this.
