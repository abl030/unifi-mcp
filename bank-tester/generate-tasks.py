#!/usr/bin/env python3
"""
Generate bank tester task files from task-config.yaml.

Reads the task configuration and produces markdown task files in bank-tester/tasks/.
Imports tool names from generator/naming.py and verifies coverage against generated/server.py.

Usage:
    uv run python bank-tester/generate-tasks.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

# Add repo root to path so we can import generator modules
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from generator.naming import (
    RESOURCE_NAMES,
    READ_ONLY_REST,
)

CONFIG_PATH = REPO_ROOT / "bank-tester" / "task-config.yaml"
TASKS_DIR = REPO_ROOT / "bank-tester" / "tasks"
SERVER_PY = REPO_ROOT / "generated" / "server.py"


def load_config() -> list[dict[str, Any]]:
    """Load and return the task config."""
    with open(CONFIG_PATH) as f:
        config = yaml.safe_load(f)
    return config.get("tasks", [])


def extract_all_tool_names() -> set[str]:
    """Extract all unifi_* tool names from generated/server.py."""
    if not SERVER_PY.exists():
        print(f"WARNING: {SERVER_PY} not found, coverage check will be incomplete")
        return set()
    text = SERVER_PY.read_text()
    return set(re.findall(r"async def (unifi_\w+)\(", text))


def resource_to_tools(resource: str) -> dict[str, str]:
    """Get tool names for a REST resource."""
    if resource not in RESOURCE_NAMES:
        return {}
    singular, plural = RESOURCE_NAMES[resource]
    tools = {
        "list": f"unifi_list_{plural}",
        "get": f"unifi_get_{singular}",
    }
    if resource not in READ_ONLY_REST:
        tools["create"] = f"unifi_create_{singular}"
        tools["update"] = f"unifi_update_{singular}"
        tools["delete"] = f"unifi_delete_{singular}"
    return tools


def format_values(values: Any, indent: int = 2) -> str:
    """Format test values as human-readable key=value pairs."""
    if not values:
        return "(no parameters needed)"
    if isinstance(values, dict):
        lines = []
        for k, v in values.items():
            if isinstance(v, list):
                v_display = repr(v)
            elif isinstance(v, str) and len(v) > 60:
                v_display = v[:57] + "..."
            else:
                v_display = repr(v) if not isinstance(v, str) else v
            lines.append(f"{'  ' * indent}- `{k}`: `{v_display}`")
        return "\n".join(lines)
    return str(values)


def generate_crud_steps(
    ep: dict,
    step_num: int,
    all_steps: list[str],
    cleanup_steps: list[str],
    tools_exercised: list[str],
) -> int:
    """Generate CRUD lifecycle steps for a REST resource."""
    resource = ep["resource"]
    tools = resource_to_tools(resource)
    if not tools:
        all_steps.append(f"{step_num}. **SKIP** — resource `{resource}` not in RESOURCE_NAMES")
        return step_num + 1

    create_values = ep.get("create_values", {})
    update_field = ep.get("update_field")
    update_value = ep.get("update_value")
    notes = ep.get("notes", "")
    hw_dep = ep.get("hardware_dependent", False)

    extra_note = f" ({notes})" if notes else ""
    hw_note = " **[Hardware-dependent — expect error]**" if hw_dep else ""

    # Create
    if "create" in tools:
        all_steps.append(
            f"{step_num}. **Create** using `{tools['create']}` with `confirm=True`{hw_note}{extra_note}:\n{format_values(create_values)}"
        )
        tools_exercised.append(tools["create"])
        step_num += 1

    # List
    all_steps.append(
        f"{step_num}. **List** using `{tools['list']}` — verify the created resource appears"
    )
    tools_exercised.append(tools["list"])
    step_num += 1

    # Get
    if "create" in tools:
        all_steps.append(
            f"{step_num}. **Get** using `{tools['get']}` with the ID from the create response"
        )
    else:
        all_steps.append(
            f"{step_num}. **Get** using `{tools['get']}` — read a single resource"
        )
    tools_exercised.append(tools["get"])
    step_num += 1

    # Update
    if update_field and "update" in tools:
        all_steps.append(
            f'{step_num}. **Update** using `{tools["update"]}` with `confirm=True` — set `{update_field}` to `{update_value}`'
        )
        tools_exercised.append(tools["update"])
        step_num += 1

        all_steps.append(
            f"{step_num}. **Get** again using `{tools['get']}` — verify `{update_field}` was updated"
        )
        step_num += 1

    # Delete goes in cleanup
    if "delete" in tools:
        cleanup_steps.insert(
            0,
            f"- Delete using `{tools['delete']}` with `confirm=True` (ID from create step)",
        )
        tools_exercised.append(tools["delete"])

    return step_num


def generate_read_only_steps(
    ep: dict,
    step_num: int,
    all_steps: list[str],
    tools_exercised: list[str],
) -> int:
    """Generate read-only GET steps."""
    tool = ep["tool"]
    notes = ep.get("notes", "")
    hw_dep = ep.get("hardware_dependent", False)

    extra_note = f" ({notes})" if notes else ""
    hw_note = " **[Hardware-dependent — may return empty or error]**" if hw_dep else ""

    all_steps.append(
        f"{step_num}. **Read** using `{tool}`{hw_note}{extra_note}"
    )
    tools_exercised.append(tool)
    return step_num + 1


def generate_stat_steps(
    ep: dict,
    step_num: int,
    all_steps: list[str],
    tools_exercised: list[str],
) -> int:
    """Generate stat endpoint steps."""
    tool = ep["tool"]
    notes = ep.get("notes", "")

    extra_note = f" ({notes})" if notes else ""

    all_steps.append(
        f"{step_num}. **Read stat** using `{tool}`{extra_note}"
    )
    tools_exercised.append(tool)
    return step_num + 1


def generate_cmd_steps(
    ep: dict,
    step_num: int,
    all_steps: list[str],
    cleanup_steps: list[str],
    tools_exercised: list[str],
) -> int:
    """Generate command endpoint steps."""
    tool = ep["tool"]
    params = ep.get("params", {})
    notes = ep.get("notes", "")
    mutation = ep.get("mutation", False)
    hw_dep = ep.get("hardware_dependent", False)

    extra_note = f" ({notes})" if notes else ""
    hw_note = " **[Hardware-dependent — expect error]**" if hw_dep else ""
    confirm_note = " with `confirm=True`" if mutation else ""

    if params:
        params_str = format_values(params)
        all_steps.append(
            f"{step_num}. **Execute** `{tool}`{confirm_note}{hw_note}{extra_note}:\n{params_str}"
        )
    else:
        all_steps.append(
            f"{step_num}. **Execute** `{tool}`{confirm_note}{hw_note}{extra_note}"
        )
    tools_exercised.append(tool)
    return step_num + 1


def generate_settings_read_steps(
    ep: dict,
    step_num: int,
    all_steps: list[str],
    tools_exercised: list[str],
) -> int:
    """Generate steps to read all setting keys."""
    tool = ep["tool"]
    keys = ep.get("keys", [])

    if not keys:
        all_steps.append(
            f"{step_num}. **Read** using `{tool}`"
        )
        tools_exercised.append(tool)
        return step_num + 1

    for key in keys:
        all_steps.append(
            f'{step_num}. **Read setting** using `{tool}` with `key="{key}"`'
        )
        step_num += 1

    tools_exercised.append(tool)
    return step_num


def generate_settings_write_steps(
    ep: dict,
    step_num: int,
    all_steps: list[str],
    tools_exercised: list[str],
) -> int:
    """Generate steps to write and restore a setting."""
    key = ep["key"]
    update_field = ep.get("update_field")
    update_value = ep.get("update_value")
    restore_value = ep.get("restore_value")
    notes = ep.get("notes", "")
    extra_note = f" ({notes})" if notes else ""

    # Read current
    all_steps.append(
        f'{step_num}. **Read setting** using `unifi_get_setting` with `key="{key}"` — note current value of `{update_field}`{extra_note}'
    )
    tools_exercised.append("unifi_get_setting")
    step_num += 1

    # Update
    all_steps.append(
        f'{step_num}. **Update setting** using `unifi_update_setting` with `key="{key}"`, `data={{"{update_field}": "{update_value}"}}`, `confirm=True`'
    )
    tools_exercised.append("unifi_update_setting")
    step_num += 1

    # Verify
    all_steps.append(
        f'{step_num}. **Verify** using `unifi_get_setting` with `key="{key}"` — confirm `{update_field}` changed'
    )
    step_num += 1

    # Restore
    if restore_value is not None:
        all_steps.append(
            f'{step_num}. **Restore** using `unifi_update_setting` with `key="{key}"`, `data={{"{update_field}": "{restore_value}"}}`, `confirm=True`'
        )
        step_num += 1

    return step_num


def generate_v2_steps(
    ep: dict,
    step_num: int,
    all_steps: list[str],
    cleanup_steps: list[str],
    tools_exercised: list[str],
) -> int:
    """Generate v2 API steps."""
    v2_tools = ep.get("tools", [])
    create_values = ep.get("create_values", {})
    update_field = ep.get("update_field")
    update_value = ep.get("update_value")

    is_crud = ep.get("v2_crud", False)

    for tool in v2_tools:
        if "list" in tool:
            all_steps.append(f"{step_num}. **List** using `{tool}`")
            tools_exercised.append(tool)
            step_num += 1
        elif "create" in tool and is_crud:
            all_steps.append(
                f"{step_num}. **Create** using `{tool}` with `confirm=True`:\n{format_values(create_values)}"
            )
            tools_exercised.append(tool)
            step_num += 1
        elif "update" in tool:
            if is_crud and update_field:
                all_steps.append(
                    f'{step_num}. **Update** using `{tool}` with `confirm=True` — set `{update_field}` to `{update_value}`'
                )
            else:
                all_steps.append(
                    f"{step_num}. **Update** using `{tool}` with `confirm=True` — read current data, modify, and PUT back"
                )
            tools_exercised.append(tool)
            step_num += 1
        elif "delete" in tool and is_crud:
            cleanup_steps.insert(
                0,
                f"- Delete using `{tool}` with `confirm=True` (ID from create step)",
            )
            tools_exercised.append(tool)

    return step_num


def generate_systematic_task(task: dict, task_num: str) -> str:
    """Generate a systematic task file."""
    title = task["title"]
    endpoints = task.get("endpoints", [])
    notes = task.get("notes", "")

    task_id_suffix = title.lower()
    for char in "— ,&()/'":
        task_id_suffix = task_id_suffix.replace(char, "-")
    task_id_suffix = re.sub(r"-+", "-", task_id_suffix).strip("-")[:50]

    all_steps: list[str] = []
    cleanup_steps: list[str] = []
    tools_exercised: list[str] = []
    step_num = 1

    for ep in endpoints:
        if ep.get("crud"):
            step_num = generate_crud_steps(
                ep, step_num, all_steps, cleanup_steps, tools_exercised
            )
        elif ep.get("read_only"):
            step_num = generate_read_only_steps(
                ep, step_num, all_steps, tools_exercised
            )
        elif ep.get("stat"):
            step_num = generate_stat_steps(
                ep, step_num, all_steps, tools_exercised
            )
        elif ep.get("cmd"):
            step_num = generate_cmd_steps(
                ep, step_num, all_steps, cleanup_steps, tools_exercised
            )
        elif ep.get("settings_read"):
            step_num = generate_settings_read_steps(
                ep, step_num, all_steps, tools_exercised
            )
        elif ep.get("settings_write"):
            step_num = generate_settings_write_steps(
                ep, step_num, all_steps, tools_exercised
            )
        elif ep.get("v2_crud") or ep.get("v2_read"):
            step_num = generate_v2_steps(
                ep, step_num, all_steps, cleanup_steps, tools_exercised
            )

    # Deduplicate tools while preserving order
    unique_tools = list(dict.fromkeys(tools_exercised))

    # Build markdown
    lines = [
        f"## Task {task_num}: {title}",
        "",
        f"**task_id**: {task_num}-{task_id_suffix}",
        "",
        f"**Objective**: Exercise all tools in the {task.get('subsystem', 'unknown')} subsystem.",
        "",
        f"**Tools to exercise** ({len(unique_tools)}):",
    ]
    for t in unique_tools:
        lines.append(f"- `{t}`")

    lines.extend([
        "",
        "**Steps**:",
    ])
    lines.extend(all_steps)

    if notes:
        lines.extend([
            "",
            "**Important notes**:",
            notes.strip(),
        ])

    lines.extend([
        "",
        "**Cleanup** (reverse order):",
    ])
    if cleanup_steps:
        lines.extend(cleanup_steps)
    else:
        lines.append("- No cleanup needed (read-only / settings restored)")

    lines.extend([
        "",
        f"**Expected outcome**: All {len(unique_tools)} tools exercised successfully.",
        "",
    ])

    return "\n".join(lines)


def generate_adversarial_task(task: dict, task_num: str) -> str:
    """Generate an adversarial task file."""
    title = task["title"]
    test_cases = task.get("test_cases", [])

    lines = [
        f"## Task {task_num}: {title}",
        "",
        f"**task_id**: {task_num}-adversarial",
        "",
        "**Objective**: Test error handling by intentionally sending bad inputs across multiple endpoints.",
        "",
        "**Instructions**: For each test case below, make the API call exactly as specified. Record the error response quality: does it clearly explain what went wrong? Does it suggest the correct values?",
        "",
        "**Steps**:",
    ]

    tools_referenced = []
    for i, tc in enumerate(test_cases, 1):
        tool = tc["tool"]
        desc = tc["description"]
        params = tc.get("params", {})
        expected = tc.get("expected", "error")
        params_str = ", ".join(f"`{k}={repr(v)}`" for k, v in params.items())
        lines.append(f"{i}. **{desc}**: Call `{tool}` with {params_str}")
        lines.append(f"   - Expected: {expected}")
        lines.append(f"   - Rate error message quality: clear/unclear/missing")
        tools_referenced.append(tool)

    unique_tools = list(dict.fromkeys(tools_referenced))
    lines.extend([
        "",
        f"**Tools to exercise** ({len(unique_tools)}):",
    ])
    for t in unique_tools:
        lines.append(f"- `{t}`")

    lines.extend([
        "",
        "**Expected outcome**: All calls should fail with clear error messages (except the status call). No resources should be created.",
        "",
        "**Cleanup**: None needed (all calls should fail).",
        "",
    ])

    return "\n".join(lines)


def generate_destructive_task(task: dict, task_num: str) -> str:
    """Generate the destructive opt-in task."""
    title = task["title"]
    notes = task.get("notes", "")
    endpoints = task.get("endpoints", [])

    tools_referenced = []
    lines = [
        f"## Task {task_num}: {title}",
        "",
        f"**task_id**: {task_num}-destructive",
        "",
        "**Objective**: Test destructive operations (logout, reboot, poweroff). Only run with INCLUDE_DESTRUCTIVE=1.",
        "",
        "**Steps**:",
    ]

    for i, ep in enumerate(endpoints, 1):
        tool = ep["tool"]
        notes_ep = ep.get("notes", "")
        mutation = ep.get("mutation", False)
        confirm_note = " with `confirm=True`" if mutation else ""
        lines.append(f"{i}. **Execute** `{tool}`{confirm_note} — {notes_ep}")
        tools_referenced.append(tool)

    unique_tools = list(dict.fromkeys(tools_referenced))
    lines.extend([
        "",
        f"**Tools to exercise** ({len(unique_tools)}):",
    ])
    for t in unique_tools:
        lines.append(f"- `{t}`")

    lines.extend([
        "",
        "**Important notes**:",
        notes.strip() if notes else "This will affect the controller.",
        "",
        "**Cleanup**: None (controller may be unreachable after poweroff).",
        "",
        "**Expected outcome**: Logout breaks session. Reboot makes controller temporarily unreachable. Poweroff stops the container.",
        "",
    ])

    return "\n".join(lines)


def main():
    """Generate all task files."""
    print("Loading task config...")
    tasks = load_config()
    print(f"  {len(tasks)} tasks defined")

    print("Loading tool names from generated/server.py...")
    all_tools = extract_all_tool_names()
    print(f"  {len(all_tools)} tools found")

    # Clean existing generated tasks
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    for f in TASKS_DIR.glob("*.md"):
        f.unlink()

    generated_count = 0
    all_tools_exercised: set[str] = set()

    for task in tasks:
        num = task["number"]
        task_num = f"{num:02d}"

        if task.get("adversarial_only"):
            content = generate_adversarial_task(task, task_num)
        elif task.get("destructive"):
            content = generate_destructive_task(task, task_num)
        else:
            content = generate_systematic_task(task, task_num)

        # Extract tools from content for coverage tracking
        for match in re.finditer(r"`(unifi_\w+)`", content):
            all_tools_exercised.add(match.group(1))

        # Build filename
        title_slug = task["title"].lower()
        for char in "— ,&()/'":
            title_slug = title_slug.replace(char, "-")
        title_slug = re.sub(r"-+", "-", title_slug).strip("-")[:60]

        output_path = TASKS_DIR / f"{task_num}-{title_slug}.md"
        output_path.write_text(content)
        generated_count += 1
        print(f"  Generated: {output_path.name}")

    # Coverage report
    print(f"\n{'='*60}")
    print(f"Generated {generated_count} task files in {TASKS_DIR}")
    print(f"{'='*60}")

    if all_tools:
        covered = all_tools_exercised & all_tools
        missing = sorted(all_tools - all_tools_exercised)
        extra = sorted(all_tools_exercised - all_tools)
        pct = len(covered) / len(all_tools) * 100

        print(f"\nTool Coverage: {len(covered)}/{len(all_tools)} ({pct:.1f}%)")

        if missing:
            print(f"\nMISSING ({len(missing)} tools not referenced in any task):")
            for t in missing:
                print(f"  - {t}")

        if extra:
            print(f"\nEXTRA ({len(extra)} referenced but not in server.py):")
            for t in extra:
                print(f"  - {t}")
    else:
        print(f"\nTools referenced in tasks: {len(all_tools_exercised)}")
        print("(Could not verify coverage — generated/server.py not found)")


if __name__ == "__main__":
    main()
