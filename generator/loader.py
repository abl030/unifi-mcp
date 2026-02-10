"""Load spec/ data (endpoint inventory, api-samples, field inventory) into structured data."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class RestEndpoint:
    name: str
    path: str
    methods: list[str]
    live_status: int | None = None
    sample_count: int | None = None
    note: str | None = None
    samples: list[dict] = field(default_factory=list)


@dataclass
class StatEndpoint:
    name: str
    path: str
    method: str
    live_status: int | None = None
    sample_count: int | None = None
    note: str | None = None
    samples: list[dict] = field(default_factory=list)


@dataclass
class CmdEndpoint:
    name: str
    path: str
    commands: list[str]
    live_status: int | None = None


@dataclass
class V2Endpoint:
    name: str
    path: str
    methods: list[str]
    live_status: int | None = None
    samples: list[dict] = field(default_factory=list)


@dataclass
class GlobalEndpoint:
    name: str
    method: str
    path: str
    auth: bool = True


@dataclass
class APIInventory:
    controller_version: str
    rest_endpoints: dict[str, RestEndpoint] = field(default_factory=dict)
    stat_endpoints: dict[str, StatEndpoint] = field(default_factory=dict)
    cmd_endpoints: dict[str, CmdEndpoint] = field(default_factory=dict)
    v2_endpoints: dict[str, V2Endpoint] = field(default_factory=dict)
    global_endpoints: dict[str, GlobalEndpoint] = field(default_factory=dict)
    field_inventory: dict[str, list[str]] = field(default_factory=dict)


def _load_sample(samples_dir: Path, prefix: str, name: str) -> list[dict]:
    """Load sample JSON for an endpoint, returning the data records."""
    sample_file = samples_dir / f"{prefix}_{name}.json"
    if not sample_file.exists():
        return []
    raw = json.loads(sample_file.read_text())
    # v1 API wraps in {"meta": ..., "data": [...]}
    if isinstance(raw, dict) and "data" in raw:
        data = raw["data"]
        return data if isinstance(data, list) else []
    # v2 API returns a bare list
    if isinstance(raw, list):
        return raw
    return []


def load_field_inventory(path: Path) -> dict[str, list[str]]:
    """Load field-inventory.json → dict mapping endpoint key to sorted field names.

    Keys are like "rest_networkconf", "stat_sta", "v2_clients_active".
    Values are lists of field names sorted alphabetically.
    """
    if not path.exists():
        return {}
    raw = json.loads(path.read_text())
    result: dict[str, list[str]] = {}
    for key, entry in raw.items():
        fields = sorted(entry.get("fields", {}).keys())
        if fields:
            result[key] = fields
    return result


def load_inventory(
    inventory_path: Path,
    samples_dir: Path,
    field_inventory_path: Path | None = None,
) -> APIInventory:
    """Parse endpoint-inventory.json and load matching samples."""
    raw = json.loads(inventory_path.read_text())

    inv = APIInventory(controller_version=raw.get("controller_version", "unknown"))

    # REST endpoints
    for name, ep in raw.get("rest_endpoints", {}).items():
        rest = RestEndpoint(
            name=name,
            path=ep["path"],
            methods=ep.get("methods", ["GET"]),
            live_status=ep.get("live_status"),
            sample_count=ep.get("sample_count"),
            note=ep.get("note"),
            samples=_load_sample(samples_dir, "rest", name),
        )
        inv.rest_endpoints[name] = rest

    # Stat endpoints
    for name, ep in raw.get("stat_endpoints", {}).items():
        stat = StatEndpoint(
            name=name,
            path=ep["path"],
            method=ep.get("method", "GET"),
            live_status=ep.get("live_status"),
            sample_count=ep.get("sample_count"),
            note=ep.get("note"),
            samples=_load_sample(samples_dir, "stat", name),
        )
        inv.stat_endpoints[name] = stat

    # Command endpoints
    for name, ep in raw.get("cmd_endpoints", {}).items():
        cmd = CmdEndpoint(
            name=name,
            path=ep["path"],
            commands=ep.get("commands", []),
            live_status=ep.get("live_status"),
        )
        inv.cmd_endpoints[name] = cmd

    # v2 endpoints
    for name, ep in raw.get("v2_endpoints", {}).items():
        v2 = V2Endpoint(
            name=name,
            path=ep["path"],
            methods=ep.get("methods", ["GET"]),
            live_status=ep.get("live_status"),
            samples=_load_sample(samples_dir, "v2", name),
        )
        inv.v2_endpoints[name] = v2

    # Global endpoints
    for name, ep in raw.get("global_endpoints", {}).items():
        glb = GlobalEndpoint(
            name=name,
            method=ep.get("method", "GET"),
            path=ep["path"],
            auth=ep.get("auth", True),
        )
        inv.global_endpoints[name] = glb

    # Field inventory (optional enrichment from production controllers)
    if field_inventory_path:
        inv.field_inventory = load_field_inventory(field_inventory_path)

    return inv
