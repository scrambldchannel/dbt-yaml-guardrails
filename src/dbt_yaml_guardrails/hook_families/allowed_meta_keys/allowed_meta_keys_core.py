"""Shared *-allowed-meta-keys validation (``specs/hook-families/allowed-meta-keys.md``)."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, MutableMapping
from pathlib import Path
from typing import Any

from dbt_yaml_guardrails.hook_families.allowed_keys.allowed_keys_core import (
    ViolationRow,
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


def violations_for_meta_keys(
    path_posix: str,
    resource_id: str,
    meta_keys: set[str],
    *,
    required: set[str],
    forbidden: set[str],
    allowed: frozenset[str] | None,
) -> list[ViolationRow]:
    """Validate *meta_keys* against *required*, *forbidden*, and optional allowlist.

    * *allowed* is ``None`` — only *required* and *forbidden* apply (no unknown-key rule).
    * *allowed* is a ``frozenset`` — allowlist mode: effective allow = *allowed* ∪ *required*;
      *forbidden* still wins for keys present on *meta*.
    """
    rows: list[ViolationRow] = []
    for req in sorted(required):
        if req not in meta_keys:
            detail = f"missing required meta key '{req}'"
            rows.append(((path_posix, resource_id, req, 0), detail))

    if allowed is None:
        for key in sorted(meta_keys):
            if key in forbidden:
                detail = f"forbidden meta key '{key}'"
                rows.append(((path_posix, resource_id, key, 1), detail))
    else:
        effective = set(allowed) | required
        for key in sorted(meta_keys):
            if key in forbidden:
                detail = f"forbidden meta key '{key}'"
                rows.append(((path_posix, resource_id, key, 1), detail))
            elif key not in effective:
                detail = f"meta key '{key}' not allowed"
                rows.append(((path_posix, resource_id, key, 2), detail))

    return rows


def meta_keys_from_resource_entry(
    path: Path,
    resource_kind: str,
    resource_name: str,
    entry: Mapping[str, Any],
) -> ParseError | set[str]:
    """Return top-level keys on ``config.meta`` for a resource entry, or :class:`ParseError`.

    *resource_kind* is the singular label in messages (e.g. ``\"model\"``, ``\"seed\"``).
    """
    if "config" not in entry:
        return set()
    cfg = entry["config"]
    if cfg is None:
        return ParseError(
            path,
            f"{resource_kind} '{resource_name}': config must be a mapping, not null",
        )
    if not isinstance(cfg, MutableMapping):
        return ParseError(
            path,
            f"{resource_kind} '{resource_name}': config must be a mapping, got {type(cfg).__name__}",
        )
    if "meta" not in cfg:
        return set()
    raw = cfg["meta"]
    if raw is None:
        return set()
    if not isinstance(raw, MutableMapping):
        return ParseError(
            path,
            f"{resource_kind} '{resource_name}': config.meta must be a mapping, got {type(raw).__name__}",
        )
    return set(raw.keys())


def collect_violation_rows_for_resource_meta_paths(
    files: list[Path],
    required: set[str],
    forbidden: set[str],
    allowed: frozenset[str] | None,
    *,
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
    """Walk *files*, extract resource entries, validate ``config.meta`` keys per entry."""
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
        for name, entry in iter_entries(inner):
            mk = meta_keys_from_resource_entry(path, resource_kind, name, entry)
            if isinstance(mk, ParseError):
                rows.append(violation_row_parse_error(path.as_posix(), mk.message))
                continue
            rows.extend(
                violations_for_meta_keys(
                    path.as_posix(),
                    name,
                    mk,
                    required=required,
                    forbidden=forbidden,
                    allowed=allowed,
                )
            )
    return rows


def run_allowed_meta_keys_cli(
    files: list[Path],
    required_csv: str,
    forbidden_csv: str,
    allowed_option: str | None,
    *,
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
    """Parse CLI flags, collect violations, emit; return ``0`` or ``1``."""
    required = parse_csv_keys(required_csv)
    forbidden = parse_csv_keys(forbidden_csv)
    if allowed_option is None:
        allowed: frozenset[str] | None = None
    else:
        allowed = frozenset(parse_csv_keys(allowed_option))

    if allowed is None and not required and not forbidden:
        return 0

    if not files:
        return 0

    rows = collect_violation_rows_for_resource_meta_paths(
        files,
        required,
        forbidden,
        allowed,
        resource_kind=resource_kind,
        extract_by_name=extract_by_name,
        iter_entries=iter_entries,
    )
    return finalize_violation_rows(
        rows,
        resource_label=resource_kind,
        emit=emit,
    )
