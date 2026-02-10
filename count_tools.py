#!/usr/bin/env python3
"""Count endpoints and tools from endpoint-inventory.json.

Uses the same logic as generator/context_builder.py + server.py.j2 template
to compute tool counts. Run: uv run python count_tools.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
INVENTORY_PATH = ROOT / "spec" / "endpoint-inventory.json"

# Import the authoritative sets from the generator so we stay in sync.
from generator.naming import (
    CMD_MODULES,
    CRUD_REST,
    MODULE_ORDER,
    MUTATING_GLOBALS,
    MUTATION_COMMANDS,
    NO_REST_DELETE,
    READ_ONLY_REST,
    REST_MODULES,
    SKIP_COMMANDS,
    STAT_MODULES,
    V2_MODULES,
)


def count_from_spec() -> dict:
    """Count endpoints and tools directly from the spec."""
    raw = json.loads(INVENTORY_PATH.read_text())

    rest = raw.get("rest_endpoints", {})
    stat = raw.get("stat_endpoints", {})
    cmd = raw.get("cmd_endpoints", {})
    v2 = raw.get("v2_endpoints", {})
    glb = raw.get("global_endpoints", {})
    lst = raw.get("list_endpoints", {})
    guest = raw.get("guest_endpoints", {})
    ws = raw.get("websocket_endpoints", {})

    # --- Endpoint counts ---
    rest_count = len(rest)
    stat_count = len(stat)
    cmd_count = sum(len(ep.get("commands", [])) for ep in cmd.values())
    cmd_manager_count = len(cmd)
    v2_count = len(v2)
    global_count = len(glb)
    list_count = len(lst)
    guest_count = len(guest)
    ws_count = len(ws)
    total_endpoints = (rest_count + stat_count + cmd_count + v2_count
                       + global_count + list_count + guest_count + ws_count)

    # --- Tool counts ---
    # The template (server.py.j2) only generates tools for REST endpoints that
    # match is_setting, is_readonly, or is_crud. Endpoints not in RESOURCE_NAMES
    # are silently skipped (no {% else %} clause in the template).
    rest_tools = 0
    rest_detail = {}
    rest_skipped = []
    for name in rest:
        is_setting = name == "setting"
        is_readonly = name in READ_ONLY_REST
        is_crud = name in CRUD_REST

        if is_setting:
            tools = 3
        elif is_readonly:
            tools = 1
        elif is_crud:
            tools = 4 if name in NO_REST_DELETE else 5
        else:
            # Not in RESOURCE_NAMES → template skips it, no tools generated
            rest_skipped.append(name)
            continue
        rest_tools += tools
        rest_detail[name] = tools

    stat_tools = stat_count  # 1 tool per stat endpoint

    cmd_skipped = sum(
        1 for mgr, ep in cmd.items()
        for c in ep.get("commands", [])
        if (mgr, c) in SKIP_COMMANDS
    )
    cmd_tools = cmd_count - cmd_skipped  # 1 tool per command, minus skipped

    v2_tools = 0
    v2_detail = {}
    for name, ep in v2.items():
        methods = len(ep.get("methods", ["GET"]))
        v2_tools += methods
        v2_detail[name] = methods

    global_tools = global_count  # 1 tool per global endpoint
    port_override = 1  # port override helper
    report_issue = 1  # error reporting helper
    overview = 1  # network overview composite tool
    search_tools = 1  # tool discovery helper

    total_tools = rest_tools + stat_tools + cmd_tools + v2_tools + global_tools + port_override + report_issue + overview + search_tools

    return {
        "endpoints": {
            "rest": rest_count,
            "stat": stat_count,
            "cmd_managers": cmd_manager_count,
            "cmd_commands": cmd_count,
            "v2": v2_count,
            "global": global_count,
            "list": list_count,
            "guest": guest_count,
            "websocket": ws_count,
            "total": total_endpoints,
        },
        "tools": {
            "rest": rest_tools,
            "stat": stat_tools,
            "cmd": cmd_tools,
            "v2": v2_tools,
            "global": global_tools,
            "port_override": port_override,
            "report_issue": report_issue,
            "overview": overview,
            "search_tools": search_tools,
            "total": total_tools,
        },
        "rest_detail": rest_detail,
        "rest_skipped": rest_skipped,
        "v2_detail": v2_detail,
        "cmd_detail": {
            mgr: ep.get("commands", [])
            for mgr, ep in cmd.items()
        },
    }


def count_readonly_breakdown() -> dict[str, int]:
    """Count read-only vs mutating tools from the spec.

    Returns {"readonly": N, "mutating": N}.
    """
    raw = json.loads(INVENTORY_PATH.read_text())
    rest = raw.get("rest_endpoints", {})
    stat = raw.get("stat_endpoints", {})
    cmd = raw.get("cmd_endpoints", {})
    v2 = raw.get("v2_endpoints", {})
    glb = raw.get("global_endpoints", {})

    ro = 0
    mut = 0

    # REST
    for name in rest:
        is_setting = name == "setting"
        is_readonly = name in READ_ONLY_REST
        is_crud = name in CRUD_REST
        if is_setting:
            ro += 2   # list_settings + get_setting
            mut += 1  # update_setting
        elif is_readonly:
            ro += 1   # list_*
        elif is_crud:
            ro += 2   # list_* + get_*
            mut += 2  # create_* + update_*
            if name not in NO_REST_DELETE:
                mut += 1  # delete_*

    # Stat: all read-only
    ro += len(stat)

    # Cmd: split by MUTATION_COMMANDS
    for mgr, ep in cmd.items():
        for c in ep.get("commands", []):
            key = (mgr, c)
            if key in SKIP_COMMANDS:
                continue
            if key in MUTATION_COMMANDS:
                mut += 1
            else:
                ro += 1

    # v2: GET = read-only, POST/PUT/DELETE = mutating
    for name, ep in v2.items():
        methods = ep.get("methods", ["GET"])
        for m in methods:
            if m == "GET":
                ro += 1
            else:
                mut += 1

    # Global: use MUTATING_GLOBALS
    for name in glb:
        if name in MUTATING_GLOBALS:
            mut += 1
        else:
            ro += 1

    # Port override: mutating
    mut += 1

    # Report issue: read-only
    ro += 1

    # Overview: read-only
    ro += 1

    # Search tools: read-only
    ro += 1

    return {"readonly": ro, "mutating": mut}


def count_module_breakdown(counts: dict) -> dict[str, dict]:
    """Compute per-module tool breakdown using the same mappings as the generator.

    Returns per-module dict with keys: v1, v2, v1_ro, v2_ro.
    """
    raw = json.loads(INVENTORY_PATH.read_text())
    rest = raw.get("rest_endpoints", {})
    stat = raw.get("stat_endpoints", {})
    cmd = raw.get("cmd_endpoints", {})
    v2 = raw.get("v2_endpoints", {})

    modules: dict[str, dict] = {
        m: {"v1": 0, "v2": 0, "v1_ro": 0, "v2_ro": 0} for m in MODULE_ORDER
    }

    # REST tools by module
    for name in rest:
        is_setting = name == "setting"
        is_readonly = name in READ_ONLY_REST
        is_crud = name in CRUD_REST
        if is_setting:
            tools = 3
            ro = 2  # list_settings + get_setting
        elif is_readonly:
            tools = 1
            ro = 1
        elif is_crud:
            tools = 4 if name in NO_REST_DELETE else 5
            ro = 2  # list_* + get_*
        else:
            continue
        mod = REST_MODULES.get(name, "advanced")
        modules[mod]["v1"] += tools
        modules[mod]["v1_ro"] += ro

    # Stat tools by module (all read-only)
    for name in stat:
        mod = STAT_MODULES.get(name, "monitor")
        modules[mod]["v1"] += 1
        modules[mod]["v1_ro"] += 1

    # Cmd tools by module
    for mgr, ep in cmd.items():
        for c in ep.get("commands", []):
            key = (mgr, c)
            if key in SKIP_COMMANDS:
                continue
            mod = CMD_MODULES.get(key, "admin")
            modules[mod]["v1"] += 1
            if key not in MUTATION_COMMANDS:
                modules[mod]["v1_ro"] += 1

    # v2 tools by module
    for name, ep in v2.items():
        methods = ep.get("methods", ["GET"])
        mod = V2_MODULES.get(name, "advanced")
        modules[mod]["v2"] += len(methods)
        # Only GET methods are read-only
        modules[mod]["v2_ro"] += methods.count("GET")

    # Port override helper → device module (mutating, not read-only)
    modules["device"]["v1"] += 1

    return modules


def count_actual_tools() -> int | None:
    """Count actual tool functions in generated/server.py if it exists."""
    server_path = ROOT / "generated" / "server.py"
    if not server_path.exists():
        return None
    code = server_path.read_text()
    return len(re.findall(r"^\s*async def unifi_", code, re.MULTILINE))


def main():
    counts = count_from_spec()
    actual = count_actual_tools()

    print("=" * 60)
    print("ENDPOINT COUNTS (from endpoint-inventory.json)")
    print("=" * 60)
    ep = counts["endpoints"]
    print(f"  REST endpoints:      {ep['rest']}")
    print(f"  Stat endpoints:      {ep['stat']}")
    print(f"  Cmd managers:        {ep['cmd_managers']} ({ep['cmd_commands']} commands)")
    print(f"  v2 endpoints:        {ep['v2']}")
    print(f"  Global endpoints:    {ep['global']}")
    if ep["list"]:
        print(f"  List endpoints:      {ep['list']}  (not yet generating tools)")
    if ep["guest"]:
        print(f"  Guest endpoints:     {ep['guest']}  (not yet generating tools)")
    if ep["websocket"]:
        print(f"  WebSocket endpoints: {ep['websocket']}  (not yet generating tools)")
    print(f"  TOTAL endpoints:     {ep['total']}")

    print()
    print("=" * 60)
    print("TOOL COUNTS (computed from spec)")
    print("=" * 60)
    t = counts["tools"]
    print(f"  REST tools:          {t['rest']}")
    for name, n in sorted(counts["rest_detail"].items()):
        label = "CRUD" if n == 5 else ("CRUD-no-delete" if n == 4 else ("settings" if n == 3 else "read-only"))
        print(f"    {name:25s} → {n} tools ({label})")
    if counts["rest_skipped"]:
        print(f"  REST skipped:        {len(counts['rest_skipped'])} (no RESOURCE_NAMES entry)")
        for name in sorted(counts["rest_skipped"]):
            print(f"    {name:25s}   (needs naming.py entry)")
    print(f"  Stat tools:          {t['stat']}")
    print(f"  Cmd tools:           {t['cmd']}")
    for mgr, cmds in sorted(counts["cmd_detail"].items()):
        print(f"    {mgr:25s} → {len(cmds)} commands")
    print(f"  v2 tools:            {t['v2']}")
    for name, n in sorted(counts["v2_detail"].items()):
        print(f"    {name:25s} → {n} tools")
    print(f"  Global tools:        {t['global']}")
    print(f"  Port override:       {t['port_override']}")
    print(f"  Report issue:        {t['report_issue']}")
    print(f"  Overview:            {t['overview']}")
    print(f"  Search tools:        {t['search_tools']}")
    print(f"  TOTAL tools:         {t['total']}")

    # Module breakdown
    modules = count_module_breakdown(counts)
    print()
    print("=" * 60)
    print("MODULE BREAKDOWN")
    print("=" * 60)
    always_on = t["global"] + t["report_issue"] + t["overview"] + t["search_tools"]
    print(f"  {'Module':<12s} {'v1':>5s} {'v2':>5s} {'Total':>7s}  (with always-on: +{always_on})")
    print(f"  {'-'*12:s} {'-'*5:s} {'-'*5:s} {'-'*7:s}")
    total_v1 = 0
    total_v2 = 0
    for mod in MODULE_ORDER:
        m = modules[mod]
        mod_total = m["v1"] + m["v2"]
        total_v1 += m["v1"]
        total_v2 += m["v2"]
        print(f"  {mod:<12s} {m['v1']:>5d} {m['v2']:>5d} {mod_total:>7d}")
    print(f"  {'-'*12:s} {'-'*5:s} {'-'*5:s} {'-'*7:s}")
    print(f"  {'SUBTOTAL':<12s} {total_v1:>5d} {total_v2:>5d} {total_v1 + total_v2:>7d}")
    print(f"  {'always-on':<12s} {'':>5s} {'':>5s} {always_on:>7d}  (global + report_issue)")
    print(f"  {'GRAND TOTAL':<12s} {'':>5s} {'':>5s} {total_v1 + total_v2 + always_on:>7d}")

    # Read-only breakdown
    ro = count_readonly_breakdown()
    print()
    print("=" * 60)
    print("READ-ONLY BREAKDOWN")
    print("=" * 60)
    print(f"  Read-only tools:     {ro['readonly']}  (UNIFI_READ_ONLY=true)")
    print(f"  Mutating tools:      {ro['mutating']}  (stripped in read-only mode)")
    print(f"  Total:               {ro['readonly'] + ro['mutating']}")
    assert ro["readonly"] + ro["mutating"] == t["total"], "Read-only + mutating != total"

    # Per-module read-only breakdown
    print()
    print(f"  {'Module':<12s} {'v1_ro':>6s} {'v2_ro':>6s} {'Total':>7s}")
    print(f"  {'-'*12:s} {'-'*6:s} {'-'*6:s} {'-'*7:s}")
    for mod in MODULE_ORDER:
        m = modules[mod]
        mod_ro = m["v1_ro"] + m["v2_ro"]
        print(f"  {mod:<12s} {m['v1_ro']:>6d} {m['v2_ro']:>6d} {mod_ro:>7d}")

    if actual is not None:
        print()
        print("=" * 60)
        print("VERIFICATION")
        print("=" * 60)
        print(f"  Computed from spec:  {t['total']}")
        print(f"  Actual in server.py: {actual}")
        if t["total"] == actual:
            print("  \u2713 MATCH")
        else:
            print(f"  \u2717 MISMATCH (diff: {actual - t['total']})")


if __name__ == "__main__":
    main()
