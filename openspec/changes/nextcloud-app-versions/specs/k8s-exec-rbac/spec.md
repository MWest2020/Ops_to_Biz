## ADDED Requirements

### Requirement: ClusterRole grants pods exec across all namespaces
The system SHALL provide a ClusterRole that grants `get` and `list` on `pods` and `create` on `pods/exec` cluster-wide.

#### Scenario: ClusterRole applied
- **WHEN** `k8s/clusterrole.yaml` is applied
- **THEN** a ClusterRole named `argocd-sheets-sync-exec` exists with the described permissions

---

### Requirement: ClusterRoleBinding binds to the sync ServiceAccount
The system SHALL bind the ClusterRole to the `argocd-sheets-sync` ServiceAccount in the `argocd` namespace.

#### Scenario: Binding applied
- **WHEN** `k8s/clusterrolebinding.yaml` is applied
- **THEN** the ServiceAccount can exec into pods in any namespace
