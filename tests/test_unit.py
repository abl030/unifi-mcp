#!/usr/bin/env python3
"""Unit tests for generated server helper functions.

These tests do NOT require a running UniFi controller — they test
pure functions and mock async helpers directly.

Run:
    uv run --extra test python -m pytest tests/test_unit.py -v
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

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

    def test_backward_compatible_flat_fields(self):
        """Existing flat-field behavior is unchanged."""
        data = [{"_id": "1", "name": "Test", "extra": "drop"}]
        result, missing = srv._paginate_and_filter(data, 0, 0, "name")
        assert result == [{"_id": "1", "name": "Test"}]
        assert missing == []


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
