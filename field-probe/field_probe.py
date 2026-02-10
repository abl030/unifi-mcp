#!/usr/bin/env python3
"""Field Probe: capture field names from a live UniFi controller with real data.

Connects to a production controller (one with actual devices, clients, traffic)
and records which fields each endpoint returns. Outputs field-inventory.json —
a map of endpoint → sorted field names, with no sensitive values.

This is designed to fill the gap left by probing a bare Docker controller
(no adopted devices = empty data arrays = no field information).

Usage:
    # Set env vars for your production controller:
    export UNIFI_HOST=192.168.1.1
    export UNIFI_USERNAME=admin
    export UNIFI_PASSWORD=your-password

    # Run the probe:
    uv run python field-probe/field_probe.py

    # Or with explicit args:
    uv run python field-probe/field_probe.py --host 192.168.1.1 --username admin --password secret

    # Dry run — show what would be probed:
    uv run python field-probe/field_probe.py --dry-run

Output:
    field-probe/field-inventory.json — field names per endpoint (no values)

The output can then be fed into the generator to enrich docstrings with
available field names, so LLM consumers know what to ask for.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).parent
OUTPUT = ROOT / "field-inventory.json"

# Fields whose values must never be written to disk.
SCRUB_FIELDS = frozenset({
    "x_password", "x_passphrase", "x_shadow", "x_private_key",
    "x_certificate_pem", "x_certificate_arn", "device_auth",
})
SCRUB_SUBSTRINGS = ("secret", "token", "key", "password", "passphrase")

# ── Endpoints to probe ─────────────────────────────────────────────────────
# These are endpoints known to return empty on a bare controller.
# Grouped by API pattern.

SITE_ENDPOINTS: list[dict] = [
    # v1 REST endpoints (GET /api/s/{site}/rest/{resource})
    {"category": "rest", "name": "networkconf", "path": "rest/networkconf"},
    {"category": "rest", "name": "wlanconf", "path": "rest/wlanconf"},
    {"category": "rest", "name": "wlangroup", "path": "rest/wlangroup"},
    {"category": "rest", "name": "portconf", "path": "rest/portconf"},
    {"category": "rest", "name": "portforward", "path": "rest/portforward"},
    {"category": "rest", "name": "firewallrule", "path": "rest/firewallrule"},
    {"category": "rest", "name": "firewallgroup", "path": "rest/firewallgroup"},
    {"category": "rest", "name": "routing", "path": "rest/routing"},
    {"category": "rest", "name": "dynamicdns", "path": "rest/dynamicdns"},
    {"category": "rest", "name": "radiusprofile", "path": "rest/radiusprofile"},
    {"category": "rest", "name": "account", "path": "rest/account"},
    {"category": "rest", "name": "usergroup", "path": "rest/usergroup"},
    {"category": "rest", "name": "user", "path": "rest/user"},
    {"category": "rest", "name": "tag", "path": "rest/tag"},
    {"category": "rest", "name": "setting", "path": "rest/setting"},
    {"category": "rest", "name": "hotspotop", "path": "rest/hotspotop"},
    {"category": "rest", "name": "hotspotpackage", "path": "rest/hotspotpackage"},
    {"category": "rest", "name": "hotspot2conf", "path": "rest/hotspot2conf"},
    {"category": "rest", "name": "scheduletask", "path": "rest/scheduletask"},
    {"category": "rest", "name": "map", "path": "rest/map"},
    {"category": "rest", "name": "channelplan", "path": "rest/channelplan"},
    {"category": "rest", "name": "virtualdevice", "path": "rest/virtualdevice"},
    {"category": "rest", "name": "rogueknown", "path": "rest/rogueknown"},
    {"category": "rest", "name": "dhcpoption", "path": "rest/dhcpoption"},
    {"category": "rest", "name": "heatmap", "path": "rest/heatmap"},
    {"category": "rest", "name": "heatmappoint", "path": "rest/heatmappoint"},
    {"category": "rest", "name": "spatialrecord", "path": "rest/spatialrecord"},
    {"category": "rest", "name": "dpiapp", "path": "rest/dpiapp"},
    {"category": "rest", "name": "dpigroup", "path": "rest/dpigroup"},
    {"category": "rest", "name": "dnsrecord", "path": "rest/dnsrecord"},
    {"category": "rest", "name": "broadcastgroup", "path": "rest/broadcastgroup"},
    {"category": "rest", "name": "mediafile", "path": "rest/mediafile"},
    {"category": "rest", "name": "element", "path": "rest/element"},
    {"category": "rest", "name": "alarm", "path": "rest/alarm"},
    {"category": "rest", "name": "event", "path": "rest/event"},

    # v1 Stat endpoints (GET /api/s/{site}/stat/{resource})
    {"category": "stat", "name": "device", "path": "stat/device"},
    {"category": "stat", "name": "device_basic", "path": "stat/device-basic"},
    {"category": "stat", "name": "sta", "path": "stat/sta"},
    {"category": "stat", "name": "alluser", "path": "stat/alluser"},
    {"category": "stat", "name": "guest", "path": "stat/guest"},
    {"category": "stat", "name": "health", "path": "stat/health"},
    {"category": "stat", "name": "alarm", "path": "stat/alarm"},
    {"category": "stat", "name": "event", "path": "stat/event"},
    {"category": "stat", "name": "rogueap", "path": "stat/rogueap"},
    {"category": "stat", "name": "sitedpi", "path": "stat/sitedpi"},
    {"category": "stat", "name": "stadpi", "path": "stat/stadpi"},
    {"category": "stat", "name": "voucher", "path": "stat/voucher"},
    {"category": "stat", "name": "sysinfo", "path": "stat/sysinfo"},
    {"category": "stat", "name": "dashboard", "path": "stat/dashboard"},
    {"category": "stat", "name": "anomalies", "path": "stat/anomalies"},
    {"category": "stat", "name": "ips_event", "path": "stat/ips/event"},
    {"category": "stat", "name": "dynamicdns", "path": "stat/dynamicdns"},
    {"category": "stat", "name": "portforward", "path": "stat/portforward"},
    {"category": "stat", "name": "remoteuservpn", "path": "stat/remoteuservpn"},
    {"category": "stat", "name": "routing", "path": "stat/routing"},
    {"category": "stat", "name": "authorization", "path": "stat/authorization"},
    {"category": "stat", "name": "payment", "path": "stat/payment"},
    {"category": "stat", "name": "spectrum_scan", "path": "stat/spectrum_scan"},
    {"category": "stat", "name": "ccode", "path": "stat/ccode"},
    {"category": "stat", "name": "current_channel", "path": "stat/current-channel"},
    {"category": "stat", "name": "sdn", "path": "stat/sdn"},
    {"category": "stat", "name": "dpi", "path": "stat/dpi"},
    {"category": "stat", "name": "gateway", "path": "stat/gateway"},

    # Stat endpoints that need POST with body
    {"category": "stat", "name": "session", "path": "stat/session",
     "method": "POST", "body": {"type": "all", "start": 0, "end": 9999999999}},
    {"category": "stat", "name": "report", "path": "stat/report/daily.site",
     "method": "POST", "body": {"attrs": ["bytes", "num_sta"], "interval": 3600}},
]

# v2 endpoints (GET /v2/api/site/{site}/{resource})
V2_ENDPOINTS: list[dict] = [
    {"category": "v2", "name": "clients_active", "path": "clients/active"},
    {"category": "v2", "name": "clients_history", "path": "clients/history"},
    {"category": "v2", "name": "firewall_policies", "path": "firewall/policies"},
    {"category": "v2", "name": "firewall_zones", "path": "firewall/zones"},
    {"category": "v2", "name": "traffic_rules", "path": "traffic/rules"},
    {"category": "v2", "name": "trafficroutes", "path": "trafficroutes"},
    {"category": "v2", "name": "apgroups", "path": "apgroups"},
]


class FieldProber:
    """Connects to a UniFi controller and captures field names from each endpoint."""

    def __init__(self, host: str, port: int, username: str, password: str,
                 site: str = "default", verify_ssl: bool = False, verbose: bool = False):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.site = site
        self.verbose = verbose
        self.csrf_token: str | None = None

        self.client = httpx.Client(
            base_url=f"https://{host}:{port}",
            verify=verify_ssl,
            timeout=30.0,
            follow_redirects=True,
        )

    def _log(self, msg: str):
        if self.verbose:
            print(f"  [{msg}]", file=sys.stderr)

    def _headers(self) -> dict:
        h = {}
        if self.csrf_token:
            h["X-Csrf-Token"] = self.csrf_token
        return h

    def _update_csrf(self, response: httpx.Response):
        token = response.headers.get("x-csrf-token")
        if token:
            self.csrf_token = token

    def login(self) -> bool:
        try:
            r = self.client.post("/api/login", json={
                "username": self.username,
                "password": self.password,
            })
            self._update_csrf(r)
            if r.status_code == 200:
                print(f"Logged in to {self.host}:{self.port}")
                return True
            print(f"ERROR: Login failed (HTTP {r.status_code})", file=sys.stderr)
            return False
        except Exception as e:
            print(f"ERROR: Login failed: {e}", file=sys.stderr)
            return False

    def _request(self, method: str, path: str, json_body: dict | None = None) -> httpx.Response | None:
        try:
            r = self.client.request(method, path, headers=self._headers(), json=json_body)
            self._update_csrf(r)
            if r.status_code == 401:
                if self.login():
                    r = self.client.request(method, path, headers=self._headers(), json=json_body)
                    self._update_csrf(r)
            return r
        except Exception as e:
            self._log(f"Request failed: {e}")
            return None

    def _extract_fields(self, data: list | dict) -> dict:
        """Extract field names and basic type info from response data.

        Returns {field_name: {"type": str, "sample_count": int}} — NO values.
        """
        if isinstance(data, dict):
            records = [data]
        elif isinstance(data, list):
            records = data
        else:
            return {}

        field_info: dict[str, dict] = {}
        for record in records:
            if not isinstance(record, dict):
                continue
            for key, value in record.items():
                if key not in field_info:
                    # Determine type without storing the value
                    if value is None:
                        vtype = "null"
                    elif isinstance(value, bool):
                        vtype = "bool"
                    elif isinstance(value, int):
                        vtype = "int"
                    elif isinstance(value, float):
                        vtype = "float"
                    elif isinstance(value, str):
                        vtype = "str"
                    elif isinstance(value, list):
                        vtype = "list"
                    elif isinstance(value, dict):
                        vtype = "dict"
                    else:
                        vtype = type(value).__name__
                    field_info[key] = {"type": vtype, "seen_in": 0}
                field_info[key]["seen_in"] += 1

        # Add total record count for computing commonality
        for fi in field_info.values():
            fi["total_records"] = len(records)

        return dict(sorted(field_info.items()))

    def probe_site_endpoint(self, ep: dict) -> dict | None:
        """Probe a site-scoped endpoint and return field info."""
        method = ep.get("method", "GET")
        path = f"/api/s/{self.site}/{ep['path']}"
        body = ep.get("body")

        self._log(f"{method} {path}")
        r = self._request(method, path, json_body=body)
        if r is None:
            return None

        if r.status_code != 200:
            self._log(f"  → HTTP {r.status_code}")
            return None

        try:
            resp = r.json()
        except Exception:
            return None

        data = resp.get("data", resp) if isinstance(resp, dict) else resp
        if not data:
            return None

        return self._extract_fields(data)

    def probe_v2_endpoint(self, ep: dict) -> dict | None:
        """Probe a v2 endpoint and return field info."""
        path = f"/v2/api/site/{self.site}/{ep['path']}"

        self._log(f"GET {path}")
        r = self._request("GET", path)
        if r is None:
            return None

        if r.status_code != 200:
            self._log(f"  → HTTP {r.status_code}")
            return None

        try:
            data = r.json()
        except Exception:
            return None

        # v2 responses may be a list directly or wrapped
        if isinstance(data, dict) and "data" in data:
            data = data["data"]

        if not data:
            return None

        return self._extract_fields(data)

    def run(self, dry_run: bool = False) -> dict:
        """Probe all endpoints and return field inventory."""
        inventory: dict[str, dict] = {}

        all_endpoints = SITE_ENDPOINTS + V2_ENDPOINTS
        print(f"\nField probe: {len(all_endpoints)} endpoints to check\n")

        if dry_run:
            for ep in all_endpoints:
                method = ep.get("method", "GET")
                if ep["category"] == "v2":
                    path = f"/v2/api/site/{self.site}/{ep['path']}"
                else:
                    path = f"/api/s/{self.site}/{ep['path']}"
                print(f"  {method:4s} {path}")
            return {}

        if not self.login():
            print("FATAL: Could not authenticate", file=sys.stderr)
            sys.exit(1)

        found = 0
        empty = 0
        errors = 0

        for ep in all_endpoints:
            key = f"{ep['category']}_{ep['name']}"

            if ep["category"] == "v2":
                fields = self.probe_v2_endpoint(ep)
            else:
                fields = self.probe_site_endpoint(ep)

            if fields is None:
                status = "empty/error"
                errors += 1
            elif not fields:
                status = "empty"
                empty += 1
            else:
                status = f"{len(fields)} fields"
                found += 1
                inventory[key] = {
                    "category": ep["category"],
                    "name": ep["name"],
                    "path": ep["path"],
                    "field_count": len(fields),
                    "fields": fields,
                }

            print(f"  {key:40s} → {status}")

        print(f"\nResults: {found} with data, {empty} empty, {errors} errors")
        return inventory


def main():
    parser = argparse.ArgumentParser(description="UniFi Field Probe — capture field names from endpoints")
    parser.add_argument("--host", default=os.environ.get("UNIFI_HOST", "localhost"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("UNIFI_PORT", "8443")))
    parser.add_argument("--username", default=os.environ.get("UNIFI_USERNAME", "admin"))
    parser.add_argument("--password", default=os.environ.get("UNIFI_PASSWORD", ""))
    parser.add_argument("--site", default=os.environ.get("UNIFI_SITE", "default"))
    parser.add_argument("--no-verify-ssl", action="store_true", default=True)
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be probed without connecting")
    parser.add_argument("--output", type=Path, default=OUTPUT, help="Output file path")
    args = parser.parse_args()

    if not args.password and not args.dry_run:
        print("ERROR: UNIFI_PASSWORD env var or --password required", file=sys.stderr)
        sys.exit(1)

    prober = FieldProber(
        host=args.host,
        port=args.port,
        username=args.username,
        password=args.password,
        site=args.site,
        verify_ssl=not args.no_verify_ssl,
        verbose=args.verbose,
    )

    inventory = prober.run(dry_run=args.dry_run)

    if inventory:
        args.output.write_text(json.dumps(inventory, indent=2) + "\n")
        print(f"\nWrote {len(inventory)} endpoint field maps to {args.output}")

        # Summary: which endpoints gained new field data
        print("\n=== Endpoints with field data ===")
        for key, info in sorted(inventory.items()):
            fields = sorted(info["fields"].keys())
            print(f"  {key} ({info['field_count']} fields): {', '.join(fields[:10])}", end="")
            if len(fields) > 10:
                print(f" ... +{len(fields) - 10} more", end="")
            print()


if __name__ == "__main__":
    main()
