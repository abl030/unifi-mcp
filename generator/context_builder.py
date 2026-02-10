"""Assemble Jinja2 template context from loaded data + schemas + naming."""

from __future__ import annotations

from generator.loader import APIInventory
from generator.naming import (
    CMD_MODULES,
    COMMAND_PARAMS,
    COMMAND_TOOL_NAMES,
    CRUD_REST,
    DEVICE_DEPENDENT_COMMANDS,
    FULL_OBJECT_UPDATE_REST,
    HARDWARE_DEPENDENT_REST,
    MODULE_ORDER,
    NO_REST_DELETE,
    REST_MODULES,
    STAT_MODULES,
    V2_CREATE_HINTS,
    V2_MODULES,
    ID_CROSS_REFS,
    MINIMAL_CREATE_PAYLOADS,
    MUTATION_COMMANDS,
    READ_ONLY_REST,
    REQUIRED_CREATE_FIELDS,
    RESOURCE_NAMES,
    SAFE_TEST_COMMANDS,
    SKIP_COMMANDS,
    STAT_NAMES,
    STAT_OVERRIDES,
    UNTESTABLE_GLOBALS,
    V2_RESOURCE_NAMES,
    WORKFLOW_HINTS,
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
            "enum_values": fi.enum_values,
        }
        for fi in schema.values()
    ]


def _field_description(fi: FieldInfo) -> str:
    """Build a rich description string for a field: name (type: enum|cross-ref)."""
    parts = [fi.name]
    type_detail = fi.python_type
    if fi.enum_values:
        type_detail += ": " + "|".join(f'"{v}"' for v in fi.enum_values)
    cross_ref = ID_CROSS_REFS.get(fi.name)
    if cross_ref:
        type_detail += f", see {cross_ref}"
    parts.append(f"({type_detail})")
    return " ".join(parts)


def _field_sort_key(fi: FieldInfo) -> tuple[int, str]:
    """Sort fields: enum/cross-ref fields first, then common, then alpha."""
    has_enum = bool(fi.enum_values)
    has_xref = fi.name in ID_CROSS_REFS
    # Lower = first: fields with enums or cross-refs are most useful
    priority = 0 if (has_enum or has_xref) else (1 if fi.common else 2)
    return (priority, fi.name)


def _writable_fields(schema: dict[str, FieldInfo]) -> list[dict]:
    """Return only writable fields from schema, prioritized for usefulness."""
    fields = [fi for fi in schema.values() if not fi.read_only]
    fields.sort(key=_field_sort_key)
    return [
        {
            "name": fi.name,
            "python_type": fi.python_type,
            "annotation": fi.annotation,
            "common": fi.common,
            "enum_values": fi.enum_values,
            "description": _field_description(fi),
        }
        for fi in fields
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
            "required_create_fields": REQUIRED_CREATE_FIELDS.get(name, ""),
            "full_object_update": name in FULL_OBJECT_UPDATE_REST,
            "no_rest_delete": name in NO_REST_DELETE,
            "workflow_hint": WORKFLOW_HINTS.get(name, ""),
        }
        tool["module"] = REST_MODULES.get(name, "advanced")
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
        tool["module"] = STAT_MODULES.get(name, "monitor")
        ctx["stat_tools"].append(tool)

    # --- Command endpoints ---
    for mgr_name, ep in sorted(inventory.cmd_endpoints.items()):
        for cmd in ep.commands:
            key = (mgr_name, cmd)
            if key in SKIP_COMMANDS:
                continue
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
            tool["module"] = CMD_MODULES.get(key, "admin")
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
            "create_hint": V2_CREATE_HINTS.get(name, ""),
        }
        tool["module"] = V2_MODULES.get(name, "advanced")
        ctx["v2_tools"].append(tool)

    # --- Global endpoints ---
    for name, ep in sorted(inventory.global_endpoints.items()):
        tool = {
            "name": name,
            "method": ep.method,
            "path": ep.path,
            "auth": ep.auth,
            "skip_test": name in UNTESTABLE_GLOBALS,
        }
        ctx["global_tools"].append(tool)

    # --- Group tools by module for per-module template blocks ---
    from collections import defaultdict

    rest_by_module: dict[str, list] = defaultdict(list)
    for t in ctx["rest_tools"]:
        rest_by_module[t["module"]].append(t)
    stat_by_module: dict[str, list] = defaultdict(list)
    for t in ctx["stat_tools"]:
        stat_by_module[t["module"]].append(t)
    cmd_by_module: dict[str, list] = defaultdict(list)
    for t in ctx["cmd_tools"]:
        cmd_by_module[t["module"]].append(t)
    v2_by_module: dict[str, list] = defaultdict(list)
    for t in ctx["v2_tools"]:
        v2_by_module[t["module"]].append(t)

    ctx["rest_by_module"] = dict(rest_by_module)
    ctx["stat_by_module"] = dict(stat_by_module)
    ctx["cmd_by_module"] = dict(cmd_by_module)
    ctx["v2_by_module"] = dict(v2_by_module)
    ctx["module_order"] = MODULE_ORDER

    # Summary counts
    ctx["tool_count"] = (
        sum(
            (4 if t["is_crud"] and t.get("no_rest_delete") else
             5 if t["is_crud"] else
             3 if t["is_setting"] else 1)
            for t in ctx["rest_tools"]
        )
        + len(ctx["stat_tools"])
        + len(ctx["cmd_tools"])
        + sum(
            len(t["methods"])  # GET=list, POST=create, PUT=update, DELETE=delete
            for t in ctx["v2_tools"]
        )
        + len(ctx["global_tools"])
        + 1  # port override helper
        + 1  # report issue helper
    )

    return ctx
