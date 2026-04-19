"""Shared *-meta-accepted-values validation (``specs/hook-families/meta-accepted-values.md``)."""

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


def parse_key_path(raw: str) -> list[str] | None:
    """Split a dot path under ``meta`` into segments; ``None`` if invalid."""
    s = raw.strip()
    if not s:
        return None
    parts = s.split(".")
    out: list[str] = []
    for p in parts:
        t = p.strip()
        if not t:
            return None
        out.append(t)
    return out


def _meta_mapping_from_entry(
    path: Path,
    resource_kind: str,
    resource_name: str,
    entry: Mapping[str, Any],
) -> ParseError | dict[str, Any]:
    """Return a plain dict for ``config.meta``, or ``{}`` if absent; :class:`ParseError` on bad shape."""
    if "config" not in entry:
        return {}
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
        return {}
    raw = cfg["meta"]
    if raw is None:
        return {}
    if not isinstance(raw, MutableMapping):
        return ParseError(
            path,
            f"{resource_kind} '{resource_name}': config.meta must be a mapping, got {type(raw).__name__}",
        )
    return dict(raw)


def violations_for_meta_accepted_value(
    path_posix: str,
    resource_id: str,
    meta: Mapping[str, Any],
    segments: list[str],
    *,
    optional: bool,
    allowed: frozenset[str],
) -> list[ViolationRow]:
    """Validate one dot path under ``meta`` for string leaf ∈ *allowed*."""
    rows: list[ViolationRow] = []
    key_path = ".".join(segments)
    cur: Any = meta

    for i, seg in enumerate(segments[:-1]):
        prefix = ".".join(segments[: i + 1])
        if not isinstance(cur, MutableMapping):
            detail = (
                f"meta path '{key_path}': expected mapping at '{prefix}', "
                f"got {type(cur).__name__}"
            )
            rows.append(((path_posix, resource_id, key_path, 1), detail))
            return rows
        if seg not in cur:
            if optional:
                return rows
            detail = f"missing required meta path '{key_path}'"
            rows.append(((path_posix, resource_id, key_path, 0), detail))
            return rows
        cur = cur[seg]

    last = segments[-1]
    if not isinstance(cur, MutableMapping):
        detail = (
            f"meta path '{key_path}': expected mapping before leaf '{last}', "
            f"got {type(cur).__name__}"
        )
        rows.append(((path_posix, resource_id, key_path, 1), detail))
        return rows
    if last not in cur:
        if optional:
            return rows
        detail = f"missing required meta path '{key_path}'"
        rows.append(((path_posix, resource_id, key_path, 0), detail))
        return rows

    leaf = cur[last]
    if not isinstance(leaf, str):
        detail = f"meta path '{key_path}' must be a string, got {type(leaf).__name__}"
        rows.append(((path_posix, resource_id, key_path, 1), detail))
        return rows

    val = leaf.strip()
    if val not in allowed:
        detail = f"meta path '{key_path}': value {val!r} is not an allowed value"
        rows.append(((path_posix, resource_id, key_path, 2), detail))
    return rows


def collect_violation_rows_for_meta_accepted_values(
    files: list[Path],
    segments: list[str],
    allowed: frozenset[str],
    *,
    optional: bool,
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
    """Walk *files* and validate ``config.meta`` path + allowed string values per entry."""
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
            meta = _meta_mapping_from_entry(path, resource_kind, name, entry)
            if isinstance(meta, ParseError):
                rows.append(violation_row_parse_error(path.as_posix(), meta.message))
                continue
            rows.extend(
                violations_for_meta_accepted_value(
                    path.as_posix(),
                    name,
                    meta,
                    segments,
                    optional=optional,
                    allowed=allowed,
                )
            )
    return rows


def run_meta_accepted_values_cli(
    files: list[Path],
    key_raw: str,
    values_csv: str,
    optional: bool,
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
    """Parse CLI flags, collect violations, emit; return ``0``, ``1``, or ``2``."""
    segments = parse_key_path(key_raw)
    if segments is None:
        emit("error: --key must be a non-empty dot path (e.g. domain or owner.name)")
        return 2

    allowed_set = parse_csv_keys(values_csv)
    if not allowed_set:
        emit("error: --values must list at least one allowed value")
        return 2

    allowed = frozenset(allowed_set)

    if not files:
        return 0

    rows = collect_violation_rows_for_meta_accepted_values(
        files,
        segments,
        allowed,
        optional=optional,
        resource_kind=resource_kind,
        extract_by_name=extract_by_name,
        iter_entries=iter_entries,
    )
    return finalize_violation_rows(
        rows,
        resource_label=resource_kind,
        emit=emit,
    )
