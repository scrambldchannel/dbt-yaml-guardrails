"""Shared *-allowed-keys validation (``specs/hooks.md`` § Pattern, ``yaml-handling.md`` § Errors)."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any, TypeAlias

# Sort tuple: path, resource_id, primary (key or parse message), kind —
# 0=missing, 1=forbidden, 2=disallowed, 3=parse/shape error at file level.
SortKey: TypeAlias = tuple[str, str, str, int]
ViolationRow: TypeAlias = tuple[SortKey, str]


def parse_csv_keys(raw: str) -> set[str]:
    """Split a comma-separated key list (whitespace trimmed, empty parts dropped)."""
    return {part.strip() for part in raw.split(",") if part.strip()}


def violation_row_parse_error(path_posix: str, message: str) -> ViolationRow:
    """One sortable row for YAML / extract failure on *path_posix*."""
    return ((path_posix, "", message, 3), message)


def violations_for_entries(
    path_posix: str,
    entries: Iterable[tuple[str, Mapping[str, Any]]],
    *,
    allowed: frozenset[str],
    required: set[str],
    forbidden: set[str],
) -> list[ViolationRow]:
    """Collect violation rows for each resource entry under *path_posix*.

    *entries* yields ``(resource_id, mapping)`` (e.g. model name and model dict).
    """
    rows: list[ViolationRow] = []
    for resource_id, entry in entries:
        keys = set(entry.keys())
        for req in sorted(required):
            if req not in keys:
                detail = f"missing required key '{req}'"
                rows.append(((path_posix, resource_id, req, 0), detail))
        for key in sorted(keys):
            if key in forbidden:
                detail = f"forbidden key '{key}'"
                rows.append(((path_posix, resource_id, key, 1), detail))
            elif key not in allowed:
                detail = f"disallowed key '{key}'"
                rows.append(((path_posix, resource_id, key, 2), detail))
    return rows


def sort_violation_rows(rows: list[ViolationRow]) -> None:
    """Stable sort: path, resource id, key / message, kind (``yaml-handling.md`` § Errors)."""
    rows.sort(key=lambda item: item[0])


def format_violation_line(
    sort_key: SortKey,
    detail: str,
    *,
    resource_label: str,
) -> str:
    """Format one line for stderr (``resource_label`` e.g. ``\"model\"``, ``\"source\"``)."""
    fspath, resource_id, _, _ = sort_key
    if resource_id:
        return f"{fspath}: {resource_label} '{resource_id}': {detail}"
    return f"{fspath}: {detail}"


def print_violation_rows(
    rows: Sequence[ViolationRow],
    *,
    resource_label: str,
    emit: Callable[[str], None],
) -> None:
    """Emit each line with *emit* (e.g. ``lambda m: typer.echo(m, err=True)``)."""
    for sort_key, detail in rows:
        emit(format_violation_line(sort_key, detail, resource_label=resource_label))
