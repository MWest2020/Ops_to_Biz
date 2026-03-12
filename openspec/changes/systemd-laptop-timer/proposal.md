## Why

The k8s CronJob requires in-cluster gws OAuth credentials which aren't yet solved. A systemd user timer on the laptop runs the existing sync nightly with zero new infrastructure — kubeconfig and gws keyring credentials are already present in the user session.

## What Changes

- A systemd **user** service unit (`argocd-sheets-sync.service`) that runs `sync.sh` with the project's `.env` file as its environment source.
- A systemd **user** timer unit (`argocd-sheets-sync.timer`) that triggers nightly at 06:00.
- A `Makefile` with `install`, `uninstall`, `run`, and `status` targets for managing the units.
- Units are installed to `~/.config/systemd/user/` so no root is required.

## Why user units, not system units

`gws` uses the user keyring (`keyring backend: keyring`). A system service runs without a user session and cannot access the keyring. A user service runs within the user's session (with `lingering` enabled) and has full keyring access.

## Capabilities

### New Capabilities

- `systemd-user-timer`: Nightly user systemd timer that runs `sync.sh` via an `EnvironmentFile` pointing to the project `.env`.

### Modified Capabilities

*(none)*

## Impact

- New directory: `systemd/` with `argocd-sheets-sync.service` and `argocd-sheets-sync.timer`.
- New `Makefile` at project root.
- `README.md`: add laptop deployment section.
