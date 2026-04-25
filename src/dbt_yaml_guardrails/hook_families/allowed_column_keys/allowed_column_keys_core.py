"""Shared *-allowed-column-keys validation (``specs/hook-families/allowed-column-keys.md``)."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from pathlib import Path
from typing import Any

from dbt_yaml_guardrails.hook_families.allowed_keys.allowed_keys_core import (
    ViolationRow,
    finalize_violation_rows,
    message_name_in_required,
    parse_csv_keys,
    violation_row_parse_error,
)
from dbt_yaml_guardrails.yaml_handling import (
    ParseError,
    ParseSkip,
    ParseSuccess,
    load_property_yaml,
)


def violations_for_column_keys(
    path_posix: str,
    entries: Iterable[tuple[str, Mapping[str, Any]]],
    *,
    resource_label: str,
    allowed: frozenset[str],
    required: set[str],
    forbidden: set[str],
    legacy_key_messages: Mapping[str, str] | None = None,
) -> list[ViolationRow]:
    """Collect violation rows for direct keys on each column entry.

    Shape errors (``columns:`` not a list, column not a mapping, column missing
    ``name``) exit ``1`` with a precise message. If ``columns:`` is absent or
    an empty list the resource entry is skipped silently.

    Violation sort key uses ``column:{col_name}:{key}`` so column violations
    sort after top-level entry key violations and after ``config:`` violations
    within the same resource.

    Args:
        path_posix: POSIX path for sort keys and messages.
        entries: ``(resource_id, entry_mapping)`` pairs.
        resource_label: Singular resource noun for messages (e.g. ``"model"``).
        allowed: Allowlisted keys on each column entry.
        required: Keys that must appear on every column entry.
        forbidden: Keys that must not appear on any column entry.
        legacy_key_messages: Optional legacy-key detail map.

    Returns:
        Unsorted violation rows.
    """
    legacy = legacy_key_messages or {}
    rows: list[ViolationRow] = []
    for resource_id, entry in entries:
        if "columns" not in entry:
            continue
        raw_columns = entry["columns"]
        if not isinstance(raw_columns, list):
            msg = f"{resource_label} '{resource_id}': columns must be a list"
            rows.append(violation_row_parse_error(path_posix, msg))
            continue
        if not raw_columns:
            continue
        for i, col in enumerate(raw_columns):
            if col is None or not isinstance(col, Mapping):
                msg = f"{resource_label} '{resource_id}': column at index {i} must be a mapping"
                rows.append(violation_row_parse_error(path_posix, msg))
                continue
            name = col.get("name")
            if not name:
                msg = f"{resource_label} '{resource_id}': column at index {i} is missing 'name'"
                rows.append(violation_row_parse_error(path_posix, msg))
                continue
            col_name = str(name)
            keys = set(col.keys())
            for req in sorted(required):
                if req not in keys:
                    detail = f"missing required key '{req}'"
                    rows.append(
                        (
                            (path_posix, resource_id, f"column:{col_name}:{req}", 0),
                            f"column '{col_name}': {detail}",
                        )
                    )
            for key in sorted(keys):
                if key in forbidden:
                    detail = f"forbidden key '{key}'"
                    rows.append(
                        (
                            (path_posix, resource_id, f"column:{col_name}:{key}", 1),
                            f"column '{col_name}': {detail}",
                        )
                    )
                elif key not in allowed:
                    detail = legacy.get(key) or f"disallowed key '{key}'"
                    rows.append(
                        (
                            (path_posix, resource_id, f"column:{col_name}:{key}", 2),
                            f"column '{col_name}': {detail}",
                        )
                    )
    return rows


def collect_violation_rows_for_column_paths(
    files: list[Path],
    required: set[str],
    forbidden: set[str],
    allowed: frozenset[str],
    *,
    legacy_key_messages: Mapping[str, str] | None,
    resource_label: str,
    extract_by_name: Callable[
        [ParseSuccess],
        ParseError | Mapping[str, Mapping[str, Any]] | None,
    ],
    iter_entries: Callable[
        [Mapping[str, Mapping[str, Any]]],
        Iterable[tuple[str, Mapping[str, Any]]],
    ],
) -> list[ViolationRow]:
    """Walk *files* and validate keys on each column entry for the resource type.

    Args:
        files: Property YAML paths from the CLI.
        required: Keys that must appear on every column entry.
        forbidden: Keys that must not appear on any column entry.
        allowed: Fixed allowlist for column keys (from ``resource_keys``).
        legacy_key_messages: Optional legacy-key detail map.
        resource_label: Singular resource noun for messages and sorting.
        extract_by_name: Returns ``None`` (skip), :class:`ParseError`, or
            a ``name -> entry`` map from a :class:`ParseSuccess`.
        iter_entries: Stable iteration over that map.

    Returns:
        Unsorted violation rows.
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
            violations_for_column_keys(
                path.as_posix(),
                iter_entries(inner),
                resource_label=resource_label,
                allowed=allowed,
                required=required,
                forbidden=forbidden,
                legacy_key_messages=legacy_key_messages,
            )
        )
    return rows


def run_allowed_column_keys_cli(
    files: list[Path],
    required_csv: str,
    forbidden_csv: str,
    *,
    allowed: frozenset[str],
    legacy_key_messages: Mapping[str, str] | None,
    resource_label: str,
    resource_plural: str,
    extract_by_name: Callable[
        [ParseSuccess],
        ParseError | Mapping[str, Mapping[str, Any]] | None,
    ],
    iter_entries: Callable[
        [Mapping[str, Mapping[str, Any]]],
        Iterable[tuple[str, Mapping[str, Any]]],
    ],
    emit: Callable[[str], None],
) -> int:
    """Run a ``*-allowed-column-keys`` hook: parse flags, validate, print.

    Returns exit code ``0`` (pass), ``1`` (violation / shape error), or
    ``2`` (invalid CLI usage — ``name`` in ``--required``).
    """
    required = parse_csv_keys(required_csv)
    forbidden = parse_csv_keys(forbidden_csv)
    if "name" in required:
        emit(message_name_in_required(resource_plural=f"{resource_plural} columns"))
        return 2
    if not files:
        return 0
    rows = collect_violation_rows_for_column_paths(
        files,
        required,
        forbidden,
        allowed,
        legacy_key_messages=legacy_key_messages,
        resource_label=resource_label,
        extract_by_name=extract_by_name,
        iter_entries=iter_entries,
    )
    return finalize_violation_rows(rows, resource_label=resource_label, emit=emit)
