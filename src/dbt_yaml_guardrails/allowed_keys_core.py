"""Shared *-allowed-keys validation (``specs/hooks.md`` § Pattern, ``yaml-handling.md`` § Errors)."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any, TypeAlias

from dbt_yaml_guardrails.yaml_handling import (
    ParseError,
    ParseSkip,
    ParseSuccess,
    load_property_yaml,
)

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


def message_name_in_required(*, resource_plural: str) -> str:
    """CLI error when ``name`` is in ``--required`` (``--required`` is redundant for real resources)."""
    return (
        f"error: do not list 'name' in --required "
        f"(it is always present on real {resource_plural})"
    )


def collect_violation_rows_for_property_paths(
    files: list[Path],
    required: set[str],
    forbidden: set[str],
    allowed: frozenset[str],
    *,
    extract_by_name: Callable[
        [ParseSuccess],
        ParseError | Mapping[str, Mapping[str, Any]] | None,
    ],
    iter_entries: Callable[
        [Mapping[str, Mapping[str, Any]]],
        Iterable[tuple[str, Mapping[str, Any]]],
    ],
) -> list[ViolationRow]:
    """Walk *files* with :func:`load_property_yaml`, then validate keys per resource.

    *extract_by_name* returns ``None`` if the file has no hook target section (skip),
    :class:`ParseError` for shape errors, or ``by_name`` mapping on success.
    """
    rows: list[ViolationRow] = []
    for path in files:
        path = path.expanduser()
        loaded = load_property_yaml(path)
        if isinstance(loaded, ParseSkip):
            continue
        if isinstance(loaded, ParseError):
            rows.append(violation_row_parse_error(path.as_posix(), loaded.message))
            continue
        inner = extract_by_name(loaded)
        if inner is None:
            continue
        if isinstance(inner, ParseError):
            rows.append(violation_row_parse_error(path.as_posix(), inner.message))
            continue
        rows.extend(
            violations_for_entries(
                path.as_posix(),
                iter_entries(inner),
                allowed=allowed,
                required=required,
                forbidden=forbidden,
            )
        )
    return rows


def finalize_violation_rows(
    rows: list[ViolationRow],
    *,
    resource_label: str,
    emit: Callable[[str], None],
) -> int:
    """Return ``0`` if *rows* is empty; otherwise sort, print, return ``1``."""
    if not rows:
        return 0
    sort_violation_rows(rows)
    print_violation_rows(rows, resource_label=resource_label, emit=emit)
    return 1
