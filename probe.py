#!/usr/bin/env python3
"""UniFi API Live Probe.

Probes a live UniFi controller to discover all working API endpoints.
Reads probe-spec.json (declarative list of endpoints to try), hammers
each one, and outputs an updated endpoint-inventory.json + api-samples/.

Usage:
    uv run python probe.py --host 192.168.1.1 --username admin --password secret
    uv run python probe.py --dry-run          # just print what would be probed
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import httpx

ROOT = Path(__file__).parent
DEFAULT_SPEC = ROOT / "spec" / "probe-spec.json"
DEFAULT_OUTPUT = ROOT / "spec" / "endpoint-inventory.json"
DEFAULT_SAMPLES_DIR = ROOT / "spec" / "api-samples"

# ── Safety ──────────────────────────────────────────────────────────────────
# Commands that are safe to execute via POST (read-only / no side effects).
# Everything else is recorded as "declared, unverified".
SAFE_COMMANDS = frozenset({
    "speedtest-status",
    "get-admins",
    "list-backups",
    "check-firmware-update",
})

# Fields to scrub from sample data before writing to disk.
SCRUB_FIELDS = frozenset({
    "x_password",
    "x_passphrase",
    "x_shadow",
    "x_private_key",
    "x_certificate_pem",
    "x_certificate_arn",
    "device_auth",
    "ubic_uuid",
    "device_id",
})

# Substrings — any field whose name contains one of these gets scrubbed.
SCRUB_SUBSTRINGS = ("secret", "token", "key", "password", "passphrase")


# ── Result types ────────────────────────────────────────────────────────────
@dataclass
class ProbeResult:
    category: str
    name: str
    path: str
    source: str
    status_code: int | None = None
    record_count: int | None = None
    error: str | None = None
    response_data: dict | list | None = None
    method_used: str = "GET"
    verified: bool = True  # False for cmd endpoints we didn't execute


# ── Scrubbing ───────────────────────────────────────────────────────────────
def _should_scrub(field_name: str) -> bool:
    """Check if a field name indicates sensitive data."""
    if field_name in SCRUB_FIELDS:
        return True
    lower = field_name.lower()
    return any(s in lower for s in SCRUB_SUBSTRINGS)


def scrub_value(obj):
    """Recursively scrub sensitive fields from a JSON-like object."""
    if isinstance(obj, dict):
        return {
            k: "REDACTED" if _should_scrub(k) else scrub_value(v)
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [scrub_value(item) for item in obj]
    return obj


# ── HTTP client ─────────────────────────────────────────────────────────────
class UniFiProber:
    """Manages auth and requests to a live UniFi controller."""

    def __init__(self, host: str, port: int, username: str, password: str,
                 site: str, verify_ssl: bool, verbose: bool):
        self.base_url = f"https://{host}:{port}"
        self.username = username
        self.password = password
        self.site = site
        self.verbose = verbose
        self.csrf_token: str | None = None
        self.client = httpx.Client(
            base_url=self.base_url,
            verify=verify_ssl,
            timeout=30.0,
            follow_redirects=True,
        )
        self.controller_version: str | None = None
        self.controller_type: str | None = None

    def close(self):
        try:
            self.client.post("/api/logout")
        except Exception:
            pass
        self.client.close()

    def _log(self, msg: str):
        if self.verbose:
            print(f"  [probe] {msg}", file=sys.stderr)

    def _update_csrf(self, response: httpx.Response):
        """Extract CSRF token from cookies or headers."""
        for cookie in response.cookies.jar:
            if cookie.name == "csrf_token":
                self.csrf_token = cookie.value
                return
        # Some versions use X-Csrf-Token header
        csrf = response.headers.get("x-csrf-token")
        if csrf:
            self.csrf_token = csrf

    def _headers(self) -> dict[str, str]:
        h = {}
        if self.csrf_token:
            h["X-Csrf-Token"] = self.csrf_token
        return h

    def probe_status(self) -> ProbeResult:
        """Probe /status (unauthenticated) to get controller version."""
        try:
            r = self.client.get("/status")
            self._log(f"GET /status → {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                self.controller_version = data.get("meta", {}).get("server_version",
                                                                     data.get("server_version"))
                # Try to detect controller type
                if "ubnt_device_type" in data.get("meta", {}):
                    self.controller_type = "unifi_os"
                else:
                    self.controller_type = "standalone"
                return ProbeResult("global", "status", "/status", "existing",
                                   status_code=r.status_code, response_data=data)
            return ProbeResult("global", "status", "/status", "existing",
                               status_code=r.status_code)
        except Exception as e:
            return ProbeResult("global", "status", "/status", "existing", error=str(e))

    def login(self) -> bool:
        """Authenticate and establish session."""
        try:
            r = self.client.post("/api/login", json={
                "username": self.username,
                "password": self.password,
            })
            self._update_csrf(r)
            self._log(f"POST /api/login → {r.status_code}")
            if r.status_code == 200:
                return True
            print(f"ERROR: Login failed with status {r.status_code}", file=sys.stderr)
            try:
                body = r.json()
                print(f"  Response: {body}", file=sys.stderr)
            except Exception:
                pass
            return False
        except Exception as e:
            print(f"ERROR: Login failed: {e}", file=sys.stderr)
            return False

    def _relogin(self) -> bool:
        """Re-authenticate on 401."""
        self._log("Got 401, re-authenticating...")
        return self.login()

    def _request(self, method: str, path: str, json_body: dict | None = None,
                 retry_auth: bool = True) -> httpx.Response | None:
        """Make a request with auth retry."""
        try:
            r = self.client.request(method, path, headers=self._headers(),
                                     json=json_body)
            self._update_csrf(r)
            if r.status_code == 401 and retry_auth:
                if self._relogin():
                    return self._request(method, path, json_body, retry_auth=False)
            return r
        except httpx.TimeoutException:
            self._log(f"TIMEOUT: {method} {path}")
            return None
        except Exception as e:
            self._log(f"ERROR: {method} {path}: {e}")
            return None

    def _site_path(self, relative: str) -> str:
        """Build /api/s/{site}/{relative} path."""
        return f"/api/s/{self.site}/{relative}"

    def probe_global(self, name: str, ep: dict) -> ProbeResult:
        """Probe a global endpoint."""
        path = ep["path"]
        source = ep.get("source", "community")
        method = ep.get("method", "GET")

        # Replace {site} if present
        path = path.replace("{site}", self.site)

        r = self._request(method, path)
        if r is None:
            return ProbeResult("global", name, path, source, error="connection error")
        self._log(f"{method} {path} → {r.status_code}")
        data = None
        if r.status_code == 200:
            try:
                data = r.json()
            except Exception:
                pass
        return ProbeResult("global", name, path, source,
                           status_code=r.status_code, response_data=data)

    def probe_rest(self, name: str, ep: dict) -> ProbeResult:
        """Probe a REST endpoint (GET only — never mutate)."""
        path = self._site_path(ep["path"])
        source = ep.get("source", "community")

        r = self._request("GET", path)
        if r is None:
            return ProbeResult("rest", name, path, source, error="connection error")
        self._log(f"GET {path} → {r.status_code}")
        data = None
        count = None
        if r.status_code == 200:
            try:
                body = r.json()
                data = body
                if isinstance(body, dict) and "data" in body:
                    records = body["data"]
                    if isinstance(records, list):
                        count = len(records)
            except Exception:
                pass
        return ProbeResult("rest", name, path, source,
                           status_code=r.status_code, record_count=count,
                           response_data=data)

    def probe_list(self, name: str, ep: dict) -> ProbeResult:
        """Probe a list/ endpoint (GET only)."""
        path = self._site_path(ep["path"])
        source = ep.get("source", "community")

        r = self._request("GET", path)
        if r is None:
            return ProbeResult("list", name, path, source, error="connection error")
        self._log(f"GET {path} → {r.status_code}")
        data = None
        count = None
        if r.status_code == 200:
            try:
                body = r.json()
                data = body
                if isinstance(body, dict) and "data" in body:
                    records = body["data"]
                    if isinstance(records, list):
                        count = len(records)
            except Exception:
                pass
        return ProbeResult("list", name, path, source,
                           status_code=r.status_code, record_count=count,
                           response_data=data)

    def probe_stat(self, name: str, ep: dict) -> ProbeResult:
        """Probe a stat endpoint."""
        relative = ep["path"]
        source = ep.get("source", "community")
        method = ep.get("method", "GET")

        # Skip parameterized paths like stat/report/{interval}.{type}
        if "{" in relative:
            return ProbeResult("stat", name, relative, source,
                               error="parameterized path, skipped")

        path = self._site_path(relative)
        json_body = {} if method == "POST" else None

        r = self._request(method, path, json_body=json_body)
        if r is None:
            return ProbeResult("stat", name, path, source, error="connection error")
        self._log(f"{method} {path} → {r.status_code}")
        data = None
        count = None
        if r.status_code == 200:
            try:
                body = r.json()
                data = body
                if isinstance(body, dict) and "data" in body:
                    records = body["data"]
                    if isinstance(records, list):
                        count = len(records)
            except Exception:
                pass
        return ProbeResult("stat", name, path, source,
                           status_code=r.status_code, record_count=count,
                           response_data=data, method_used=method)

    def probe_cmd_manager(self, manager: str, ep: dict) -> list[ProbeResult]:
        """Probe a cmd manager: check path exists, execute only safe commands."""
        relative = ep["path"]
        source = ep.get("source", "community")
        commands = ep.get("commands", [])
        results = []

        path = self._site_path(relative)

        # First: check if the manager path exists (POST with no body → 400 = exists)
        r = self._request("POST", path, json_body={})
        manager_exists = False
        if r is not None:
            self._log(f"POST {path} (empty) → {r.status_code}")
            # 400 = "missing cmd" = path is valid
            # 200 = weird but valid
            # 404 = doesn't exist
            manager_exists = r.status_code in (200, 400)

        if not manager_exists:
            status = r.status_code if r else None
            results.append(ProbeResult(
                "cmd", manager, path, source,
                status_code=status,
                error="manager path not found" if r else "connection error",
            ))
            return results

        # Record each command
        for cmd in commands:
            if cmd in SAFE_COMMANDS:
                # Actually execute the safe command
                r2 = self._request("POST", path, json_body={"cmd": cmd})
                if r2 is not None:
                    self._log(f"POST {path} cmd={cmd} → {r2.status_code}")
                    data = None
                    if r2.status_code == 200:
                        try:
                            data = r2.json()
                        except Exception:
                            pass
                    results.append(ProbeResult(
                        "cmd", f"{manager}/{cmd}", path, source,
                        status_code=r2.status_code, response_data=data,
                        method_used="POST",
                    ))
                else:
                    results.append(ProbeResult(
                        "cmd", f"{manager}/{cmd}", path, source,
                        error="connection error",
                    ))
            else:
                # Record as declared but unverified
                results.append(ProbeResult(
                    "cmd", f"{manager}/{cmd}", path, source,
                    verified=False,
                ))

        # If no commands but manager exists, record the manager itself
        if not commands:
            results.append(ProbeResult(
                "cmd", manager, path, source,
                status_code=r.status_code if r else None,
            ))

        return results

    def probe_v2(self, name: str, ep: dict) -> ProbeResult:
        """Probe a v2 endpoint (GET only)."""
        raw_path = ep["path"]
        source = ep.get("source", "community")

        # v2 paths use {site} directly
        path = "/" + raw_path.replace("{site}", self.site)

        r = self._request("GET", path)
        if r is None:
            return ProbeResult("v2", name, path, source, error="connection error")
        self._log(f"GET {path} → {r.status_code}")
        data = None
        count = None
        if r.status_code == 200:
            try:
                body = r.json()
                data = body
                # v2 may return a bare list
                if isinstance(body, list):
                    count = len(body)
                elif isinstance(body, dict) and "data" in body:
                    records = body["data"]
                    if isinstance(records, list):
                        count = len(records)
            except Exception:
                pass
        return ProbeResult("v2", name, path, source,
                           status_code=r.status_code, record_count=count,
                           response_data=data)

    def probe_guest(self, name: str, ep: dict) -> ProbeResult:
        """Probe a guest endpoint."""
        path = ep["path"].replace("{site}", self.site)
        source = ep.get("source", "community")
        method = ep.get("method", "GET")

        r = self._request(method, path)
        if r is None:
            return ProbeResult("guest", name, path, source, error="connection error")
        self._log(f"{method} {path} → {r.status_code}")
        data = None
        if r.status_code == 200:
            try:
                data = r.json()
            except Exception:
                pass
        return ProbeResult("guest", name, path, source,
                           status_code=r.status_code, response_data=data)

    def probe_site_endpoint(self, category: str, name: str, ep: dict) -> ProbeResult:
        """Probe a generic site-scoped endpoint (GET only). Works for upd/, group/, cnt/, get/, set/."""
        path = self._site_path(ep["path"])
        source = ep.get("source", "community")

        r = self._request("GET", path)
        if r is None:
            return ProbeResult(category, name, path, source, error="connection error")
        self._log(f"GET {path} → {r.status_code}")
        data = None
        count = None
        if r.status_code == 200:
            try:
                body = r.json()
                data = body
                if isinstance(body, dict) and "data" in body:
                    records = body["data"]
                    if isinstance(records, list):
                        count = len(records)
            except Exception:
                pass
        return ProbeResult(category, name, path, source,
                           status_code=r.status_code, record_count=count,
                           response_data=data)

    def probe_dl(self, name: str, ep: dict) -> ProbeResult:
        """Probe a download endpoint (global path, GET only)."""
        path = ep["path"]
        source = ep.get("source", "community")

        r = self._request("GET", path)
        if r is None:
            return ProbeResult("dl", name, path, source, error="connection error")
        self._log(f"GET {path} → {r.status_code}")
        data = None
        if r.status_code == 200:
            try:
                data = r.json()
            except Exception:
                pass
        return ProbeResult("dl", name, path, source,
                           status_code=r.status_code, response_data=data)

    def probe_websocket(self, name: str, ep: dict) -> ProbeResult:
        """Check if a WebSocket endpoint exists (HTTP GET, expect 101 or 400)."""
        path = ep["path"].replace("{site}", self.site)
        source = ep.get("source", "community")

        r = self._request("GET", path)
        if r is None:
            return ProbeResult("websocket", name, path, source, error="connection error")
        self._log(f"GET {path} → {r.status_code}")
        # 101 = upgrade, 400 = endpoint exists but needs WS upgrade, 404 = not found
        return ProbeResult("websocket", name, path, source,
                           status_code=r.status_code)


# ── Inventory output ────────────────────────────────────────────────────────
def _build_inventory(results: list[ProbeResult], spec: dict,
                     controller_version: str | None,
                     controller_type: str | None) -> dict:
    """Build endpoint-inventory.json from probe results."""
    inv = {
        "controller_version": controller_version or "unknown",
        "controller_type": controller_type or "unknown",
        "base_url": "https://{host}:{port}",
        "auth": {
            "login": {
                "method": "POST",
                "path": "/api/login",
                "body": {"username": "str", "password": "str"},
            },
            "logout": {
                "method": "POST",
                "path": "/api/logout",
            },
        },
    }

    # Index results by category+name for lookup
    result_map: dict[str, ProbeResult] = {}
    for r in results:
        result_map[f"{r.category}:{r.name}"] = r

    # ── Global endpoints
    global_eps = {}
    for name, ep in spec.get("global_endpoints", {}).items():
        r = result_map.get(f"global:{name}")
        entry: dict = {
            "method": ep.get("method", "GET"),
            "path": ep["path"],
        }
        if ep.get("auth") is False:
            entry["auth"] = False
        if r and r.status_code is not None:
            entry["live_status"] = r.status_code
        if ep.get("source") == "community":
            entry["source"] = "community"
        global_eps[name] = entry
    inv["global_endpoints"] = global_eps

    # ── REST endpoints
    rest_eps = {}
    for name, ep in spec.get("rest_endpoints", {}).items():
        r = result_map.get(f"rest:{name}")
        entry = {
            "path": ep["path"],
            "methods": ep.get("methods", ["GET"]),
        }
        if r and r.status_code is not None:
            entry["live_status"] = r.status_code
        if r and r.record_count is not None:
            entry["sample_count"] = r.record_count
        if ep.get("note"):
            entry["note"] = ep["note"]
        if ep.get("source") == "community":
            entry["source"] = "community"
        rest_eps[name] = entry
    inv["rest_endpoints"] = rest_eps

    # ── List endpoints (new category)
    list_eps = {}
    for name, ep in spec.get("list_endpoints", {}).items():
        r = result_map.get(f"list:{name}")
        entry = {
            "path": ep["path"],
        }
        if r and r.status_code is not None:
            entry["live_status"] = r.status_code
        if r and r.record_count is not None:
            entry["sample_count"] = r.record_count
        if ep.get("source") == "community":
            entry["source"] = "community"
        list_eps[name] = entry
    inv["list_endpoints"] = list_eps

    # ── Stat endpoints
    stat_eps = {}
    for name, ep in spec.get("stat_endpoints", {}).items():
        r = result_map.get(f"stat:{name}")
        entry = {
            "path": ep["path"],
            "method": ep.get("method", "GET"),
        }
        if r and r.status_code is not None:
            entry["live_status"] = r.status_code
        if r and r.record_count is not None:
            entry["sample_count"] = r.record_count
        if ep.get("note"):
            entry["note"] = ep["note"]
        if ep.get("source") == "community":
            entry["source"] = "community"
        stat_eps[name] = entry
    inv["stat_endpoints"] = stat_eps

    # ── Cmd endpoints — rebuild from spec, annotate with live results
    cmd_eps = {}
    for manager, ep in spec.get("cmd_endpoints", {}).items():
        entry = {
            "path": ep["path"],
            "commands": ep.get("commands", []),
        }
        # Check if manager was probed successfully
        # Manager-level results use manager name directly for empty command lists,
        # or we check if any command had results
        mgr_result = result_map.get(f"cmd:{manager}")
        if mgr_result and mgr_result.status_code is not None:
            entry["live_status"] = mgr_result.status_code
        else:
            # Check if any command result exists and infer manager status
            for cmd in ep.get("commands", []):
                cmd_result = result_map.get(f"cmd:{manager}/{cmd}")
                if cmd_result and cmd_result.status_code is not None:
                    entry["live_status"] = 200  # manager exists if commands work
                    break

        if ep.get("source") == "community":
            entry["source"] = "community"
        cmd_eps[manager] = entry
    inv["cmd_endpoints"] = cmd_eps

    # ── V2 endpoints
    v2_eps = {}
    for name, ep in spec.get("v2_endpoints", {}).items():
        r = result_map.get(f"v2:{name}")
        entry = {
            "path": ep["path"],
            "methods": ep.get("methods", ["GET"]),
        }
        if r and r.status_code is not None:
            entry["live_status"] = r.status_code
        if ep.get("source") == "community":
            entry["source"] = "community"
        v2_eps[name] = entry
    inv["v2_endpoints"] = v2_eps

    # ── Guest endpoints (new category)
    guest_eps = {}
    for name, ep in spec.get("guest_endpoints", {}).items():
        r = result_map.get(f"guest:{name}")
        entry = {
            "method": ep.get("method", "GET"),
            "path": ep["path"],
        }
        if r and r.status_code is not None:
            entry["live_status"] = r.status_code
        if ep.get("source") == "community":
            entry["source"] = "community"
        guest_eps[name] = entry
    inv["guest_endpoints"] = guest_eps

    # ── Generic site-scoped categories (upd, group, cnt, get, set)
    for cat_key in ("upd_endpoints", "group_endpoints", "cnt_endpoints",
                     "get_endpoints", "set_endpoints"):
        cat_prefix = cat_key.replace("_endpoints", "")
        cat_eps = {}
        for name, ep in spec.get(cat_key, {}).items():
            r = result_map.get(f"{cat_prefix}:{name}")
            entry = {
                "path": ep["path"],
            }
            if r and r.status_code is not None:
                entry["live_status"] = r.status_code
            if r and r.record_count is not None:
                entry["sample_count"] = r.record_count
            if ep.get("note"):
                entry["note"] = ep["note"]
            if ep.get("source") == "community":
                entry["source"] = "community"
            cat_eps[name] = entry
        if cat_eps:
            inv[cat_key] = cat_eps

    # ── Download endpoints
    dl_eps = {}
    for name, ep in spec.get("dl_endpoints", {}).items():
        r = result_map.get(f"dl:{name}")
        entry = {
            "method": ep.get("method", "GET"),
            "path": ep["path"],
        }
        if r and r.status_code is not None:
            entry["live_status"] = r.status_code
        if ep.get("note"):
            entry["note"] = ep["note"]
        if ep.get("source") == "community":
            entry["source"] = "community"
        dl_eps[name] = entry
    if dl_eps:
        inv["dl_endpoints"] = dl_eps

    # ── WebSocket endpoints
    ws_eps = {}
    for name, ep in spec.get("websocket_endpoints", {}).items():
        r = result_map.get(f"websocket:{name}")
        entry = {
            "path": ep["path"],
        }
        if r and r.status_code is not None:
            entry["live_status"] = r.status_code
        if ep.get("note"):
            entry["note"] = ep["note"]
        if ep.get("source") == "community":
            entry["source"] = "community"
        ws_eps[name] = entry
    inv["websocket_endpoints"] = ws_eps

    return inv


def _write_sample(samples_dir: Path, prefix: str, name: str, data) -> bool:
    """Write a scrubbed sample file. Returns True if written."""
    if data is None:
        return False
    scrubbed = scrub_value(data)
    sample_path = samples_dir / f"{prefix}_{name}.json"
    sample_path.write_text(json.dumps(scrubbed, indent=None, ensure_ascii=False))
    return True


# ── Diff report ─────────────────────────────────────────────────────────────
def _print_report(results: list[ProbeResult],
                  controller_version: str | None):
    """Print a human-readable diff report."""
    total = len(results)
    ok_existing = []
    ok_new = []
    not_found = []
    errors = []
    unverified = []

    for r in results:
        if not r.verified:
            unverified.append(r)
        elif r.error:
            errors.append(r)
        elif r.status_code == 200:
            if r.source == "existing":
                ok_existing.append(r)
            else:
                ok_new.append(r)
        elif r.status_code == 404:
            not_found.append(r)
        elif r.status_code is not None:
            # Other status codes (400, 403, etc.) — still interesting
            if r.source == "existing":
                ok_existing.append(r)
            else:
                ok_new.append(r)

    print()
    print("=" * 60)
    print("  UniFi API Probe Report")
    print("=" * 60)
    print(f"  Controller: {controller_version or 'unknown'}")
    print(f"  Probed: {total} endpoints")
    print()

    if ok_new:
        print("--- New Endpoints (responding) ---")
        for r in sorted(ok_new, key=lambda x: x.name):
            count = f"{r.record_count} records" if r.record_count is not None else ""
            status = f"HTTP {r.status_code}" if r.status_code != 200 else ""
            extra = "  ".join(filter(None, [count, status]))
            print(f"  {r.category}/{r.name:<30s} {extra}  [{r.source}]")
        print()

    if not_found:
        print("--- Not Found (404) ---")
        for r in sorted(not_found, key=lambda x: x.name):
            print(f"  {r.category}/{r.name:<30s} [{r.source}]")
        print()

    if errors:
        print("--- Errors ---")
        for r in sorted(errors, key=lambda x: x.name):
            print(f"  {r.category}/{r.name:<30s} {r.error}  [{r.source}]")
        print()

    if unverified:
        print(f"--- Declared Commands (not executed, {len(unverified)} total) ---")
        print("  (Unsafe commands are recorded but not run)")
        print()

    if ok_existing:
        print("--- Existing Confirmed ---")
        for r in sorted(ok_existing, key=lambda x: x.name):
            count = f"{r.record_count} records" if r.record_count is not None else ""
            status = f"HTTP {r.status_code}" if r.status_code and r.status_code != 200 else ""
            extra = "  ".join(filter(None, [count, status]))
            print(f"  {r.category}/{r.name:<30s} {extra}")
        print()

    print("--- Summary ---")
    print(f"  Existing confirmed:  {len(ok_existing)}")
    print(f"  New discovered:      {len(ok_new)}")
    print(f"  Not found (404):     {len(not_found)}")
    print(f"  Errors:              {len(errors)}")
    print(f"  Unverified commands: {len(unverified)}")
    print()


# ── Dry-run ─────────────────────────────────────────────────────────────────
def _dry_run(spec: dict):
    """Print what would be probed without connecting."""
    total = 0
    for category in ("global_endpoints", "rest_endpoints", "list_endpoints",
                      "stat_endpoints", "v2_endpoints",
                      "upd_endpoints", "group_endpoints", "cnt_endpoints",
                      "get_endpoints", "set_endpoints", "dl_endpoints",
                      "guest_endpoints", "websocket_endpoints"):
        eps = spec.get(category, {})
        if eps:
            print(f"\n{category} ({len(eps)}):")
            for name, ep in eps.items():
                source = ep.get("source", "existing")
                path = ep.get("path", "?")
                tag = " [NEW]" if source == "community" else ""
                print(f"  {name:<30s} {path}{tag}")
                total += 1

    cmd_eps = spec.get("cmd_endpoints", {})
    if cmd_eps:
        cmd_count = sum(len(ep.get("commands", [])) for ep in cmd_eps.values())
        print(f"\ncmd_endpoints ({len(cmd_eps)} managers, {cmd_count} commands):")
        for manager, ep in cmd_eps.items():
            source = ep.get("source", "existing")
            tag = " [NEW]" if source == "community" else ""
            cmds = ep.get("commands", [])
            safe = [c for c in cmds if c in SAFE_COMMANDS]
            unsafe = [c for c in cmds if c not in SAFE_COMMANDS]
            print(f"  {manager:<20s} {ep.get('path', '?')}{tag}")
            if safe:
                print(f"    safe (will execute):  {', '.join(safe)}")
            if unsafe:
                print(f"    unsafe (skip):        {', '.join(unsafe)}")
            total += len(cmds) or 1  # at least 1 for the manager probe

    print(f"\nTotal endpoints to probe: {total}")


# ── Main ────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Probe a live UniFi controller for API endpoint discovery",
    )
    parser.add_argument("--host", default=os.environ.get("UNIFI_HOST", ""),
                        help="Controller hostname/IP (env: UNIFI_HOST)")
    parser.add_argument("--port", type=int,
                        default=int(os.environ.get("UNIFI_PORT", "8443")),
                        help="Controller port (default: 8443, env: UNIFI_PORT)")
    parser.add_argument("--username", default=os.environ.get("UNIFI_USERNAME", ""),
                        help="Admin username (env: UNIFI_USERNAME)")
    parser.add_argument("--password", default=os.environ.get("UNIFI_PASSWORD", ""),
                        help="Admin password (env: UNIFI_PASSWORD)")
    parser.add_argument("--site", default=os.environ.get("UNIFI_SITE", "default"),
                        help="Site name (default: 'default', env: UNIFI_SITE)")
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC,
                        help=f"Probe spec file (default: {DEFAULT_SPEC.name})")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help=f"Output inventory file (default: {DEFAULT_OUTPUT.name})")
    parser.add_argument("--samples-dir", type=Path, default=DEFAULT_SAMPLES_DIR,
                        help=f"Samples directory (default: {DEFAULT_SAMPLES_DIR.name}/)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print endpoints to probe without connecting")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Print detailed request/response info")
    parser.add_argument("--no-verify-ssl", action="store_true",
                        help="Disable SSL certificate verification")
    args = parser.parse_args()

    # Load spec
    if not args.spec.exists():
        print(f"ERROR: Spec file not found: {args.spec}", file=sys.stderr)
        sys.exit(1)
    spec = json.loads(args.spec.read_text())

    # Filter out _comment keys
    spec = {k: v for k, v in spec.items() if not k.startswith("_")}

    if args.dry_run:
        _dry_run(spec)
        sys.exit(0)

    # Validate required args
    if not args.host:
        print("ERROR: --host is required (or set UNIFI_HOST)", file=sys.stderr)
        sys.exit(1)
    if not args.username:
        print("ERROR: --username is required (or set UNIFI_USERNAME)", file=sys.stderr)
        sys.exit(1)
    if not args.password:
        print("ERROR: --password is required (or set UNIFI_PASSWORD)", file=sys.stderr)
        sys.exit(1)

    verify_ssl = not args.no_verify_ssl
    # Also check env
    if os.environ.get("UNIFI_VERIFY_SSL", "").lower() in ("false", "0", "no"):
        verify_ssl = False

    prober = UniFiProber(
        host=args.host,
        port=args.port,
        username=args.username,
        password=args.password,
        site=args.site,
        verify_ssl=verify_ssl,
        verbose=args.verbose,
    )

    results: list[ProbeResult] = []
    samples_written = 0

    try:
        # 1. Probe /status (unauthenticated)
        print("Probing /status...", file=sys.stderr)
        status_result = prober.probe_status()
        results.append(status_result)
        if status_result.response_data:
            if _write_sample(args.samples_dir, "global", "status",
                              status_result.response_data):
                samples_written += 1

        print(f"Controller version: {prober.controller_version or 'unknown'}",
              file=sys.stderr)
        print(f"Controller type: {prober.controller_type or 'unknown'}",
              file=sys.stderr)

        # 2. Login
        print("Authenticating...", file=sys.stderr)
        if not prober.login():
            print("FATAL: Cannot authenticate. Aborting.", file=sys.stderr)
            sys.exit(1)
        print("Authenticated.", file=sys.stderr)

        # 3. Probe all categories
        # ── Global (skip status, already probed)
        print("Probing global endpoints...", file=sys.stderr)
        for name, ep in spec.get("global_endpoints", {}).items():
            if name == "status":
                continue  # already probed
            r = prober.probe_global(name, ep)
            results.append(r)
            if r.response_data:
                if _write_sample(args.samples_dir, "global", name, r.response_data):
                    samples_written += 1

        # ── REST
        rest_eps = spec.get("rest_endpoints", {})
        print(f"Probing {len(rest_eps)} REST endpoints...", file=sys.stderr)
        for name, ep in rest_eps.items():
            r = prober.probe_rest(name, ep)
            results.append(r)
            if r.response_data:
                if _write_sample(args.samples_dir, "rest", name, r.response_data):
                    samples_written += 1

        # ── List
        list_eps = spec.get("list_endpoints", {})
        print(f"Probing {len(list_eps)} list endpoints...", file=sys.stderr)
        for name, ep in list_eps.items():
            r = prober.probe_list(name, ep)
            results.append(r)
            if r.response_data:
                if _write_sample(args.samples_dir, "list", name, r.response_data):
                    samples_written += 1

        # ── Stat
        stat_eps = spec.get("stat_endpoints", {})
        print(f"Probing {len(stat_eps)} stat endpoints...", file=sys.stderr)
        for name, ep in stat_eps.items():
            r = prober.probe_stat(name, ep)
            results.append(r)
            if r.response_data:
                if _write_sample(args.samples_dir, "stat", name, r.response_data):
                    samples_written += 1

        # ── Cmd
        cmd_eps = spec.get("cmd_endpoints", {})
        print(f"Probing {len(cmd_eps)} cmd managers...", file=sys.stderr)
        for manager, ep in cmd_eps.items():
            cmd_results = prober.probe_cmd_manager(manager, ep)
            results.extend(cmd_results)
            for cr in cmd_results:
                if cr.response_data:
                    # Use manager_command as filename
                    safe_name = cr.name.replace("/", "_")
                    if _write_sample(args.samples_dir, "cmd", safe_name,
                                      cr.response_data):
                        samples_written += 1

        # ── V2
        v2_eps = spec.get("v2_endpoints", {})
        print(f"Probing {len(v2_eps)} v2 endpoints...", file=sys.stderr)
        for name, ep in v2_eps.items():
            r = prober.probe_v2(name, ep)
            results.append(r)
            if r.response_data:
                if _write_sample(args.samples_dir, "v2", name, r.response_data):
                    samples_written += 1

        # ── Guest
        guest_eps = spec.get("guest_endpoints", {})
        print(f"Probing {len(guest_eps)} guest endpoints...", file=sys.stderr)
        for name, ep in guest_eps.items():
            r = prober.probe_guest(name, ep)
            results.append(r)
            if r.response_data:
                if _write_sample(args.samples_dir, "guest", name, r.response_data):
                    samples_written += 1

        # ── Generic site-scoped categories (upd, group, cnt, get, set)
        for cat_key in ("upd_endpoints", "group_endpoints", "cnt_endpoints",
                         "get_endpoints", "set_endpoints"):
            cat_prefix = cat_key.replace("_endpoints", "")
            cat_eps = spec.get(cat_key, {})
            if cat_eps:
                print(f"Probing {len(cat_eps)} {cat_prefix} endpoints...",
                      file=sys.stderr)
                for name, ep in cat_eps.items():
                    r = prober.probe_site_endpoint(cat_prefix, name, ep)
                    results.append(r)
                    if r.response_data:
                        if _write_sample(args.samples_dir, cat_prefix, name,
                                          r.response_data):
                            samples_written += 1

        # ── Download
        dl_eps = spec.get("dl_endpoints", {})
        if dl_eps:
            print(f"Probing {len(dl_eps)} dl endpoints...", file=sys.stderr)
            for name, ep in dl_eps.items():
                r = prober.probe_dl(name, ep)
                results.append(r)
                if r.response_data:
                    if _write_sample(args.samples_dir, "dl", name,
                                      r.response_data):
                        samples_written += 1

        # ── WebSocket
        ws_eps = spec.get("websocket_endpoints", {})
        print(f"Probing {len(ws_eps)} websocket endpoints...", file=sys.stderr)
        for name, ep in ws_eps.items():
            r = prober.probe_websocket(name, ep)
            results.append(r)

        # 4. Logout
        print("Logging out...", file=sys.stderr)

    finally:
        prober.close()

    # 5. Build and write inventory
    inv = _build_inventory(results, spec, prober.controller_version,
                           prober.controller_type)
    args.output.write_text(json.dumps(inv, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {args.output}", file=sys.stderr)
    print(f"Wrote {samples_written} sample files to {args.samples_dir}/",
          file=sys.stderr)

    # 6. Also scrub any pre-existing sample files
    _rescrub_existing_samples(args.samples_dir)

    # 7. Print report
    _print_report(results, prober.controller_version)


def _rescrub_existing_samples(samples_dir: Path):
    """Re-scrub all existing sample files to catch previously unscrubbed data."""
    if not samples_dir.is_dir():
        return
    count = 0
    for f in sorted(samples_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text())
            scrubbed = scrub_value(data)
            if scrubbed != data:
                f.write_text(json.dumps(scrubbed, indent=None, ensure_ascii=False))
                count += 1
        except Exception:
            pass
    if count:
        print(f"Re-scrubbed {count} existing sample files.", file=sys.stderr)


if __name__ == "__main__":
    main()
