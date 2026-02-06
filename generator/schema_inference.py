"""Infer field types and metadata from sample JSON records."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FieldInfo:
    name: str
    python_type: str  # "str", "int", "float", "bool", "list", "dict"
    read_only: bool = False
    common: bool = False  # present in all sample records

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


def infer_schema(records: list[dict]) -> dict[str, FieldInfo]:
    """Infer schema from a list of sample JSON records.

    Returns a dict of field_name → FieldInfo, sorted by field name.
    """
    if not records:
        return {}

    # Collect all field names and their observed types
    field_types: dict[str, dict[str, int]] = {}
    field_counts: dict[str, int] = {}
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

    # Build FieldInfo for each field
    result: dict[str, FieldInfo] = {}
    for fname in sorted(field_types.keys()):
        type_counts = field_types[fname]
        # Pick the most common type
        best_type = max(type_counts, key=lambda t: type_counts[t])
        result[fname] = FieldInfo(
            name=fname,
            python_type=best_type,
            read_only=_is_readonly(fname),
            common=field_counts.get(fname, 0) == total,
        )

    return result
