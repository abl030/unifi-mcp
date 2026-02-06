"""Assemble Jinja2 template context from loaded data + schemas + naming."""

from __future__ import annotations

from generator.loader import APIInventory
from generator.naming import (
    COMMAND_PARAMS,
    COMMAND_TOOL_NAMES,
    CRUD_REST,
    DEVICE_DEPENDENT_COMMANDS,
    HARDWARE_DEPENDENT_REST,
    MINIMAL_CREATE_PAYLOADS,
    MUTATION_COMMANDS,
    READ_ONLY_REST,
    RESOURCE_NAMES,
    SAFE_TEST_COMMANDS,
    STAT_NAMES,
    STAT_OVERRIDES,
    V2_RESOURCE_NAMES,
)
from generator.schema_inference import FieldInfo, infer_schema


def _schema_to_dict(schema: dict[str, FieldInfo]) -> list[dict]:
    """Convert FieldInfo schema to serializable dicts for templates."""
    return [
        {
            "name": fi.name,
            "python_type": fi.python_type,
            "read_only": fi.read_only,
            "common": fi.common,
            "annotation": fi.annotation,
        }
        for fi in schema.values()
    ]


def _writable_fields(schema: dict[str, FieldInfo]) -> list[dict]:
    """Return only writable fields from schema."""
    return [
        {
            "name": fi.name,
            "python_type": fi.python_type,
            "annotation": fi.annotation,
            "common": fi.common,
        }
        for fi in schema.values()
        if not fi.read_only
    ]


def build_context(inventory: APIInventory) -> dict:
    """Build the full Jinja2 template context."""
    ctx: dict = {
        "controller_version": inventory.controller_version,
        "rest_tools": [],
        "stat_tools": [],
        "cmd_tools": [],
        "v2_tools": [],
        "global_tools": [],
    }

    # --- REST endpoints ---
    for name, ep in sorted(inventory.rest_endpoints.items()):
        singular, plural = RESOURCE_NAMES.get(name, (name, name + "s"))
        schema = infer_schema(ep.samples)
        is_crud = name in CRUD_REST
        is_readonly = name in READ_ONLY_REST
        is_setting = name == "setting"

        is_hardware_dependent = name in HARDWARE_DEPENDENT_REST

        tool = {
            "resource": name,
            "singular": singular,
            "plural": plural,
            "path": ep.path,
            "methods": ep.methods,
            "is_crud": is_crud,
            "is_readonly": is_readonly,
            "is_setting": is_setting,
            "is_hardware_dependent": is_hardware_dependent,
            "has_samples": bool(ep.samples),
            "schema": _schema_to_dict(schema),
            "writable_fields": _writable_fields(schema),
            "create_payload": MINIMAL_CREATE_PAYLOADS.get(name, {}),
        }
        ctx["rest_tools"].append(tool)

    # --- Stat endpoints ---
    for name, ep in sorted(inventory.stat_endpoints.items()):
        display_name = STAT_NAMES.get(name, name)
        schema = infer_schema(ep.samples)

        # Apply method/body overrides for endpoints that need them
        overrides = STAT_OVERRIDES.get(name, {})
        method = overrides.get("method", ep.method)
        post_body = overrides.get("body", {})

        tool = {
            "resource": name,
            "display_name": display_name,
            "path": ep.path,
            "method": method,
            "post_body": repr(post_body) if post_body else "{}",
            "has_samples": bool(ep.samples),
            "schema": _schema_to_dict(schema),
            "note": ep.note,
            "sample_fields": [fi.name for fi in schema.values() if fi.common][:5],
        }
        ctx["stat_tools"].append(tool)

    # --- Command endpoints ---
    for mgr_name, ep in sorted(inventory.cmd_endpoints.items()):
        for cmd in ep.commands:
            key = (mgr_name, cmd)
            tool_name = COMMAND_TOOL_NAMES.get(key, f"{cmd.replace('-', '_')}_{mgr_name}")
            params = COMMAND_PARAMS.get(key, {})
            is_mutation = key in MUTATION_COMMANDS
            is_safe_test = key in SAFE_TEST_COMMANDS
            is_device_dependent = key in DEVICE_DEPENDENT_COMMANDS

            tool = {
                "manager": mgr_name,
                "command": cmd,
                "tool_name": tool_name,
                "path": ep.path,
                "params": params,
                "is_mutation": is_mutation,
                "is_safe_test": is_safe_test,
                "is_device_dependent": is_device_dependent,
            }
            ctx["cmd_tools"].append(tool)

    # --- v2 endpoints ---
    for name, ep in sorted(inventory.v2_endpoints.items()):
        singular, plural = V2_RESOURCE_NAMES.get(name, (name, name + "s"))
        schema = infer_schema(ep.samples)

        tool = {
            "resource": name,
            "singular": singular,
            "plural": plural,
            "path": ep.path,
            "methods": ep.methods,
            "has_samples": bool(ep.samples),
            "schema": _schema_to_dict(schema),
            "writable_fields": _writable_fields(schema),
        }
        ctx["v2_tools"].append(tool)

    # --- Global endpoints ---
    for name, ep in sorted(inventory.global_endpoints.items()):
        tool = {
            "name": name,
            "method": ep.method,
            "path": ep.path,
            "auth": ep.auth,
        }
        ctx["global_tools"].append(tool)

    # Summary counts
    ctx["tool_count"] = (
        sum(
            (5 if t["is_crud"] else 3 if t["is_setting"] else 1)
            for t in ctx["rest_tools"]
        )
        + len(ctx["stat_tools"])
        + len(ctx["cmd_tools"])
        + sum(
            len(t["methods"]) + 1  # list + CRUD per method
            for t in ctx["v2_tools"]
        )
        + len(ctx["global_tools"])
        + 1  # port override helper
    )

    return ctx
