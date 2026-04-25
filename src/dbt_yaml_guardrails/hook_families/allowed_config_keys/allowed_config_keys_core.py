"""Shared *-allowed-config-keys validation (``specs/hook-families/allowed-config-keys.md``)."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from pathlib import Path
from typing import Any

from dbt_yaml_guardrails.hook_families.allowed_keys.allowed_keys_core import (
    ViolationRow,
    config_mapping_from_resource_entry,
    finalize_violation_rows,
    parse_csv_keys,
    violation_row_parse_error,
)
from dbt_yaml_guardrails.yaml_handling import (
    ParseError,
    ParseSkip,
    ParseSuccess,
    load_property_yaml,
)


def violations_for_config_keys(
    path_posix: str,
    entries: Iterable[tuple[str, Mapping[str, Any]]],
    *,
    allowed: frozenset[str],
    required: set[str],
    forbidden: set[str],
    legacy_key_messages: Mapping[str, str] | None = None,
) -> list[ViolationRow]:
    """Collect violation rows for top-level keys inside each resource's ``config`` mapping."""
    legacy = legacy_key_messages or {}
    rows: list[ViolationRow] = []
    for resource_id, config_block in entries:
        keys = set(config_block.keys())
        for req in sorted(required):
            if req not in keys:
                detail = f"missing required config key '{req}'"
                rows.append(((path_posix, resource_id, req, 0), detail))
        for key in sorted(keys):
            if key in forbidden:
                detail = f"forbidden config key '{key}'"
                rows.append(((path_posix, resource_id, key, 1), detail))
            elif key not in allowed:
                detail = legacy.get(key) or f"disallowed config key '{key}'"
                rows.append(((path_posix, resource_id, key, 2), detail))
    return rows


def collect_violation_rows_for_resource_config_paths(
    files: list[Path],
    required: set[str],
    forbidden: set[str],
    allowed: frozenset[str],
    *,
    legacy_key_messages: Mapping[str, str] | None,
    resource_kind: str,
    extract_by_name: Callable[
        [ParseSuccess],
        ParseError | Mapping[str, Mapping[str, Any]] | None,
    ],
    iter_entries: Callable[
        [Mapping[str, Mapping[str, Any]]],
        Iterable[tuple[str, Mapping[str, Any]]],
    ],
) -> list[ViolationRow]:
    """Walk *files* and validate keys under ``config`` for each resource entry."""
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
        config_entries: list[tuple[str, Mapping[str, Any]]] = []
        for name, entry in iter_entries(inner):
            cfg = config_mapping_from_resource_entry(path, resource_kind, name, entry)
            if isinstance(cfg, ParseError):
                rows.append(violation_row_parse_error(path.as_posix(), cfg.message))
                continue
            config_entries.append((name, cfg))
        rows.extend(
            violations_for_config_keys(
                path.as_posix(),
                config_entries,
                allowed=allowed,
                required=required,
                forbidden=forbidden,
                legacy_key_messages=legacy_key_messages,
            )
        )
    return rows


def run_allowed_config_keys_cli(
    files: list[Path],
    required_csv: str,
    forbidden_csv: str,
    *,
    allowed: frozenset[str],
    legacy_key_messages: Mapping[str, str] | None,
    resource_kind: str,
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
    """Run a ``*-allowed-config-keys`` hook: parse flags, validate, print."""
    required = parse_csv_keys(required_csv)
    forbidden = parse_csv_keys(forbidden_csv)
    if not files:
        return 0
    rows = collect_violation_rows_for_resource_config_paths(
        files,
        required,
        forbidden,
        allowed,
        legacy_key_messages=legacy_key_messages,
        resource_kind=resource_kind,
        extract_by_name=extract_by_name,
        iter_entries=iter_entries,
    )
    return finalize_violation_rows(
        rows,
        resource_label=resource_kind,
        emit=emit,
    )
