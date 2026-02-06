#!/usr/bin/env python3
"""UniFi MCP Server Generator.

Reads endpoint-inventory.json + api-samples/ and produces:
  - generated/server.py (FastMCP server with ~139 tools)
  - generated/conftest.py (pytest fixtures)
  - generated/tests/test_rest_*.py (per-resource CRUD tests)
  - generated/tests/test_stat.py
  - generated/tests/test_cmd.py
  - generated/tests/test_v2.py
  - generated/tests/test_global.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from generator.context_builder import build_context
from generator.loader import load_inventory
from generator.naming import HARDWARE_DEPENDENT_REST, MINIMAL_CREATE_PAYLOADS, READ_ONLY_REST

ROOT = Path(__file__).parent
INVENTORY_PATH = ROOT / "endpoint-inventory.json"
SAMPLES_DIR = ROOT / "api-samples"
TEMPLATES_DIR = ROOT / "templates"
OUTPUT_DIR = ROOT / "generated"
TESTS_DIR = OUTPUT_DIR / "tests"


def _render_create_payload(resource: str, create_payload: dict) -> str:
    """Render a create payload dict as Python source code for tests.

    Replaces {unique} with a f-string variable and {default_network_id}
    with the fixture value.
    """
    if not create_payload:
        return "{}"
    lines = ["{"]
    for key, value in create_payload.items():
        if isinstance(value, str):
            rendered = value.replace("{unique}", f"{{unique}}")
            rendered = rendered.replace("{default_network_id}", "{default_network_id}")
            if "{unique}" in value or "{default_network_id}" in value:
                lines.append(f'            "{key}": f"{rendered}",')
            else:
                lines.append(f'            "{key}": "{rendered}",')
        elif isinstance(value, bool):
            lines.append(f'            "{key}": {value},')
        elif isinstance(value, (int, float)):
            lines.append(f'            "{key}": {value},')
        elif isinstance(value, list):
            lines.append(f'            "{key}": {json.dumps(value)},')
        elif isinstance(value, dict):
            lines.append(f'            "{key}": {json.dumps(value)},')
        else:
            lines.append(f'            "{key}": {json.dumps(value)},')
    lines.append("        }")
    return "\n".join(lines)


def _needs_network_id(resource: str) -> bool:
    """Check if a resource's create payload references default_network_id."""
    payload = MINIMAL_CREATE_PAYLOADS.get(resource, {})
    for v in payload.values():
        if isinstance(v, str) and "{default_network_id}" in v:
            return True
    return False


def _get_update_field(resource: str) -> tuple[str | None, str | None]:
    """Return a (field_name, update_value) pair for update tests."""
    update_map = {
        "networkconf": ("name", 'f"updated_network_{unique}"'),
        "wlanconf": ("name", 'f"updated_wlan_{unique}"'),
        "wlangroup": ("name", 'f"updated_wlangroup_{unique}"'),
        "portconf": ("name", 'f"updated_portprofile_{unique}"'),
        "portforward": ("name", 'f"updated_portforward_{unique}"'),
        "firewallrule": ("name", 'f"updated_fwrule_{unique}"'),
        "firewallgroup": ("name", 'f"updated_fwgroup_{unique}"'),
        "dynamicdns": ("host_name", 'f"updated_{unique}.example.com"'),
        "routing": ("name", 'f"updated_route_{unique}"'),
        "usergroup": ("name", 'f"updated_usergroup_{unique}"'),
        "user": ("name", 'f"updated_user_{unique}"'),
        "tag": ("name", 'f"updated_tag_{unique}"'),
        "radiusprofile": ("name", 'f"updated_radius_{unique}"'),
        "account": ("name", 'f"updated_account_{unique}"'),
    }
    field, value = update_map.get(resource, (None, None))
    return field, value


def generate() -> None:
    """Run the full generation pipeline."""
    print("Loading endpoint inventory...")
    inventory = load_inventory(INVENTORY_PATH, SAMPLES_DIR)
    print(f"  Controller version: {inventory.controller_version}")
    print(f"  REST endpoints: {len(inventory.rest_endpoints)}")
    print(f"  Stat endpoints: {len(inventory.stat_endpoints)}")
    print(f"  Cmd endpoints: {len(inventory.cmd_endpoints)}")
    print(f"  v2 endpoints: {len(inventory.v2_endpoints)}")
    print(f"  Global endpoints: {len(inventory.global_endpoints)}")

    print("\nBuilding template context...")
    ctx = build_context(inventory)
    print(f"  Estimated tool count: {ctx['tool_count']}")

    # Set up Jinja2
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # Ensure output dirs exist
    OUTPUT_DIR.mkdir(exist_ok=True)
    TESTS_DIR.mkdir(exist_ok=True)

    # --- Render server.py ---
    print("\nRendering server.py...")
    server_template = env.get_template("server.py.j2")
    server_code = server_template.render(**ctx)
    (OUTPUT_DIR / "server.py").write_text(server_code)
    # Count tool functions
    tool_count = len(re.findall(r"^async def unifi_", server_code, re.MULTILINE))
    print(f"  Generated {tool_count} tool functions")

    # --- Render conftest.py ---
    print("Rendering conftest.py...")
    conftest_template = env.get_template("conftest.py.j2")
    conftest_code = conftest_template.render(**ctx)
    (OUTPUT_DIR / "conftest.py").write_text(conftest_code)

    # --- Render per-resource REST test files ---
    print("Rendering REST test files...")
    rest_template = env.get_template("test_rest.py.j2")
    rest_test_count = 0
    for tool in ctx["rest_tools"]:
        # Enhance tool context for the test template
        tool_ctx = dict(tool)
        tool_ctx["create_payload_rendered"] = _render_create_payload(
            tool["resource"], tool.get("create_payload", {})
        )
        tool_ctx["needs_network_id"] = _needs_network_id(tool["resource"])
        tool_ctx["is_hardware_dependent"] = tool["resource"] in HARDWARE_DEPENDENT_REST
        update_field, update_value = _get_update_field(tool["resource"])
        tool_ctx["update_field"] = update_field
        tool_ctx["update_value"] = update_value

        test_code = rest_template.render(tool=tool_ctx)
        filename = f"test_rest_{tool['resource']}.py"
        (TESTS_DIR / filename).write_text(test_code)
        rest_test_count += 1
    print(f"  Generated {rest_test_count} REST test files")

    # --- Render stat tests ---
    print("Rendering stat tests...")
    stat_template = env.get_template("test_stat.py.j2")
    stat_code = stat_template.render(**ctx)
    (TESTS_DIR / "test_stat.py").write_text(stat_code)

    # --- Render command tests ---
    print("Rendering command tests...")
    cmd_template = env.get_template("test_cmd.py.j2")
    cmd_code = cmd_template.render(**ctx)
    (TESTS_DIR / "test_cmd.py").write_text(cmd_code)

    # --- Render v2 tests ---
    print("Rendering v2 tests...")
    v2_template = env.get_template("test_v2.py.j2")
    v2_code = v2_template.render(**ctx)
    (TESTS_DIR / "test_v2.py").write_text(v2_code)

    # --- Render global tests ---
    print("Rendering global tests...")
    global_template = env.get_template("test_global.py.j2")
    global_code = global_template.render(**ctx)
    (TESTS_DIR / "test_global.py").write_text(global_code)

    # --- Render server validation tests ---
    print("Rendering server validation tests...")
    server_test_template = env.get_template("test_server.py.j2")
    server_test_code = server_test_template.render(**ctx)
    (TESTS_DIR / "test_server.py").write_text(server_test_code)

    # --- Write tests __init__.py ---
    (TESTS_DIR / "__init__.py").write_text("")

    # Summary
    test_files = list(TESTS_DIR.glob("test_*.py"))
    print(f"\n=== Generation Complete ===")
    print(f"  Server: generated/server.py ({tool_count} tools)")
    print(f"  Config: generated/conftest.py")
    print(f"  Tests:  {len(test_files)} test files in generated/tests/")
    print(f"\nTo run: python -c \"import generated.server\"")


if __name__ == "__main__":
    generate()
