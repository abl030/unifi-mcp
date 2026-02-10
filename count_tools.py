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
INVENTORY_PATH = ROOT / "endpoint-inventory.json"

# Import the authoritative sets from the generator so we stay in sync.
from generator.naming import CRUD_REST, READ_ONLY_REST


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
            tools = 5
        else:
            # Not in RESOURCE_NAMES → template skips it, no tools generated
            rest_skipped.append(name)
            continue
        rest_tools += tools
        rest_detail[name] = tools

    stat_tools = stat_count  # 1 tool per stat endpoint

    cmd_tools = cmd_count  # 1 tool per command

    v2_tools = 0
    v2_detail = {}
    for name, ep in v2.items():
        methods = len(ep.get("methods", ["GET"]))
        v2_tools += methods
        v2_detail[name] = methods

    global_tools = global_count  # 1 tool per global endpoint
    port_override = 1  # port override helper

    total_tools = rest_tools + stat_tools + cmd_tools + v2_tools + global_tools + port_override

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


def count_actual_tools() -> int | None:
    """Count actual tool functions in generated/server.py if it exists."""
    server_path = ROOT / "generated" / "server.py"
    if not server_path.exists():
        return None
    code = server_path.read_text()
    return len(re.findall(r"^async def unifi_", code, re.MULTILINE))


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
        label = "CRUD" if n == 5 else ("settings" if n == 3 else "read-only")
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
    print(f"  TOTAL tools:         {t['total']}")

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
