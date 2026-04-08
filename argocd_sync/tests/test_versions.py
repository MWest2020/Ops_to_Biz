"""Unit tests for versions.py — _resolve_target."""

from versions import _resolve_target


class TestResolveTarget:
    def test_env_in_namespace(self):
        # noordwijk-prod namespace → deployment = "nextcloud"
        row = {"customer_name": "noordwijk", "environment": "prod",
               "nextcloud_namespace": "noordwijk-prod", "nextcloud_app_name": "noordwijk-prod-nextcloud"}
        ns, deploy = _resolve_target(row)
        assert ns == "noordwijk-prod"
        assert deploy == "nextcloud"

    def test_org_only_namespace(self):
        # beek namespace → deployment = full app name
        row = {"customer_name": "beek", "environment": "accept",
               "nextcloud_namespace": "beek", "nextcloud_app_name": "beek-accept-nextcloud"}
        ns, deploy = _resolve_target(row)
        assert ns == "beek"
        assert deploy == "beek-accept-nextcloud"

    def test_accept_env_in_namespace(self):
        # epe-accept namespace → deployment = "nextcloud"
        row = {"customer_name": "epe", "environment": "accept",
               "nextcloud_namespace": "epe-accept", "nextcloud_app_name": "epe-accept-nextcloud"}
        ns, deploy = _resolve_target(row)
        assert ns == "epe-accept"
        assert deploy == "nextcloud"
