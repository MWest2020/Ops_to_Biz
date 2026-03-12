## ADDED Requirements

### Requirement: Service unit runs sync.sh with project environment
The system SHALL provide a systemd user service unit that executes `sync.sh` with the project `.env` loaded as environment variables.

#### Scenario: Service runs successfully
- **WHEN** the service is started
- **THEN** `sync.sh` executes and output is captured in the user journal

#### Scenario: Service fails
- **WHEN** `sync.sh` exits non-zero
- **THEN** the failure is recorded in the journal; no automatic retry

---

### Requirement: Timer fires nightly at 06:00
The system SHALL provide a systemd user timer that activates the service daily at 06:00 with up to 5 minutes of random delay.

#### Scenario: Timer triggers at scheduled time
- **WHEN** the system clock reaches 06:00 local time
- **THEN** the service unit is started within 5 minutes

---

### Requirement: Install requires no root
The system SHALL install units to `~/.config/systemd/user/` and enable them via `systemctl --user`. No `sudo` is required.

#### Scenario: make install succeeds without root
- **WHEN** `make install` is run as a normal user
- **THEN** units are copied, enabled, and the timer is started
