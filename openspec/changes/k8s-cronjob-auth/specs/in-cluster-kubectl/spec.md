## ADDED Requirements

### Requirement: kubectl is available inside the CronJob container
The system SHALL install the kubectl binary in the container image when built with `INSTALL_KUBECTL=true`. The binary SHALL be pinned to a specific version matching the cluster's minor version.

#### Scenario: kubectl exec succeeds in-cluster
- **WHEN** the CronJob pod runs `kubectl exec` against a Nextcloud pod
- **THEN** the exec succeeds using the in-cluster ServiceAccount token (no KUBECONFIG required)

#### Scenario: Local-mode image stays lean
- **WHEN** the image is built without `INSTALL_KUBECTL=true`
- **THEN** kubectl is not installed

---

### Requirement: KUBECONFIG is not set in the CronJob
The system SHALL NOT set the `KUBECONFIG` environment variable in the CronJob manifest. kubectl SHALL use in-cluster config automatically.

#### Scenario: kubectl uses in-cluster config
- **WHEN** the pod runs without `KUBECONFIG` set
- **THEN** kubectl reads the ServiceAccount token from `/var/run/secrets/kubernetes.io/serviceaccount/`
