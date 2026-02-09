"""Infer field types and metadata from sample JSON records."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FieldInfo:
    name: str
    python_type: str  # "str", "int", "float", "bool", "list", "dict"
    read_only: bool = False
    common: bool = False  # present in all sample records
    enum_values: list[str] = field(default_factory=list)  # observed string values (≤10 distinct)

    @property
    def annotation(self) -> str:
        """Python type annotation for use in function signatures."""
        return self.python_type


# Fields that are always read-only (set by the controller)
_READONLY_EXACT = frozenset({
    "_id", "site_id", "key",
})

_READONLY_PREFIXES = ("_", "attr_")
_READONLY_SUFFIXES = ("-r",)


def _is_readonly(field_name: str) -> bool:
    if field_name in _READONLY_EXACT:
        return True
    for prefix in _READONLY_PREFIXES:
        if field_name.startswith(prefix):
            return True
    for suffix in _READONLY_SUFFIXES:
        if field_name.endswith(suffix):
            return True
    return False


def _infer_type(value: object) -> str:
    """Infer Python type string from a JSON value. Check bool before int."""
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, list):
        return "list"
    if isinstance(value, dict):
        return "dict"
    return "str"


def _is_enum_candidate(field_name: str) -> bool:
    """Check if a field could be an enum (not an ID, name, or free-text)."""
    if field_name.endswith("_id"):
        return False
    if field_name in ("_id", "site_id", "name", "desc", "hostname", "ip",
                       "mac", "host_name", "domain_name", "x_password",
                       "x_passphrase", "login", "external_id", "fwd",
                       "fwd_port", "dst_port", "last_ip", "ip_subnet",
                       "service", "last_1x_identity"):
        return False
    if field_name.startswith("x_") or field_name.startswith("_"):
        return False
    # Skip fields that typically hold free-form or instance-specific data
    if any(s in field_name for s in ("_name", "_url", "_host", "_address",
                                      "_subnet", "_start", "_stop", "_port")):
        return False
    return True


def _looks_like_data_value(value: str) -> bool:
    """Reject values that look like instance-specific data, not enum constants."""
    # IP addresses
    if value.count(".") == 3 and all(p.isdigit() for p in value.split(".")):
        return True
    # IPv6 fragments
    if value.startswith("::"):
        return True
    # UUIDs
    if len(value) == 36 and value.count("-") == 4:
        return True
    # MAC addresses
    if len(value) == 17 and value.count(":") == 5:
        return True
    return False


_MAX_ENUM_VALUES = 10


def infer_schema(records: list[dict]) -> dict[str, FieldInfo]:
    """Infer schema from a list of sample JSON records.

    Returns a dict of field_name → FieldInfo, sorted by field name.
    """
    if not records:
        return {}

    # Collect all field names and their observed types
    field_types: dict[str, dict[str, int]] = {}
    field_counts: dict[str, int] = {}
    field_string_values: dict[str, set[str]] = {}
    total = len(records)

    for record in records:
        if not isinstance(record, dict):
            continue
        for key, value in record.items():
            if value is None:
                continue
            ptype = _infer_type(value)
            field_types.setdefault(key, {})
            field_types[key][ptype] = field_types[key].get(ptype, 0) + 1
            field_counts[key] = field_counts.get(key, 0) + 1
            # Track unique string values for enum inference
            if (isinstance(value, str) and value
                    and _is_enum_candidate(key)
                    and not _looks_like_data_value(value)):
                field_string_values.setdefault(key, set()).add(value)

    # Build FieldInfo for each field
    result: dict[str, FieldInfo] = {}
    for fname in sorted(field_types.keys()):
        type_counts = field_types[fname]
        # Pick the most common type
        best_type = max(type_counts, key=lambda t: type_counts[t])
        # Collect enum values for string fields with few distinct values
        # Skip if every observed value is unique (instance data, not enums)
        enum_vals: list[str] = []
        if best_type == "str" and fname in field_string_values:
            unique = field_string_values[fname]
            count = field_counts.get(fname, 0)
            if len(unique) <= _MAX_ENUM_VALUES and (count <= 1 or len(unique) < count):
                enum_vals = sorted(unique)
        result[fname] = FieldInfo(
            name=fname,
            python_type=best_type,
            read_only=_is_readonly(fname),
            common=field_counts.get(fname, 0) == total,
            enum_values=enum_vals,
        )

    return result
