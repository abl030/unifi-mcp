#!/usr/bin/env python3
"""Sprint F+G verification test: structured JSON responses, secret redaction,
pagination/fields, and overview tool.

Requires a running UniFi controller (docker-compose.test.yml).
Tests the helper functions and UniFiClient directly (avoids FastMCP tool wrappers).

Run:
    # Start controller first:
    docker compose -f docker-compose.test.yml up -d
    scripts/seed_admin.sh unifi-test-controller admin testpassword123
    # Then:
    uv run --extra test python -m pytest tests/test_sprint_f.py -v
    # Cleanup:
    docker compose -f docker-compose.test.yml down -v
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Setup: configure env vars BEFORE importing the generated server
# ---------------------------------------------------------------------------

os.environ.setdefault("UNIFI_HOST", "127.0.0.1")
os.environ.setdefault("UNIFI_PORT", "8443")
os.environ.setdefault("UNIFI_USERNAME", "admin")
os.environ.setdefault("UNIFI_PASSWORD", "testpassword123")
os.environ.setdefault("UNIFI_SITE", "default")
os.environ.setdefault("UNIFI_VERIFY_SSL", "false")
os.environ.setdefault("UNIFI_REDACT_SECRETS", "true")

# Add generated/ to path so we can import server
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "generated"))

import server as srv  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def parse(result) -> dict:
    """Extract structured dict from a tool result. Accepts dict (direct) or str (JSON)."""
    if isinstance(result, dict):
        return result
    try:
        return json.loads(result)
    except (json.JSONDecodeError, TypeError) as e:
        pytest.fail(f"Tool result is not valid JSON: {e}\nResult: {result!r:.500}")


def assert_structured_list(data: dict):
    """Assert the response follows our structured list JSON format."""
    assert "count" in data, f"List response missing 'count': {list(data.keys())}"
    assert "data" in data, f"List response missing 'data': {list(data.keys())}"
    assert isinstance(data["data"], list), f"'data' should be list, got {type(data['data'])}"
    assert isinstance(data["count"], int), f"'count' should be int, got {type(data['count'])}"


def assert_no_plaintext_secrets(obj: Any, path: str = ""):
    """Recursively check that secret fields have <redacted> values."""
    secret_fields = {
        "x_passphrase", "x_iapp_key", "x_password", "x_shadow",
        "x_private_key", "x_certificate_pem", "x_certificate_arn",
        "x_api_token", "x_mgmt_key", "x_secret", "x_psk",
    }
    secret_substrings = ("password", "passphrase", "secret", "preshared_key")

    if isinstance(obj, dict):
        for k, v in obj.items():
            is_secret = k in secret_fields or any(s in k.lower() for s in secret_substrings)
            if is_secret and v != "<redacted>" and v is not None and v != "":
                pytest.fail(f"Secret field '{k}' at {path}.{k} not redacted: {v!r:.100}")
            assert_no_plaintext_secrets(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            assert_no_plaintext_secrets(item, f"{path}[{i}]")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module", autouse=True)
def check_controller():
    """Skip all tests if controller is not reachable."""
    import httpx

    try:
        with httpx.Client(verify=False, timeout=5.0) as c:
            resp = c.get(f"https://127.0.0.1:{os.environ['UNIFI_PORT']}/status")
            if resp.status_code != 200:
                pytest.skip("UniFi controller not ready (status != 200)")
    except Exception as e:
        pytest.skip(f"UniFi controller not reachable: {e}")


@pytest.fixture(scope="module")
def client():
    """Provide a logged-in UniFiClient, retry login if needed."""
    import time

    cli = srv.UniFiClient()
    for attempt in range(10):
        try:
            asyncio.get_event_loop().run_until_complete(cli.login())
            break
        except Exception:
            if attempt == 9:
                pytest.skip("Could not log in to controller after 10 retries")
            time.sleep(2)

    yield cli
    asyncio.get_event_loop().run_until_complete(cli.close())


# ===========================================================================
# Test: _format_response produces structured JSON
# ===========================================================================


class TestFormatResponse:
    def test_list_format(self):
        result = srv._format_response([{"a": 1}, {"a": 2}], "Found 2 items")
        data = parse(result)
        assert data["summary"] == "Found 2 items"
        assert data["count"] == 2
        assert data["data"] == [{"a": 1}, {"a": 2}]

    def test_single_item_format(self):
        result = srv._format_response({"name": "test"})
        data = parse(result)
        assert data["data"] == {"name": "test"}
        assert "count" not in data

    def test_none_data(self):
        result = srv._format_response(None, "Not found")
        data = parse(result)
        assert data["summary"] == "Not found"
        assert "data" not in data

    def test_empty_list(self):
        result = srv._format_response([], "Found 0 items")
        data = parse(result)
        assert data["count"] == 0
        assert data["data"] == []

    def test_no_summary(self):
        result = srv._format_response([{"x": 1}])
        data = parse(result)
        assert "summary" not in data
        assert data["count"] == 1


# ===========================================================================
# Test: _redact_secrets
# ===========================================================================


class TestRedactSecrets:
    def test_direct_field_names(self):
        data = {"x_passphrase": "my_secret", "name": "Test"}
        result = srv._redact_secrets(data)
        assert result["x_passphrase"] == "<redacted>"
        assert result["name"] == "Test"

    def test_substring_matching(self):
        data = {"admin_password": "secret123", "site_name": "default"}
        result = srv._redact_secrets(data)
        assert result["admin_password"] == "<redacted>"
        assert result["site_name"] == "default"

    def test_nested_dicts(self):
        data = {"config": {"x_password": "pass", "name": "inner"}}
        result = srv._redact_secrets(data)
        assert result["config"]["x_password"] == "<redacted>"
        assert result["config"]["name"] == "inner"

    def test_list_of_dicts(self):
        data = [{"x_secret": "val1"}, {"x_secret": "val2"}]
        result = srv._redact_secrets(data)
        assert result[0]["x_secret"] == "<redacted>"
        assert result[1]["x_secret"] == "<redacted>"

    def test_non_dict_values_unchanged(self):
        assert srv._redact_secrets("hello") == "hello"
        assert srv._redact_secrets(42) == 42
        assert srv._redact_secrets(None) is None

    def test_integration_with_format_response(self):
        """Verify _format_response calls redaction when enabled."""
        data = [{"x_passphrase": "leaked!", "name": "WiFi"}]
        result = srv._format_response(data, "Test")
        parsed = parse(result)
        assert parsed["data"][0]["x_passphrase"] == "<redacted>"
        assert parsed["data"][0]["name"] == "WiFi"


# ===========================================================================
# Test: _paginate_and_filter
# ===========================================================================


class TestPaginateAndFilter:
    def test_no_params(self):
        data = [{"a": 1}, {"a": 2}, {"a": 3}]
        result, missing = srv._paginate_and_filter(data, limit=0, offset=0, fields="")
        assert result == data
        assert missing == []

    def test_limit(self):
        data = [{"a": 1}, {"a": 2}, {"a": 3}]
        result, _ = srv._paginate_and_filter(data, limit=2, offset=0, fields="")
        assert len(result) == 2
        assert result[0]["a"] == 1

    def test_offset(self):
        data = [{"a": 1}, {"a": 2}, {"a": 3}]
        result, _ = srv._paginate_and_filter(data, limit=0, offset=1, fields="")
        assert len(result) == 2
        assert result[0]["a"] == 2

    def test_limit_and_offset(self):
        data = [{"a": i} for i in range(10)]
        result, _ = srv._paginate_and_filter(data, limit=3, offset=2, fields="")
        assert len(result) == 3
        assert result[0]["a"] == 2

    def test_fields(self):
        data = [{"_id": "1", "name": "Test", "extra": "drop"}]
        result, missing = srv._paginate_and_filter(data, limit=0, offset=0, fields="name")
        assert result == [{"_id": "1", "name": "Test"}]
        assert missing == []

    def test_fields_always_includes_id(self):
        data = [{"_id": "1", "name": "Test", "type": "x"}]
        result, _ = srv._paginate_and_filter(data, limit=0, offset=0, fields="name")
        assert "_id" in result[0]

    def test_all_combined(self):
        data = [
            {"_id": str(i), "name": f"item{i}", "extra": "x"}
            for i in range(10)
        ]
        result, _ = srv._paginate_and_filter(data, limit=2, offset=3, fields="name")
        assert len(result) == 2
        assert result[0] == {"_id": "3", "name": "item3"}
        assert result[1] == {"_id": "4", "name": "item4"}

    def test_missing_fields_detected(self):
        """Requesting a field that doesn't exist returns it in missing list."""
        data = [{"_id": "1", "name": "Test", "ip": "10.0.0.1"}]
        result, missing = srv._paginate_and_filter(data, limit=0, offset=0, fields="name,network,vlan")
        assert result == [{"_id": "1", "name": "Test"}]
        assert "network" in missing
        assert "vlan" in missing
        assert "name" not in missing

    def test_missing_fields_empty_when_all_exist(self):
        data = [{"_id": "1", "name": "Test", "ip": "10.0.0.1"}]
        result, missing = srv._paginate_and_filter(data, limit=0, offset=0, fields="name,ip")
        assert missing == []

    def test_missing_fields_in_format_response(self):
        """_format_response includes missing_fields when provided."""
        result = srv._format_response([{"a": 1}], "test", missing_fields=["network", "vlan"])
        assert result["missing_fields"] == ["network", "vlan"]

    def test_no_missing_fields_key_when_empty(self):
        """_format_response omits missing_fields when list is empty."""
        result = srv._format_response([{"a": 1}], "test", missing_fields=[])
        assert "missing_fields" not in result


# ===========================================================================
# Test: Live API calls — Global tools
# ===========================================================================


class TestLiveGlobal:
    def test_status_endpoint(self):
        """GET /status returns structured JSON."""
        import httpx

        with httpx.Client(verify=False, timeout=10.0) as c:
            resp = c.get(f"https://127.0.0.1:{os.environ['UNIFI_PORT']}/status")
            data = resp.json()
            formatted = srv._format_response(data)
            parsed = parse(formatted)
            assert "data" in parsed

    def test_sites(self, client):
        data = asyncio.get_event_loop().run_until_complete(
            client.request("GET", "/api/stat/sites")
        )
        formatted = srv._format_response(data, f"Found {len(data)} sites")
        parsed = parse(formatted)
        assert_structured_list(parsed)
        assert parsed["count"] >= 1


# ===========================================================================
# Test: Live API — REST list with pagination
# ===========================================================================


class TestLiveRESTList:
    def test_list_networks(self, client):
        data = asyncio.get_event_loop().run_until_complete(
            client.request("GET", "rest/networkconf")
        )
        formatted = srv._format_response(data, f"Found {len(data)} networks")
        parsed = parse(formatted)
        assert_structured_list(parsed)
        assert parsed["count"] >= 1  # at least default network

    def test_list_networks_with_fields(self, client):
        data = asyncio.get_event_loop().run_until_complete(
            client.request("GET", "rest/networkconf")
        )
        total = len(data)
        filtered, missing = srv._paginate_and_filter(data, limit=0, offset=0, fields="name,purpose")
        formatted = srv._format_response(filtered, f"Found {total} networks", missing_fields=missing)
        parsed = parse(formatted)
        assert_structured_list(parsed)
        if parsed["data"]:
            record = parsed["data"][0]
            assert "_id" in record
            assert "name" in record
            extra = set(record.keys()) - {"_id", "name", "purpose"}
            assert not extra, f"Extra fields not filtered: {extra}"

    def test_list_networks_limit(self, client):
        data = asyncio.get_event_loop().run_until_complete(
            client.request("GET", "rest/networkconf")
        )
        total = len(data)
        limited, _ = srv._paginate_and_filter(data, limit=1, offset=0, fields="")
        formatted = srv._format_response(limited, f"Found {total} networks")
        parsed = parse(formatted)
        # Summary mentions total
        assert str(total) in parsed["summary"]
        # But data is limited
        assert len(parsed["data"]) <= 1

    def test_list_settings(self, client):
        data = asyncio.get_event_loop().run_until_complete(
            client.request("GET", "rest/setting")
        )
        formatted = srv._format_response(data, f"Found {len(data)} settings")
        parsed = parse(formatted)
        assert_structured_list(parsed)
        assert parsed["count"] > 0


# ===========================================================================
# Test: Live API — CRUD lifecycle
# ===========================================================================


class TestLiveCRUD:
    def test_network_lifecycle(self, client):
        loop = asyncio.get_event_loop()

        # Create
        payload = {"name": "test_sprint_f", "purpose": "vlan-only", "vlan_enabled": True, "vlan": 998}
        created = loop.run_until_complete(
            client.request("POST", "rest/networkconf", json_data=payload)
        )
        assert isinstance(created, list) and len(created) > 0
        net_id = created[0]["_id"]

        try:
            # Format create response
            formatted = srv._format_response(created, "Created network")
            parsed = parse(formatted)
            assert "data" in parsed

            # Get
            got = loop.run_until_complete(
                client.request("GET", f"rest/networkconf/{net_id}")
            )
            formatted = srv._format_response(got[0] if isinstance(got, list) else got)
            parsed = parse(formatted)
            assert "data" in parsed

            # Update
            updated = loop.run_until_complete(
                client.request("PUT", f"rest/networkconf/{net_id}",
                               json_data={"name": "test_sprint_f_updated"})
            )
            formatted = srv._format_response(updated, "Updated network")
            parsed = parse(formatted)
            assert "data" in parsed or "summary" in parsed
        finally:
            # Delete
            loop.run_until_complete(
                client.request("DELETE", f"rest/networkconf/{net_id}")
            )

    def test_dry_run_format(self):
        """Dry-run responses should be structured JSON."""
        preview = {"action": "create_network", "data": {"name": "test"}}
        result = srv._format_response(preview, "DRY RUN: Set confirm=True to execute.")
        parsed = parse(result)
        assert "DRY RUN" in parsed["summary"]
        assert "data" in parsed


# ===========================================================================
# Test: Live API — Stat tools
# ===========================================================================


class TestLiveStat:
    def test_health(self, client):
        data = asyncio.get_event_loop().run_until_complete(
            client.request("GET", "stat/health")
        )
        formatted = srv._format_response(data, f"Found {len(data)} health records")
        parsed = parse(formatted)
        assert_structured_list(parsed)

    def test_sysinfo(self, client):
        data = asyncio.get_event_loop().run_until_complete(
            client.request("GET", "stat/sysinfo")
        )
        formatted = srv._format_response(data, f"Found {len(data)} sysinfo records")
        parsed = parse(formatted)
        assert_structured_list(parsed)

    def test_stat_with_field_selection(self, client):
        data = asyncio.get_event_loop().run_until_complete(
            client.request("GET", "stat/health")
        )
        filtered, missing = srv._paginate_and_filter(data, limit=0, offset=0, fields="subsystem,status")
        formatted = srv._format_response(filtered, f"Found {len(data)} health records", missing_fields=missing)
        parsed = parse(formatted)
        if parsed["data"]:
            record = parsed["data"][0]
            allowed = {"_id", "subsystem", "status"}
            extra = set(record.keys()) - allowed
            assert not extra, f"Fields not filtered: {extra}"


# ===========================================================================
# Test: Live API — Command tools (safe only)
# ===========================================================================


class TestLiveCommands:
    def test_get_admins(self, client):
        data = asyncio.get_event_loop().run_until_complete(
            client.request("POST", "cmd/sitemgr", json_data={"cmd": "get-admins"})
        )
        formatted = srv._format_response(data, "Executed get-admins")
        parsed = parse(formatted)
        assert "data" in parsed or "summary" in parsed

    def test_list_backups(self, client):
        data = asyncio.get_event_loop().run_until_complete(
            client.request("POST", "cmd/backup", json_data={"cmd": "list-backups"})
        )
        formatted = srv._format_response(data, "Executed list-backups")
        parsed = parse(formatted)
        assert "data" in parsed or "summary" in parsed


# ===========================================================================
# Test: Live API — Redaction in real responses
# ===========================================================================


class TestLiveRedaction:
    def test_settings_redacted(self, client):
        """Settings contain x_password and other secrets — verify redaction."""
        data = asyncio.get_event_loop().run_until_complete(
            client.request("GET", "rest/setting")
        )
        formatted = srv._format_response(data, f"Found {len(data)} settings")
        parsed = parse(formatted)
        assert_no_plaintext_secrets(parsed)

    def test_accounts_redacted(self, client):
        """RADIUS accounts may have x_password — verify redaction."""
        data = asyncio.get_event_loop().run_until_complete(
            client.request("GET", "rest/account")
        )
        formatted = srv._format_response(data, f"Found {len(data)} accounts")
        parsed = parse(formatted)
        assert_no_plaintext_secrets(parsed)


# ===========================================================================
# Test: Live API — Overview tool logic
# ===========================================================================


class TestLiveOverview:
    def test_overview_structure(self, client):
        """Test the overview tool logic by calling APIs directly."""
        loop = asyncio.get_event_loop()

        health = loop.run_until_complete(client.request("GET", "stat/health"))
        devices = loop.run_until_complete(client.request("GET", "stat/device"))
        networks = loop.run_until_complete(client.request("GET", "rest/networkconf"))
        wlans = loop.run_until_complete(client.request("GET", "rest/wlanconf"))
        clients = loop.run_until_complete(client.request("GET", "stat/sta"))
        alarms = loop.run_until_complete(client.request("GET", "stat/alarm"))
        sysinfo = loop.run_until_complete(client.request("GET", "stat/sysinfo"))

        version = ""
        if sysinfo and isinstance(sysinfo, list) and sysinfo[0]:
            version = sysinfo[0].get("version", "")

        overview = {
            "controller_version": version,
            "health": {
                h.get("subsystem", "?"): h.get("status", "?")
                for h in health if isinstance(h, dict)
            },
            "device_summary": [
                {"name": d.get("name", ""), "type": d.get("type", ""),
                 "model": d.get("model", ""), "mac": d.get("mac", ""),
                 "status": "connected" if d.get("state") == 1 else "disconnected",
                 "ip": d.get("ip", "")}
                for d in devices if isinstance(d, dict)
            ],
            "network_summary": [
                {"name": n.get("name", ""), "purpose": n.get("purpose", ""),
                 "subnet": n.get("ip_subnet", ""), "vlan": n.get("vlan", None),
                 "enabled": n.get("enabled", True)}
                for n in networks if isinstance(n, dict)
            ],
            "wlan_summary": [
                {"name": w.get("name", ""), "security": w.get("security", ""),
                 "enabled": w.get("enabled", True), "wpa_mode": w.get("wpa_mode", "")}
                for w in wlans if isinstance(w, dict)
            ],
            "total_clients": len(clients) if isinstance(clients, list) else 0,
            "active_alarms": len([
                a for a in alarms
                if isinstance(a, dict) and not a.get("archived")
            ]) if isinstance(alarms, list) else 0,
        }

        formatted = srv._format_response(overview, "Network overview")
        parsed = parse(formatted)

        assert parsed["summary"] == "Network overview"
        assert "data" in parsed
        ov = parsed["data"]
        assert "controller_version" in ov
        assert "health" in ov
        assert "device_summary" in ov
        assert "network_summary" in ov
        assert "wlan_summary" in ov
        assert "total_clients" in ov
        assert "active_alarms" in ov
        assert isinstance(ov["total_clients"], int)
        assert isinstance(ov["active_alarms"], int)
        # Controller version should be present on a running instance
        assert ov["controller_version"], "controller_version should not be empty"
        # Networks should include at least the default network
        assert len(ov["network_summary"]) >= 1


# ===========================================================================
# Test: _paginate_and_filter dot-notation (Issue #15)
# ===========================================================================


class TestPaginateAndFilterDotNotation:
    def test_dot_notation_filters_nested_list(self):
        """Dot notation filters fields within nested list-of-dicts."""
        data = [{"_id": "1", "name": "Switch", "port_table": [
            {"port_idx": 1, "speed": 1000, "stp_state": "forwarding", "poe_power": 5.2},
            {"port_idx": 2, "speed": 100, "stp_state": "disabled", "poe_power": 0},
        ]}]
        result, missing = srv._paginate_and_filter(data, 0, 0, "name,port_table.port_idx,port_table.speed")
        assert result[0]["name"] == "Switch"
        assert len(result[0]["port_table"]) == 2
        assert result[0]["port_table"][0] == {"port_idx": 1, "speed": 1000}
        assert result[0]["port_table"][1] == {"port_idx": 2, "speed": 100}
        assert missing == []

    def test_dot_notation_filters_nested_dict(self):
        """Dot notation filters fields within a nested dict (not array)."""
        data = [{"_id": "1", "config": {"mode": "bridge", "timeout": 30, "debug": True}}]
        result, _ = srv._paginate_and_filter(data, 0, 0, "config.mode,config.timeout")
        assert result[0]["config"] == {"mode": "bridge", "timeout": 30}

    def test_dot_notation_mixed_with_flat(self):
        """Mix of flat fields and dot-notation in same query."""
        data = [{"_id": "1", "name": "AP", "mac": "aa:bb:cc:dd:ee:ff",
                 "radio_table": [{"radio": "ng", "channel": 6}, {"radio": "na", "channel": 36}]}]
        result, _ = srv._paginate_and_filter(data, 0, 0, "name,radio_table.radio")
        assert set(result[0].keys()) == {"_id", "name", "radio_table"}
        assert result[0]["radio_table"][0] == {"radio": "ng"}

    def test_dot_notation_parent_missing(self):
        """Dot notation with parent field that doesn't exist reports it as missing."""
        data = [{"_id": "1", "name": "Test"}]
        result, missing = srv._paginate_and_filter(data, 0, 0, "name,nonexistent.sub")
        assert "nonexistent.sub" in missing

    def test_dot_notation_with_limit_offset(self):
        """Dot notation works together with limit/offset."""
        data = [{"_id": str(i), "ports": [{"idx": i, "extra": "x"}]} for i in range(5)]
        result, _ = srv._paginate_and_filter(data, limit=2, offset=1, fields="ports.idx")
        assert len(result) == 2
        assert result[0]["_id"] == "1"
        assert result[0]["ports"] == [{"idx": 1}]


# ===========================================================================
# Test: _enrich_clients (Issue #14)
# ===========================================================================


class TestEnrichClients:
    """Unit tests for _enrich_clients (mocked client)."""

    def _run(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_enriches_wireless_clients(self):
        """Wireless clients get network_name from WLAN->network lookup."""
        class MockClient:
            async def request(self, method, path, **kw):
                if "wlanconf" in path:
                    return [{"name": "MyWiFi", "networkconf_id": "net1"}]
                if "networkconf" in path:
                    return [{"_id": "net1", "name": "LAN"}]
                return []
        clients = [
            {"_id": "c1", "mac": "aa:bb:cc:dd:ee:ff", "essid": "MyWiFi", "is_wired": False},
        ]
        result = self._run(srv._enrich_clients(MockClient(), clients, None))
        assert result[0]["network_name"] == "LAN"

    def test_skips_wired_clients(self):
        """Wired clients (no essid) are not modified."""
        class MockClient:
            async def request(self, method, path, **kw):
                return []
        clients = [{"_id": "c1", "mac": "aa:bb:cc:dd:ee:ff", "is_wired": True}]
        result = self._run(srv._enrich_clients(MockClient(), clients, None))
        assert "network_name" not in result[0]

    def test_preserves_existing_network_name(self):
        """Clients that already have network_name are not overwritten."""
        class MockClient:
            async def request(self, method, path, **kw):
                return []
        clients = [{"_id": "c1", "essid": "MyWiFi", "network_name": "Already Set"}]
        result = self._run(srv._enrich_clients(MockClient(), clients, None))
        assert result[0]["network_name"] == "Already Set"

    def test_unresolvable_essid(self):
        """Client with essid that doesn't match any WLAN is left without network_name."""
        class MockClient:
            async def request(self, method, path, **kw):
                if "wlanconf" in path:
                    return [{"name": "OtherSSID", "networkconf_id": "net1"}]
                if "networkconf" in path:
                    return [{"_id": "net1", "name": "LAN"}]
                return []
        clients = [{"_id": "c1", "essid": "UnknownSSID"}]
        result = self._run(srv._enrich_clients(MockClient(), clients, None))
        assert "network_name" not in result[0]

    def test_multiple_wlans_multiple_clients(self):
        """Multiple WLANs mapped to different networks enrich correctly."""
        class MockClient:
            async def request(self, method, path, **kw):
                if "wlanconf" in path:
                    return [
                        {"name": "Home", "networkconf_id": "n1"},
                        {"name": "Guest", "networkconf_id": "n2"},
                    ]
                if "networkconf" in path:
                    return [
                        {"_id": "n1", "name": "LAN"},
                        {"_id": "n2", "name": "Guest VLAN"},
                    ]
                return []
        clients = [
            {"_id": "c1", "essid": "Home"},
            {"_id": "c2", "essid": "Guest"},
            {"_id": "c3", "is_wired": True},
        ]
        result = self._run(srv._enrich_clients(MockClient(), clients, None))
        assert result[0]["network_name"] == "LAN"
        assert result[1]["network_name"] == "Guest VLAN"
        assert "network_name" not in result[2]
