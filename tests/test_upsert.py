"""Unit tests for upsert.py — composite key, soft-delete, restore."""

import pytest
from upsert import upsert, _REMOVED_STATUS


def _row(name: str, namespace: str, sync_status: str = "Synced", **kwargs) -> dict:
    return {
        "customer_name": namespace.split("-")[0],
        "environment": "",
        "is_frontend": False,
        "name": name,
        "namespace": namespace,
        "cluster": "https://kubernetes.default.svc",
        "repo_url": "https://git.example.com/repo",
        "target_revision": "HEAD",
        "sync_status": sync_status,
        "health_status": "Healthy",
        "last_synced": "2026-01-01T00:00:00Z",
        "images": "",
        "app_type": "",
        "team": "",
        "removed_at": "",
        **kwargs,
    }


# ---------------------------------------------------------------------------
# Composite key
# ---------------------------------------------------------------------------

class TestCompositeKey:
    def test_same_name_different_namespace_produces_two_rows(self):
        current = []
        new = [_row("app", "acme-prod"), _row("app", "acme-accept")]
        result = upsert(current, new)
        assert len(result) == 2
        namespaces = {r["namespace"] for r in result}
        assert namespaces == {"acme-prod", "acme-accept"}

    def test_same_name_same_namespace_updates_in_place(self):
        current = [_row("app", "acme-prod", sync_status="OutOfSync")]
        new = [_row("app", "acme-prod", sync_status="Synced")]
        result = upsert(current, new)
        assert len(result) == 1
        assert result[0]["sync_status"] == "Synced"

    def test_new_app_is_appended(self):
        current = [_row("app-a", "acme-prod")]
        new = [_row("app-a", "acme-prod"), _row("app-b", "acme-prod")]
        result = upsert(current, new)
        assert len(result) == 2

    def test_extra_column_preserved(self):
        current = [_row("app", "acme-prod", notes="keep this")]
        new = [_row("app", "acme-prod", sync_status="Synced")]
        result = upsert(current, new)
        assert result[0].get("notes") == "keep this"


# ---------------------------------------------------------------------------
# Soft-delete
# ---------------------------------------------------------------------------

class TestSoftDelete:
    def test_missing_app_is_marked_removed(self):
        current = [_row("app", "acme-prod")]
        new = []
        result = upsert(current, new)
        assert result[0]["sync_status"] == _REMOVED_STATUS
        assert result[0]["removed_at"] != ""

    def test_already_removed_app_is_not_double_dated(self):
        original_date = "2026-01-01"
        current = [_row("app", "acme-prod", sync_status=_REMOVED_STATUS, removed_at=original_date)]
        new = []
        result = upsert(current, new)
        assert result[0]["sync_status"] == _REMOVED_STATUS
        assert result[0]["removed_at"] == original_date

    def test_present_app_is_not_soft_deleted(self):
        current = [_row("app", "acme-prod")]
        new = [_row("app", "acme-prod")]
        result = upsert(current, new)
        assert result[0]["sync_status"] != _REMOVED_STATUS


# ---------------------------------------------------------------------------
# Restore
# ---------------------------------------------------------------------------

class TestRestore:
    def test_removed_app_reappearing_is_restored(self):
        current = [_row("app", "acme-prod", sync_status=_REMOVED_STATUS, removed_at="2026-01-01")]
        new = [_row("app", "acme-prod", sync_status="Synced")]
        result = upsert(current, new)
        assert result[0]["sync_status"] == "Synced"
        assert result[0]["removed_at"] == ""
