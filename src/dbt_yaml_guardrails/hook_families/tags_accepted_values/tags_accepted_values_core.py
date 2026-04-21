"""Shared *-tags-accepted-values validation (``specs/hook-families/tags-accepted-values.md``)."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, MutableMapping, Sequence
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


def violations_for_config_tags_leaf(
    path_posix: str,
    resource_id: str,
    leaf: Any,
    allowed: frozenset[str],
) -> list[ViolationRow]:
    """Validate ``config.tags`` value: string or sequence of strings, each ∈ *allowed*."""
    rows: list[ViolationRow] = []
    key = "config.tags"
    if isinstance(leaf, str):
        val = leaf.strip()
        if val not in allowed:
            detail = f"config.tags: value {val!r} is not an allowed value"
            rows.append(((path_posix, resource_id, key, 2), detail))
        return rows

    if isinstance(leaf, Sequence) and not isinstance(leaf, (str, bytes)):
        for i, item in enumerate(leaf):
            if not isinstance(item, str):
                detail = (
                    f"config.tags: sequence element at index {i} must be a "
                    f"string, got {type(item).__name__}"
                )
                rows.append(((path_posix, resource_id, key, 1), detail))
                continue
            val = item.strip()
            if val not in allowed:
                detail = (
                    f"config.tags: value {val!r} at index {i} is not an allowed value"
                )
                rows.append(((path_posix, resource_id, key, 2), detail))
        return rows

    detail = (
        f"config.tags must be a string or a sequence of strings, "
        f"got {type(leaf).__name__}"
    )
    rows.append(((path_posix, resource_id, key, 1), detail))
    return rows


def _config_mapping_from_entry(
    path: Path,
    resource_kind: str,
    resource_name: str,
    entry: Mapping[str, Any],
) -> ParseError | None | dict[str, Any]:
    """Return ``config`` as a plain dict, ``None`` if absent, or :class:`ParseError`."""
    if "config" not in entry:
        return None
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
    return dict(cfg)


def violations_for_entry_config_tags(
    path_posix: str,
    resource_kind: str,
    resource_name: str,
    entry: Mapping[str, Any],
    allowed: frozenset[str],
) -> list[ViolationRow]:
    """Validate ``config.tags`` on one resource entry when the key is present."""
    path = Path(path_posix)
    cfg = _config_mapping_from_entry(path, resource_kind, resource_name, entry)
    if cfg is None:
        return []
    if isinstance(cfg, ParseError):
        return [violation_row_parse_error(path_posix, cfg.message)]

    if "tags" not in cfg:
        return []

    leaf = cfg["tags"]
    return violations_for_config_tags_leaf(path_posix, resource_name, leaf, allowed)


def collect_violation_rows_for_tags_accepted_values(
    files: list[Path],
    allowed: frozenset[str],
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
    """Walk *files* and validate ``config.tags`` allowlists per entry."""
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
            rows.extend(
                violations_for_entry_config_tags(
                    path.as_posix(),
                    resource_kind,
                    name,
                    entry,
                    allowed,
                )
            )
    return rows


def run_tags_accepted_values_cli(
    files: list[Path],
    values_csv: str,
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
    allowed_set = parse_csv_keys(values_csv)
    if not allowed_set:
        emit("error: --values must list at least one allowed value")
        return 2

    allowed = frozenset(allowed_set)

    if not files:
        return 0

    rows = collect_violation_rows_for_tags_accepted_values(
        files,
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
