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
    """Validate key names under ``config.meta`` for one resource.

    If ``allowed`` is ``None``, only *required* and *forbidden* apply (unknown
    keys are not reported). If ``allowed`` is set, allowlist mode applies:
    effective allow is ``allowed | required``, and *forbidden* still wins for
    keys present on *meta*.

    Args:
        path_posix: File path (POSIX) for stable ordering.
        resource_id: Resource name (e.g. model name).
        meta_keys: Keys present on ``config.meta`` (empty if ``meta`` absent).
        required: Meta keys that must be present.
        forbidden: Meta keys that must not be present.
        allowed: If ``None``, no unknown-key rule; if set, enable allowlist mode.

    Returns:
        Unsorted violation rows for
        :func:`dbt_yaml_guardrails.hook_families.allowed_keys.allowed_keys_core.finalize_violation_rows`.
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
    """Return the set of keys on ``config.meta`` for one resource entry.

    Missing ``config`` or ``meta`` yields an empty set. Invalid shapes return
    :class:`~dbt_yaml_guardrails.yaml_handling.ParseError`.

    Args:
        path: Source file (for error messages).
        resource_kind: Singular label in messages (e.g. ``\"model\"``, ``\"seed\"``).
        resource_name: Resource ``name`` field.
        entry: Full resource mapping from YAML.

    Returns:
        Key names under ``meta``, or :class:`~dbt_yaml_guardrails.yaml_handling.ParseError`.
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
    """Walk *files* and validate ``config.meta`` keys for each entry of *resource_kind*.

    Args:
        files: Property YAML paths from the CLI.
        required: Meta keys that must be present.
        forbidden: Meta keys that must not be present.
        allowed: Optional allowlist (``None`` disables unknown-key enforcement).
        resource_kind: Singular noun for messages and stderr (e.g. ``\"model\"``).
        extract_by_name: Parse success to ``by_name`` map, skip, or parse error.
        iter_entries: Stable iteration over resource entries.

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
    """Run a ``*-allowed-meta-keys`` hook: parse flags, validate, print.

    Args:
        files: Positional YAML paths.
        required_csv: ``--required`` value (comma-separated).
        forbidden_csv: ``--forbidden`` value (comma-separated).
        allowed_option: ``--allowed`` if passed, else ``None`` (absent vs empty
            string follows Typer; see ``specs/hook-families/allowed-meta-keys.md``).
        resource_kind: Singular resource label (e.g. ``\"seed\"``).
        extract_by_name: Same contract as :func:`collect_violation_rows_for_resource_meta_paths`.
        iter_entries: Same contract as :func:`collect_violation_rows_for_resource_meta_paths`.
        emit: Line sink for violations (typically ``typer.echo(..., err=True)``).

    Returns:
        ``0`` on success or no-op (no policy, or no files), ``1`` if violations
        were printed.
    """
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
