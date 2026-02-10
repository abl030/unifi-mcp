#!/usr/bin/env python3
"""Runtime toggle tests for fine-grained UNIFI_MODULES.

Spawns subprocesses with different UNIFI_MODULES values and asserts
exact tool counts via FastMCP's tool registry.

Run: uv run --extra test python -m pytest test_modules_toggle.py -v
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

# The helper script we run in subprocesses — it imports the server module
# and dumps tool info as JSON.
_HELPER = """\
import os, sys, json
os.environ["UNIFI_MODULES"] = sys.argv[1]
# Must set env BEFORE importing server (module-level code reads it)
sys.path.insert(0, "generated")
import importlib
import server as srv
tools = srv.mcp._tool_manager._tools
names = sorted(tools.keys())
print(json.dumps({"count": len(names), "names": names}))
"""

ALWAYS_ON_TOOLS = {
    "unifi_status", "unifi_self", "unifi_sites", "unifi_stat_sites",
    "unifi_stat_admin", "unifi_logout", "unifi_system_poweroff",
    "unifi_system_reboot", "unifi_report_issue",
}
ALWAYS_ON_COUNT = len(ALWAYS_ON_TOOLS)  # 9


def _run_with_modules(modules_str: str) -> dict:
    """Run helper script with given UNIFI_MODULES value, return tool info."""
    env = os.environ.copy()
    # Clear any existing UNIFI_MODULES to let the helper set it
    env.pop("UNIFI_MODULES", None)
    result = subprocess.run(
        [sys.executable, "-c", _HELPER, modules_str],
        capture_output=True, text=True, env=env,
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )
    assert result.returncode == 0, f"Helper failed with UNIFI_MODULES={modules_str!r}:\n{result.stderr}"
    return json.loads(result.stdout)


# --- Spot-check tools per module ---

DEVICE_TOOLS = {"unifi_restart_device", "unifi_adopt_device", "unifi_locate_device",
                "unifi_set_port_override", "unifi_list_device_configs"}
CLIENT_TOOLS = {"unifi_block_client", "unifi_forget_client", "unifi_list_users",
                "unifi_list_clients"}
WIFI_TOOLS = {"unifi_list_wlans", "unifi_list_wlan_groups", "unifi_list_channel_plans"}
NETWORK_TOOLS = {"unifi_list_networks", "unifi_list_port_profiles", "unifi_list_dns_records"}
FIREWALL_TOOLS = {"unifi_list_firewall_rules", "unifi_list_port_forwards", "unifi_list_routes"}
MONITOR_TOOLS = {"unifi_list_health", "unifi_list_sysinfo", "unifi_list_dashboard",
                 "unifi_archive_all_alarms"}
ADMIN_TOOLS = {"unifi_list_settings", "unifi_add_site", "unifi_get_admins",
               "unifi_list_user_groups"}
HOTSPOT_TOOLS = {"unifi_list_hotspot_operators", "unifi_create_voucher",
                 "unifi_list_vouchers"}
ADVANCED_TOOLS = {"unifi_list_maps", "unifi_list_heatmaps", "unifi_list_dpi_apps",
                  "unifi_list_schedule_tasks"}

# v2 tools by sub-module
V2_CLIENT_TOOLS = {"unifi_list_active_clients", "unifi_list_clients_history"}
V2_WIFI_TOOLS = {"unifi_list_ap_groups"}
V2_FIREWALL_TOOLS = {"unifi_list_firewall_policies", "unifi_list_traffic_rules",
                     "unifi_list_traffic_routes", "unifi_list_firewall_zones"}


class TestModuleCounts:
    """Test exact tool counts for each UNIFI_MODULES configuration."""

    def test_default_v1_v2(self):
        """Default: v1,v2 → 284 tools (backward compat)."""
        info = _run_with_modules("v1,v2")
        assert info["count"] == 284

    def test_v1_shortcut(self):
        """v1 expands to all 9 sub-modules → 269 tools (no v2)."""
        info = _run_with_modules("v1")
        assert info["count"] == 269

    def test_v2_shortcut(self):
        """v2 tools + always-on only → 24 tools."""
        info = _run_with_modules("v2")
        assert info["count"] == 24

    def test_empty(self):
        """Empty string → only always-on tools."""
        info = _run_with_modules("")
        assert info["count"] == ALWAYS_ON_COUNT

    def test_whitespace_handling(self):
        """Whitespace around module names is stripped."""
        info = _run_with_modules(" v1 , v2 ")
        assert info["count"] == 284

    def test_device(self):
        info = _run_with_modules("device")
        assert info["count"] == 33 + ALWAYS_ON_COUNT  # 42

    def test_client(self):
        info = _run_with_modules("client")
        assert info["count"] == 15 + 2 + ALWAYS_ON_COUNT  # 26

    def test_wifi(self):
        info = _run_with_modules("wifi")
        assert info["count"] == 14 + 1 + ALWAYS_ON_COUNT  # 24

    def test_network(self):
        info = _run_with_modules("network")
        assert info["count"] == 15 + ALWAYS_ON_COUNT  # 24

    def test_firewall(self):
        info = _run_with_modules("firewall")
        assert info["count"] == 30 + 12 + ALWAYS_ON_COUNT  # 51

    def test_monitor(self):
        info = _run_with_modules("monitor")
        assert info["count"] == 34 + ALWAYS_ON_COUNT  # 43

    def test_admin(self):
        info = _run_with_modules("admin")
        assert info["count"] == 41 + ALWAYS_ON_COUNT  # 50

    def test_hotspot(self):
        info = _run_with_modules("hotspot")
        assert info["count"] == 32 + ALWAYS_ON_COUNT  # 41

    def test_advanced(self):
        info = _run_with_modules("advanced")
        assert info["count"] == 46 + ALWAYS_ON_COUNT  # 55

    def test_user_combo(self):
        """User's target config: device,client,wifi,network,monitor → 123 tools."""
        info = _run_with_modules("device,client,wifi,network,monitor")
        assert info["count"] == 123

    def test_v2_plus_device(self):
        """v2 + device → all v2 (15) + device v1 (33) + always-on (9) = 57."""
        info = _run_with_modules("v2,device")
        assert info["count"] == 57

    def test_all_individual_modules(self):
        """All 9 modules listed individually = same as v1,v2 → 284."""
        info = _run_with_modules("device,client,wifi,network,firewall,monitor,admin,hotspot,advanced")
        assert info["count"] == 284


class TestModuleToolPresence:
    """Test that specific tools are present/absent based on module selection."""

    def test_always_on_present_everywhere(self):
        """Always-on tools present in every configuration."""
        for modules in ["", "device", "v1", "v2", "client,wifi"]:
            info = _run_with_modules(modules)
            names = set(info["names"])
            missing = ALWAYS_ON_TOOLS - names
            assert not missing, f"UNIFI_MODULES={modules!r}: missing always-on tools: {missing}"

    def test_device_tools_present(self):
        info = _run_with_modules("device")
        names = set(info["names"])
        missing = DEVICE_TOOLS - names
        assert not missing, f"Missing device tools: {missing}"

    def test_device_excludes_other_modules(self):
        info = _run_with_modules("device")
        names = set(info["names"])
        for check_tools, label in [
            (NETWORK_TOOLS, "network"), (FIREWALL_TOOLS, "firewall"),
            (ADMIN_TOOLS, "admin"), (HOTSPOT_TOOLS, "hotspot"),
        ]:
            overlap = check_tools & names
            assert not overlap, f"Device module should not include {label} tools: {overlap}"

    def test_no_duplicate_tools(self):
        """No tool registered more than once in any configuration."""
        for modules in ["v1,v2", "device,client", "v2,firewall", "client"]:
            info = _run_with_modules(modules)
            names = info["names"]
            assert len(names) == len(set(names)), (
                f"UNIFI_MODULES={modules!r}: duplicate tools found"
            )

    def test_v2_dual_guard_client(self):
        """v2 client tools available via 'client' module."""
        info = _run_with_modules("client")
        names = set(info["names"])
        missing = V2_CLIENT_TOOLS - names
        assert not missing, f"Missing v2 client tools via 'client' module: {missing}"

    def test_v2_dual_guard_v2_flag(self):
        """v2 client tools available via 'v2' flag."""
        info = _run_with_modules("v2")
        names = set(info["names"])
        missing = V2_CLIENT_TOOLS - names
        assert not missing, f"Missing v2 client tools via 'v2' flag: {missing}"

    def test_v2_client_excluded_from_device(self):
        """v2 client tools NOT available via 'device' module alone."""
        info = _run_with_modules("device")
        names = set(info["names"])
        overlap = V2_CLIENT_TOOLS & names
        assert not overlap, f"v2 client tools should not be in device module: {overlap}"

    def test_v2_firewall_dual_guard(self):
        """v2 firewall tools available via 'firewall' module."""
        info = _run_with_modules("firewall")
        names = set(info["names"])
        missing = V2_FIREWALL_TOOLS - names
        assert not missing, f"Missing v2 firewall tools: {missing}"

    def test_v2_wifi_dual_guard(self):
        """v2 wifi tools available via 'wifi' module."""
        info = _run_with_modules("wifi")
        names = set(info["names"])
        missing = V2_WIFI_TOOLS - names
        assert not missing, f"Missing v2 wifi tools: {missing}"

    def test_port_override_in_device(self):
        """Port override helper is in device module, not always-on."""
        device_info = _run_with_modules("device")
        assert "unifi_set_port_override" in device_info["names"]

        empty_info = _run_with_modules("")
        assert "unifi_set_port_override" not in empty_info["names"]

    def test_spot_checks_per_module(self):
        """Verify representative tools exist in each module."""
        checks = [
            ("device", DEVICE_TOOLS),
            ("client", CLIENT_TOOLS),
            ("wifi", WIFI_TOOLS),
            ("network", NETWORK_TOOLS),
            ("firewall", FIREWALL_TOOLS),
            ("monitor", MONITOR_TOOLS),
            ("admin", ADMIN_TOOLS),
            ("hotspot", HOTSPOT_TOOLS),
            ("advanced", ADVANCED_TOOLS),
        ]
        for mod, expected_tools in checks:
            info = _run_with_modules(mod)
            names = set(info["names"])
            missing = expected_tools - names
            assert not missing, f"Module {mod!r}: missing expected tools: {missing}"
