#!/usr/bin/env python3
"""Runtime toggle tests for fine-grained UNIFI_MODULES.

All expected values are derived from endpoint-inventory.json + generator/naming.py.
Nothing is hardcoded — when the API surface changes, these tests auto-adapt.

Run: uv run --extra test python -m pytest test_modules_toggle.py -v
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from count_tools import count_from_spec, count_module_breakdown, count_readonly_breakdown
from generator.naming import (
    CMD_MODULES,
    COMMAND_TOOL_NAMES,
    CRUD_REST,
    MODULE_ORDER,
    MUTATING_GLOBALS,
    MUTATION_COMMANDS,
    NO_REST_DELETE,
    READ_ONLY_REST,
    RESOURCE_NAMES,
    REST_MODULES,
    SKIP_COMMANDS,
    STAT_MODULES,
    STAT_NAMES,
    V2_MODULES,
    V2_RESOURCE_NAMES,
)

# ---------------------------------------------------------------------------
# Derive ALL expected values from spec + naming data (zero hardcoded numbers)
# ---------------------------------------------------------------------------

_COUNTS = count_from_spec()
_MODULES = count_module_breakdown(_COUNTS)
_ALWAYS_ON = _COUNTS["tools"]["global"] + _COUNTS["tools"]["report_issue"] + _COUNTS["tools"]["overview"]
_TOTAL = _COUNTS["tools"]["total"]
_V1_TOTAL = sum(_MODULES[m]["v1"] for m in MODULE_ORDER) + _ALWAYS_ON
_V2_TOTAL = sum(_MODULES[m]["v2"] for m in MODULE_ORDER) + _ALWAYS_ON

# Per-module expected tool count when loaded alone (v1 + v2 + always-on)
_MODULE_EXPECTED = {
    mod: _MODULES[mod]["v1"] + _MODULES[mod]["v2"] + _ALWAYS_ON
    for mod in MODULE_ORDER
}


# --- Read-only derived values (zero hardcoded numbers) ---
_RO = count_readonly_breakdown()
_RO_TOTAL = _RO["readonly"]  # all read-only tools in v1,v2 mode

# Read-only always-on: non-mutating globals + report_issue
_raw_for_ro = json.loads(Path("endpoint-inventory.json").read_text())
_RO_ALWAYS_ON = (
    len([n for n in _raw_for_ro["global_endpoints"] if n not in MUTATING_GLOBALS])
    + 1  # report_issue
    + 1  # overview
)

# Per-module read-only expected count when loaded alone
_RO_MODULE_EXPECTED = {
    mod: _MODULES[mod]["v1_ro"] + _MODULES[mod]["v2_ro"] + _RO_ALWAYS_ON
    for mod in MODULE_ORDER
}

_RO_V1_TOTAL = sum(_MODULES[m]["v1_ro"] for m in MODULE_ORDER) + _RO_ALWAYS_ON
_RO_V2_TOTAL = sum(_MODULES[m]["v2_ro"] for m in MODULE_ORDER) + _RO_ALWAYS_ON


def _derive_mutating_tools() -> set[str]:
    """Derive ALL mutating tool names from spec + naming data."""
    raw = json.loads(Path("endpoint-inventory.json").read_text())
    mutating: set[str] = set()

    # REST CRUD: create_*, update_*, delete_*
    for name in raw.get("rest_endpoints", {}):
        if name not in RESOURCE_NAMES:
            continue
        singular, plural = RESOURCE_NAMES[name]
        if name == "setting":
            mutating.add("unifi_update_setting")
        elif name in CRUD_REST:
            mutating.add(f"unifi_create_{singular}")
            mutating.add(f"unifi_update_{singular}")
            if name not in NO_REST_DELETE:
                mutating.add(f"unifi_delete_{singular}")

    # Cmd: mutation commands only
    for mgr, ep in raw.get("cmd_endpoints", {}).items():
        for cmd in ep.get("commands", []):
            key = (mgr, cmd)
            if key in SKIP_COMMANDS:
                continue
            if key in MUTATION_COMMANDS:
                tool_name = COMMAND_TOOL_NAMES.get(key, f"{cmd.replace('-', '_')}_{mgr}")
                mutating.add(f"unifi_{tool_name}")

    # v2: POST/PUT/DELETE
    for name, ep in raw.get("v2_endpoints", {}).items():
        singular, plural = V2_RESOURCE_NAMES.get(name, (name, name + "s"))
        methods = ep.get("methods", ["GET"])
        if "POST" in methods:
            mutating.add(f"unifi_create_{singular}")
        if "PUT" in methods:
            mutating.add(f"unifi_update_{singular}")
        if "DELETE" in methods:
            mutating.add(f"unifi_delete_{singular}")

    # Mutating globals
    for name in MUTATING_GLOBALS:
        mutating.add(f"unifi_{name}")

    # Port override
    mutating.add("unifi_set_port_override")

    return mutating


_MUTATING_TOOLS = _derive_mutating_tools()


def _derive_always_on_tools() -> set[str]:
    """Derive always-on tool names from the inventory."""
    raw = json.loads(Path("endpoint-inventory.json").read_text())
    return {f"unifi_{name}" for name in raw["global_endpoints"]} | {"unifi_report_issue", "unifi_get_overview"}


def _derive_module_tools() -> dict[str, set[str]]:
    """Derive expected tool names per module from spec + naming data."""
    raw = json.loads(Path("endpoint-inventory.json").read_text())
    tools: dict[str, set[str]] = {m: set() for m in MODULE_ORDER}

    # REST tools
    for name in raw.get("rest_endpoints", {}):
        if name not in RESOURCE_NAMES:
            continue
        mod = REST_MODULES.get(name, "advanced")
        singular, plural = RESOURCE_NAMES[name]
        if name == "setting":
            tools[mod].update([
                "unifi_list_settings", "unifi_get_setting", "unifi_update_setting",
            ])
        elif name in READ_ONLY_REST:
            tools[mod].add(f"unifi_list_{plural}")
        elif name in CRUD_REST:
            tools[mod].update([
                f"unifi_list_{plural}", f"unifi_get_{singular}",
                f"unifi_create_{singular}", f"unifi_update_{singular}",
            ])
            if name not in NO_REST_DELETE:
                tools[mod].add(f"unifi_delete_{singular}")

    # Stat tools
    for name in raw.get("stat_endpoints", {}):
        mod = STAT_MODULES.get(name, "monitor")
        display = STAT_NAMES.get(name, name)
        if name == "report":
            tools[mod].add("unifi_list_report")
        else:
            tools[mod].add(f"unifi_list_{display}")

    # Cmd tools
    for mgr, ep in raw.get("cmd_endpoints", {}).items():
        for cmd in ep.get("commands", []):
            key = (mgr, cmd)
            if key in SKIP_COMMANDS:
                continue
            mod = CMD_MODULES.get(key, "admin")
            tool_name = COMMAND_TOOL_NAMES.get(key, f"{cmd.replace('-', '_')}_{mgr}")
            tools[mod].add(f"unifi_{tool_name}")

    # V2 tools
    for name, ep in raw.get("v2_endpoints", {}).items():
        mod = V2_MODULES.get(name, "advanced")
        singular, plural = V2_RESOURCE_NAMES.get(name, (name, name + "s"))
        methods = ep.get("methods", ["GET"])
        if "GET" in methods:
            tools[mod].add(f"unifi_list_{plural}")
        if "POST" in methods:
            tools[mod].add(f"unifi_create_{singular}")
        if "PUT" in methods:
            tools[mod].add(f"unifi_update_{singular}")
        if "DELETE" in methods:
            tools[mod].add(f"unifi_delete_{singular}")

    # Port override helper → device
    tools["device"].add("unifi_set_port_override")

    return tools


_ALWAYS_ON_TOOLS = _derive_always_on_tools()
_MODULE_TOOLS = _derive_module_tools()

# Classify which modules have v2 tools (for dual-guard tests)
_V2_MODULE_TOOLS: dict[str, set[str]] = {}
for _mod in MODULE_ORDER:
    _v2_names = set()
    _raw = json.loads(Path("endpoint-inventory.json").read_text())
    for _name, _ep in _raw.get("v2_endpoints", {}).items():
        if V2_MODULES.get(_name) == _mod:
            _s, _p = V2_RESOURCE_NAMES.get(_name, (_name, _name + "s"))
            _methods = _ep.get("methods", ["GET"])
            if "GET" in _methods:
                _v2_names.add(f"unifi_list_{_p}")
            if "POST" in _methods:
                _v2_names.add(f"unifi_create_{_s}")
            if "PUT" in _methods:
                _v2_names.add(f"unifi_update_{_s}")
            if "DELETE" in _methods:
                _v2_names.add(f"unifi_delete_{_s}")
    if _v2_names:
        _V2_MODULE_TOOLS[_mod] = _v2_names


# ---------------------------------------------------------------------------
# Subprocess helper
# ---------------------------------------------------------------------------

_HELPER = """\
import os, sys, json
os.environ["UNIFI_MODULES"] = sys.argv[1]
if len(sys.argv) > 2 and sys.argv[2] == "readonly":
    os.environ["UNIFI_READ_ONLY"] = "true"
sys.path.insert(0, "generated")
import server as srv
tools = srv.mcp._tool_manager._tools
names = sorted(tools.keys())
print(json.dumps({"count": len(names), "names": names}))
"""


def _run(modules_str: str, *, read_only: bool = False) -> dict:
    """Run helper with given UNIFI_MODULES, return {"count": N, "names": [...]}."""
    env = os.environ.copy()
    env.pop("UNIFI_MODULES", None)
    env.pop("UNIFI_READ_ONLY", None)
    args = [sys.executable, "-c", _HELPER, modules_str]
    if read_only:
        args.append("readonly")
    result = subprocess.run(
        args,
        capture_output=True, text=True, env=env,
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )
    assert result.returncode == 0, (
        f"Failed with UNIFI_MODULES={modules_str!r} read_only={read_only}:\n{result.stderr}"
    )
    return json.loads(result.stdout)


# ===========================================================================
# Tests
# ===========================================================================


class TestModuleCounts:
    """Verify tool counts match spec-derived expectations."""

    def test_default_v1_v2(self):
        assert _run("v1,v2")["count"] == _TOTAL

    def test_v1_shortcut(self):
        assert _run("v1")["count"] == _V1_TOTAL

    def test_v2_shortcut(self):
        assert _run("v2")["count"] == _V2_TOTAL

    def test_empty(self):
        assert _run("")["count"] == _ALWAYS_ON

    def test_whitespace(self):
        assert _run(" v1 , v2 ")["count"] == _TOTAL

    @pytest.mark.parametrize("mod", MODULE_ORDER)
    def test_single_module(self, mod):
        info = _run(mod)
        assert info["count"] == _MODULE_EXPECTED[mod], (
            f"{mod}: expected {_MODULE_EXPECTED[mod]}, got {info['count']}"
        )

    def test_all_individual_equals_total(self):
        assert _run(",".join(MODULE_ORDER))["count"] == _TOTAL

    def test_multi_module_combo(self):
        """Arbitrary combo: sum of per-module v1+v2 + always-on."""
        combo = ["device", "client", "wifi", "network", "monitor"]
        expected = sum(_MODULES[m]["v1"] + _MODULES[m]["v2"] for m in combo) + _ALWAYS_ON
        assert _run(",".join(combo))["count"] == expected

    def test_v2_plus_single_module(self):
        """v2 flag + one sub-module: all v2 + that module's v1 + always-on."""
        mod = "device"
        expected = _V2_TOTAL + _MODULES[mod]["v1"]
        assert _run(f"v2,{mod}")["count"] == expected


class TestModuleToolPresence:
    """Verify correct tools present/absent per module configuration."""

    def test_always_on_everywhere(self):
        """Always-on tools present in every configuration."""
        for modules in ["", "v1", "v2", MODULE_ORDER[0]]:
            names = set(_run(modules)["names"])
            missing = _ALWAYS_ON_TOOLS - names
            assert not missing, f"UNIFI_MODULES={modules!r}: missing always-on: {missing}"

    @pytest.mark.parametrize("mod", MODULE_ORDER)
    def test_module_tools_present(self, mod):
        """Each module's derived tools are present when that module is loaded."""
        names = set(_run(mod)["names"])
        expected = _MODULE_TOOLS[mod]
        missing = expected - names
        assert not missing, f"Module {mod!r}: missing tools: {missing}"

    @pytest.mark.parametrize("mod", MODULE_ORDER)
    def test_module_excludes_others(self, mod):
        """Tools from other modules should NOT appear when only one module is loaded."""
        names = set(_run(mod)["names"])
        # Remove always-on and this module's tools
        unexpected = names - _ALWAYS_ON_TOOLS - _MODULE_TOOLS[mod]
        # v2 tools for this module are also expected (dual-guard)
        unexpected -= _V2_MODULE_TOOLS.get(mod, set())
        assert not unexpected, (
            f"Module {mod!r}: unexpected tools from other modules: {unexpected}"
        )

    def test_no_duplicates(self):
        """No tool registered more than once in any configuration."""
        for modules in ["v1,v2", "device,client", "v2,firewall"]:
            names = _run(modules)["names"]
            assert len(names) == len(set(names)), (
                f"UNIFI_MODULES={modules!r}: duplicate tools"
            )

    @pytest.mark.parametrize("mod", sorted(_V2_MODULE_TOOLS.keys()))
    def test_v2_dual_guard_via_module(self, mod):
        """v2 tools available when their parent sub-module is loaded."""
        names = set(_run(mod)["names"])
        missing = _V2_MODULE_TOOLS[mod] - names
        assert not missing, f"v2 tools missing via {mod!r} module: {missing}"

    @pytest.mark.parametrize("mod", sorted(_V2_MODULE_TOOLS.keys()))
    def test_v2_dual_guard_via_v2_flag(self, mod):
        """v2 tools available when 'v2' flag is set."""
        names = set(_run("v2")["names"])
        missing = _V2_MODULE_TOOLS[mod] - names
        assert not missing, f"v2 {mod} tools missing via 'v2' flag: {missing}"

    def test_port_override_in_device_only(self):
        """Port override is in device module, not always-on."""
        assert "unifi_set_port_override" in _run("device")["names"]
        assert "unifi_set_port_override" not in _run("")["names"]


class TestReadOnly:
    """Verify UNIFI_READ_ONLY=true strips all mutating tools."""

    def test_readonly_default(self):
        """v1,v2 + read-only → correct read-only count."""
        assert _run("v1,v2", read_only=True)["count"] == _RO_TOTAL

    def test_readonly_v1(self):
        """v1 + read-only → only v1 read-only tools."""
        assert _run("v1", read_only=True)["count"] == _RO_V1_TOTAL

    def test_readonly_v2(self):
        """v2 + read-only → only v2 read-only tools."""
        assert _run("v2", read_only=True)["count"] == _RO_V2_TOTAL

    def test_readonly_empty(self):
        """Empty + read-only → only read-only always-on tools."""
        assert _run("", read_only=True)["count"] == _RO_ALWAYS_ON

    @pytest.mark.parametrize("mod", MODULE_ORDER)
    def test_readonly_per_module(self, mod):
        """Each module individually + read-only → correct count."""
        info = _run(mod, read_only=True)
        assert info["count"] == _RO_MODULE_EXPECTED[mod], (
            f"{mod}: expected {_RO_MODULE_EXPECTED[mod]}, got {info['count']}"
        )

    def test_readonly_no_mutating_tools(self):
        """No mutating tool name appears in v1,v2 read-only config."""
        names = set(_run("v1,v2", read_only=True)["names"])
        leaked = _MUTATING_TOOLS & names
        assert not leaked, f"Mutating tools in read-only mode: {leaked}"

    def test_readonly_always_on_present(self):
        """Read-only always-on tools still present."""
        names = set(_run("v1,v2", read_only=True)["names"])
        ro_always_on = (
            {f"unifi_{n}" for n in _raw_for_ro["global_endpoints"]
             if n not in MUTATING_GLOBALS}
            | {"unifi_report_issue"}
        )
        missing = ro_always_on - names
        assert not missing, f"Missing read-only always-on tools: {missing}"

    def test_readonly_composable(self):
        """device,client,monitor + read-only → correct sum."""
        combo = ["device", "client", "monitor"]
        expected = (
            sum(_MODULES[m]["v1_ro"] + _MODULES[m]["v2_ro"] for m in combo)
            + _RO_ALWAYS_ON
        )
        assert _run(",".join(combo), read_only=True)["count"] == expected

    def test_readonly_no_confirm_param(self):
        """No tool in read-only mode should require a confirm parameter."""
        # All tools with confirm are in _MUTATING_TOOLS; verify none are present
        names = set(_run("v1,v2", read_only=True)["names"])
        confirm_tools = _MUTATING_TOOLS & names
        assert not confirm_tools, (
            f"Tools with confirm param in read-only mode: {confirm_tools}"
        )

    def test_readonly_off_by_default(self):
        """Default (no env var) should include all tools."""
        assert _run("v1,v2")["count"] == _TOTAL
