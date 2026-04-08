"""Unit tests for transform.py — classify, parse_app_name, pivot."""

import pytest
from transform import classify, parse_app_name, pivot, PRODUCT_COLUMNS


# ---------------------------------------------------------------------------
# classify
# ---------------------------------------------------------------------------

class TestClassify:
    def test_nextcloud(self):
        assert classify("acato-accept-nextcloud") == "nextcloud"

    def test_reactfront(self):
        assert classify("baarn-prod-reactfront") == "react"

    def test_react(self):
        assert classify("epe-accept-react") == "react"

    def test_tilburg_ui(self):
        assert classify("opencatalogi-prod-tilburg-ui") == "tilburg-ui"

    def test_tilburg_woo_ui(self):
        assert classify("dimpact-prod-tilburg-woo-ui") == "tilburg-ui"

    def test_nc_prefix_is_nextcloud(self):
        assert classify("nc-epe-accept") == "nextcloud"

    def test_nc_prefix_multi_segment(self):
        assert classify("nc-vng-backend-accept") == "nextcloud"

    def test_no_match_returns_none(self):
        assert classify("kube-system-something") is None

    def test_monitoring_returns_none(self):
        assert classify("monitoring-agent") is None


# ---------------------------------------------------------------------------
# parse_app_name
# ---------------------------------------------------------------------------

class TestParseAppName:
    def test_standard_accept(self):
        assert parse_app_name("acato-accept-nextcloud") == ("acato", "accept")

    def test_standard_prod(self):
        assert parse_app_name("alkmaar-prod-nextcloud") == ("alkmaar", "prod")

    def test_multi_segment_customer(self):
        assert parse_app_name("opencatalogi-prod-tilburg-ui") == ("opencatalogi", "prod")

    def test_preprod(self):
        assert parse_app_name("tilburg-preprod-prod-nextcloud") == ("tilburg", "preprod")

    def test_no_env_token_uses_fallback(self):
        customer, env = parse_app_name("some-unknown-app", fallback_customer="ns-customer")
        assert customer == "ns-customer"
        assert env == ""

    def test_reactfront(self):
        assert parse_app_name("baarn-prod-reactfront") == ("baarn", "prod")

    def test_nc_prefix_simple(self):
        assert parse_app_name("nc-epe-accept") == ("epe", "accept")

    def test_nc_prefix_multi_segment_customer(self):
        assert parse_app_name("nc-vng-backend-accept") == ("vng-backend", "accept")

    def test_nc_prefix_prod(self):
        assert parse_app_name("nc-debilt-prod") == ("debilt", "prod")


# ---------------------------------------------------------------------------
# pivot
# ---------------------------------------------------------------------------

def _row(name, namespace="acato", sync_status="Synced"):
    return {
        "name": name,
        "namespace": namespace,
        "customer_name": namespace,
        "sync_status": sync_status,
    }


class TestPivot:
    def test_single_product(self):
        rows = [_row("acato-accept-nextcloud", "acato")]
        result = pivot(rows)
        assert len(result) == 1
        assert result[0]["customer_name"] == "acato"
        assert result[0]["environment"] == "accept"
        assert result[0]["nextcloud"] is True
        assert result[0]["react"] is False
        assert result[0]["tilburg-ui"] is False

    def test_multiple_products_same_env(self):
        rows = [
            _row("baarn-prod-nextcloud", "baarn"),
            _row("baarn-prod-reactfront", "baarn"),
        ]
        result = pivot(rows)
        assert len(result) == 1
        assert result[0]["nextcloud"] is True
        assert result[0]["react"] is True

    def test_same_product_two_envs_produces_two_rows(self):
        rows = [
            _row("noordwijk-accept-nextcloud", "noordwijk"),
            _row("noordwijk-prod-nextcloud", "noordwijk"),
        ]
        result = pivot(rows)
        assert len(result) == 2
        envs = {r["environment"] for r in result}
        assert envs == {"accept", "prod"}

    def test_removed_apps_excluded(self):
        rows = [_row("acato-accept-nextcloud", "acato", sync_status="[REMOVED]")]
        assert pivot(rows) == []

    def test_infra_apps_excluded(self):
        rows = [_row("kube-system-coredns", "kube-system")]
        assert pivot(rows) == []

    def test_nc_prefix_creates_nextcloud_row(self):
        rows = [_row("nc-epe-accept", "epe-accept")]
        result = pivot(rows)
        assert len(result) == 1
        assert result[0]["customer_name"] == "epe"
        assert result[0]["environment"] == "accept"
        assert result[0]["nextcloud"] is True
        assert result[0]["nextcloud_app_name"] == "nc-epe-accept"
        assert result[0]["nextcloud_namespace"] == "epe-accept"

    def test_nc_and_legacy_same_customer_different_env(self):
        rows = [
            _row("nc-epe-accept", "epe-accept"),
            _row("epe-prod-nextcloud", "epe"),
        ]
        result = pivot(rows)
        assert len(result) == 2
        envs = {r["environment"] for r in result}
        assert envs == {"accept", "prod"}

    def test_sorted_by_customer_then_env(self):
        rows = [
            _row("zwolle-prod-nextcloud", "zwolle"),
            _row("acato-accept-nextcloud", "acato"),
            _row("zwolle-accept-nextcloud", "zwolle"),
        ]
        result = pivot(rows)
        assert result[0]["customer_name"] == "acato"
        assert result[1]["environment"] == "accept"
        assert result[2]["environment"] == "prod"
