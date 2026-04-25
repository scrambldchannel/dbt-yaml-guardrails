"""Shared *-allowed-keys validation (``specs/hook-families/allowed-keys.md`` § Pattern, ``yaml-handling.md`` § Errors)."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, MutableMapping, Sequence
from pathlib import Path
from typing import Any, TypeAlias

from dbt_yaml_guardrails.yaml_handling import (
    ParseError,
    ParseSkip,
    ParseSuccess,
    load_dbt_project_yaml,
    load_property_yaml,
)

# Sort tuple: path, resource_id, primary (key or parse message), kind —
# 0=missing, 1=forbidden, 2=disallowed, 3=parse/shape error at file level.
SortKey: TypeAlias = tuple[str, str, str, int]
ViolationRow: TypeAlias = tuple[SortKey, str]


def config_mapping_from_resource_entry(
    path: Path,
    resource_kind: str,
    resource_name: str,
    entry: Mapping[str, Any],
) -> ParseError | dict[str, Any]:
    """Return the ``config`` mapping for one resource entry, or a parse error.

    Missing ``config`` yields an empty dict. ``config: null`` or a non-mapping
    ``config`` value is a shape error (``specs/hook-families/allowed-config-keys.md``
    § Pattern).

    Args:
        path: Source file (for errors).
        resource_kind: Singular label (e.g. ``\"model\"``).
        resource_name: Resource ``name`` field.
        entry: Full resource mapping from YAML.

    Returns:
        A plain dict of ``config`` keys and values, or :class:`ParseError`.
    """
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
    return dict(cfg)


def _nested_config_violations(
    path: Path,
    path_posix: str,
    entries: Iterable[tuple[str, Mapping[str, Any]]],
    *,
    resource_label: str,
    config_allowed: frozenset[str],
    config_legacy_key_messages: Mapping[str, str] | None,
) -> list[ViolationRow]:
    """Collect violation rows for direct keys under each entry's ``config:`` mapping.

    Violations use a ``config: <detail>`` prefix so they are visually distinct
    from top-level key violations on the same hook run
    (``specs/hook-families/allowed-keys.md`` § **Nested keys (`config`) and
    `--check-nested`**, ``yaml-handling.md`` § Errors).

    Args:
        path: Source file (for shape error construction).
        path_posix: POSIX path string (for sort keys / messages).
        entries: ``(resource_id, entry_mapping)`` pairs from the top-level iteration.
        resource_label: Singular resource noun for shape-error messages.
        config_allowed: Allowlisted keys under ``config:``.
        config_legacy_key_messages: Optional legacy-key detail map (same set as
            ``*-allowed-config-keys`` for this resource type).

    Returns:
        Unsorted violation rows.
    """
    legacy = config_legacy_key_messages or {}
    rows: list[ViolationRow] = []
    for resource_id, entry in entries:
        cfg = config_mapping_from_resource_entry(
            path, resource_label, resource_id, entry
        )
        if isinstance(cfg, ParseError):
            rows.append(violation_row_parse_error(path_posix, cfg.message))
            continue
        for key in sorted(cfg.keys()):
            if key in config_allowed:
                continue
            sub_detail = legacy.get(key) or f"disallowed key '{key}'"
            rows.append(((path_posix, resource_id, key, 2), f"config: {sub_detail}"))
    return rows


def parse_csv_keys(raw: str) -> set[str]:
    """Split a comma-separated key list from CLI flags.

    Args:
        raw: String from ``--required`` / ``--forbidden`` / similar (comma-separated).

    Returns:
        Non-empty key strings, whitespace-stripped, with empty segments removed.
    """
    return {part.strip() for part in raw.split(",") if part.strip()}


def violation_row_parse_error(path_posix: str, message: str) -> ViolationRow:
    """Build one sortable violation row for a file-level parse or shape error.

    Args:
        path_posix: File path (POSIX) for stable ordering.
        message: Error text shown on stderr.

    Returns:
        A :data:`ViolationRow` with empty resource id and kind ``3`` (parse).
    """
    return ((path_posix, "", message, 3), message)


def violations_for_entries(
    path_posix: str,
    entries: Iterable[tuple[str, Mapping[str, Any]]],
    *,
    allowed: frozenset[str],
    required: set[str],
    forbidden: set[str],
    legacy_key_messages: Mapping[str, str] | None = None,
) -> list[ViolationRow]:
    """Collect violation rows for top-level keys on each resource entry.

    Args:
        path_posix: File path (POSIX) for this batch of entries.
        entries: ``(resource_id, mapping)`` pairs (e.g. model name and model dict).
        allowed: Keys permitted on each entry (family allowlist from
            ``resource_keys``).
        required: Keys that must appear on every entry.
        forbidden: Keys that must not appear (deny wins over allowlist).
        legacy_key_messages: Optional map from legacy key to stderr detail
            (``specs/resource-keys.md`` § Legacy / deprecated).

    Returns:
        Unsorted :data:`ViolationRow` list; use :func:`finalize_violation_rows` to
        sort and print.
    """
    legacy = legacy_key_messages or {}
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
                detail = legacy.get(key) or f"disallowed key '{key}'"
                rows.append(((path_posix, resource_id, key, 2), detail))
    return rows


def sort_violation_rows(rows: list[ViolationRow]) -> None:
    """Sort *rows* in place by sort key (``yaml-handling.md`` § Errors).

    Args:
        rows: Violation rows produced by :func:`violations_for_entries` or
            :func:`collect_violation_rows_for_property_paths`.
    """
    rows.sort(key=lambda item: item[0])


def format_violation_line(
    sort_key: SortKey,
    detail: str,
    *,
    resource_label: str,
) -> str:
    """Format one stderr line for a single violation.

    Args:
        sort_key: Tuple carrying path, resource id, key/message, and kind.
        detail: Human-readable violation text.
        resource_label: Singular resource noun (e.g. ``\"model\"``, ``\"seed\"``).

    Returns:
        Line suitable for printing (no trailing newline).
    """
    fspath, resource_id, _, _ = sort_key
    if resource_id:
        return f"{fspath}: {resource_label} '{resource_id}': {detail}"
    if resource_label == "project":
        return f"{fspath}: project: {detail}"
    return f"{fspath}: {detail}"


def print_violation_rows(
    rows: Sequence[ViolationRow],
    *,
    resource_label: str,
    emit: Callable[[str], None],
) -> None:
    """Print each violation using *emit* (e.g. Typer to stderr).

    Args:
        rows: Sorted rows from :func:`sort_violation_rows`.
        resource_label: Singular resource noun for lines that include a resource id.
        emit: Callable that prints one line (typically ``typer.echo(..., err=True)``).
    """
    for sort_key, detail in rows:
        emit(format_violation_line(sort_key, detail, resource_label=resource_label))


def message_name_in_required(*, resource_plural: str) -> str:
    """Message for exit code 2 when ``name`` appears in ``--required``.

    Args:
        resource_plural: Plural resource noun for the error text (e.g. ``\"models\"``).

    Returns:
        Single-line message suitable for stderr.
    """
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
    legacy_key_messages: Mapping[str, str] | None = None,
    extract_by_name: Callable[
        [ParseSuccess],
        ParseError | Mapping[str, Mapping[str, Any]] | None,
    ],
    iter_entries: Callable[
        [Mapping[str, Mapping[str, Any]]],
        Iterable[tuple[str, Mapping[str, Any]]],
    ],
    check_nested: bool = True,
    config_allowed: frozenset[str] | None = None,
    config_legacy_key_messages: Mapping[str, str] | None = None,
    resource_label: str = "",
) -> list[ViolationRow]:
    """Walk *files*, load YAML, and validate top-level keys on each resource entry.

    When *check_nested* is ``True`` and *config_allowed* is provided, also validates
    direct keys under each entry's ``config:`` mapping using the same allowlists as
    ``*-allowed-config-keys`` (``specs/hook-families/allowed-keys.md`` § **Nested
    keys (`config`) and `--check-nested`**).

    Args:
        files: Property YAML paths from the CLI.
        required: Keys that must appear on every entry.
        forbidden: Keys that must not appear.
        allowed: Fixed allowlist for the hook family (from ``resource_keys``).
        legacy_key_messages: Optional legacy-key detail strings.
        extract_by_name: From a :class:`~dbt_yaml_guardrails.yaml_handling.ParseSuccess`,
            return ``None`` if the file has no target section (skip),
            :class:`~dbt_yaml_guardrails.yaml_handling.ParseError` for shape errors,
            or a ``name -> entry`` map on success.
        iter_entries: Stable iteration over that map (e.g. :func:`~dbt_yaml_guardrails.yaml_handling.iter_model_entries`).
        check_nested: When ``True`` (default) and *config_allowed* is set, also check
            direct keys under each entry's ``config:`` mapping.
        config_allowed: Allowlisted keys under ``config:`` (from ``resource_config_keys``).
            Required for nested checking; pass ``None`` to disable.
        config_legacy_key_messages: Optional legacy-key detail map for ``config`` keys.
        resource_label: Singular resource noun (e.g. ``\"model\"``); used in ``config``
            shape-error messages when nested checking is active.

    Returns:
        Unsorted violation rows.
    """
    rows: list[ViolationRow] = []
    run_nested = check_nested and config_allowed is not None
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
                legacy_key_messages=legacy_key_messages,
            )
        )
        if run_nested:
            rows.extend(
                _nested_config_violations(
                    path,
                    path.as_posix(),
                    iter_entries(inner),
                    resource_label=resource_label,
                    config_allowed=config_allowed,  # type: ignore[arg-type]
                    config_legacy_key_messages=config_legacy_key_messages,
                )
            )
    return rows


def collect_violation_rows_for_dbt_project_paths(
    files: list[Path],
    required: set[str],
    forbidden: set[str],
    allowed: frozenset[str],
    *,
    legacy_key_messages: Mapping[str, str] | None = None,
) -> list[ViolationRow]:
    """Walk *files* as ``dbt_project.yml`` roots and validate top-level keys (spec §8).

    Each file is one logical project; stderr uses the ``path: project: …`` form
    (``format_violation_line`` with ``resource_label=project`` and empty
    *resource_id* in the sort key).
    """
    rows: list[ViolationRow] = []
    for path in files:
        path = path.expanduser()
        loaded = load_dbt_project_yaml(path)
        if isinstance(loaded, ParseSkip):
            continue
        if isinstance(loaded, ParseError):
            rows.append(violation_row_parse_error(path.as_posix(), loaded.message))
            continue
        rows.extend(
            violations_for_entries(
                path.as_posix(),
                [("", dict(loaded.root))],
                allowed=allowed,
                required=required,
                forbidden=forbidden,
                legacy_key_messages=legacy_key_messages,
            )
        )
    return rows


def finalize_violation_rows(
    rows: list[ViolationRow],
    *,
    resource_label: str,
    emit: Callable[[str], None],
) -> int:
    """Sort, print violations, and return an exit code.

    Args:
        rows: Violation rows for the run (may be empty).
        resource_label: Singular resource noun for formatting.
        emit: Line sink (typically Typer stderr).

    Returns:
        ``0`` if *rows* is empty, else ``1``.
    """
    if not rows:
        return 0
    sort_violation_rows(rows)
    print_violation_rows(rows, resource_label=resource_label, emit=emit)
    return 1
