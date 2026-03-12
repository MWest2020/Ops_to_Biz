## 1. Fix .env for systemd

- [x] 1.1 Replace `KUBECONFIG=~/.kube/config` in `.env` with the full path (systemd does not expand `~`)

## 2. systemd unit files

- [x] 2.1 Create `systemd/argocd-sheets-sync.service` — user service with `EnvironmentFile`, `ExecStart=sync.sh`, `Type=oneshot`
- [x] 2.2 Create `systemd/argocd-sheets-sync.timer` — nightly at 06:00, `RandomizedDelaySec=300`, `WantedBy=timers.target`

## 3. Makefile

- [x] 3.1 Create `Makefile` with targets: `install`, `uninstall`, `run`, `status`, `logs`

## 4. Enable lingering + install

- [x] 4.1 Run `loginctl enable-linger $USER` (one-time, allows user units to run without interactive session)
- [x] 4.2 Run `make install`
- [x] 4.3 Verify with `make status`

## 5. Documentation

- [x] 5.1 Add `Laptop deployment` section to `README.md` with setup steps and make targets
