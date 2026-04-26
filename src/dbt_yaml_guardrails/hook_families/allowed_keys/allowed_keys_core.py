"""Shared *-allowed-keys validation (``specs/hook-families/allowed-keys.md`` § Pattern, ``yaml-handling.md`` § Errors)."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, MutableMapping, Sequence
from pathlib import Path
from typing import Any, TypeAlias

from dbt_yaml_guardrails.hook_families.fix_legacy_yaml.fix_legacy_integration import (
    apply_fix_legacy_yaml,
)
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


def _nested_column_violations(
    path_posix: str,
    entries: Iterable[tuple[str, Mapping[str, Any]]],
    *,
    resource_label: str,
    column_allowed: frozenset[str],
    column_legacy_key_messages: Mapping[str, str] | None,
) -> list[ViolationRow]:
    """Collect violation rows for direct keys on each column entry.

    Shape errors (``columns:`` not a list, column not a mapping, column missing
    ``name``) are treated as parse/shape errors (kind ``3``) and exit code ``1``,
    consistent with ``yaml-handling.md`` § Errors and
    ``specs/hook-families/allowed-keys.md`` § **Nested keys (`columns:`) and
    `--check-columns`**.

    Args:
        path_posix: POSIX path string (for sort keys / messages).
        entries: ``(resource_id, entry_mapping)`` pairs from the top-level iteration.
        resource_label: Singular resource noun for shape-error messages.
        column_allowed: Allowlisted keys on each column entry.
        column_legacy_key_messages: Optional legacy-key detail map for column keys.

    Returns:
        Unsorted violation rows.
    """
    legacy = column_legacy_key_messages or {}
    rows: list[ViolationRow] = []
    for resource_id, entry in entries:
        if "columns" not in entry:
            continue
        raw_columns = entry["columns"]
        if not isinstance(raw_columns, list):
            msg = f"{resource_label} '{resource_id}': columns must be a list"
            rows.append(violation_row_parse_error(path_posix, msg))
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
            for key in sorted(col.keys()):
                if key in column_allowed:
                    continue
                sub_detail = legacy.get(key) or f"disallowed key '{key}'"
                rows.append(
                    (
                        (path_posix, resource_id, f"{col_name}:{key}", 2),
                        f"column '{col_name}': {sub_detail}",
                    )
                )
    return rows


def _nested_source_table_violations(
    path: Path,
    path_posix: str,
    entries: Iterable[tuple[str, Mapping[str, Any]]],
    *,
    table_allowed: frozenset[str],
    table_legacy_key_messages: Mapping[str, str] | None,
    check_config: bool,
    config_allowed: frozenset[str] | None,
    config_legacy_key_messages: Mapping[str, str] | None,
    check_source_table_columns: bool,
    column_allowed: frozenset[str] | None,
    column_legacy_key_messages: Mapping[str, str] | None,
) -> list[ViolationRow]:
    """Validate each ``tables:`` row and optional nested ``columns:`` (source hook only)."""
    t_legacy = table_legacy_key_messages or {}
    c_leg = config_legacy_key_messages or {}
    col_leg = column_legacy_key_messages or {}
    rows: list[ViolationRow] = []
    for source_id, source_entry in entries:
        if "tables" not in source_entry:
            continue
        raw_tables = source_entry["tables"]
        if not isinstance(raw_tables, list):
            rows.append(
                violation_row_parse_error(
                    path_posix, f"source '{source_id}': tables must be a list"
                )
            )
            continue
        if not raw_tables:
            continue
        for j, table in enumerate(raw_tables):
            if table is None or not isinstance(table, MutableMapping):
                rows.append(
                    violation_row_parse_error(
                        path_posix,
                        f"source '{source_id}': table at index {j} must be a mapping",
                    )
                )
                continue
            name = table.get("name")
            if not name:
                rows.append(
                    violation_row_parse_error(
                        path_posix,
                        f"source '{source_id}': table at index {j} is missing 'name'",
                    )
                )
                continue
            table_name = str(name)
            for key in sorted(table.keys()):
                if key in table_allowed:
                    continue
                sub_detail = t_legacy.get(key) or f"disallowed key '{key}'"
                rows.append(
                    (
                        (path_posix, source_id, f"table:{table_name}:{key}", 2),
                        f"table '{table_name}': {sub_detail}",
                    )
                )
            if check_config and config_allowed is not None:
                cfg = _source_table_config_mapping(path, source_id, table_name, table)
                if isinstance(cfg, ParseError):
                    rows.append(violation_row_parse_error(path_posix, cfg.message))
                else:
                    for ck in sorted(cfg.keys()):
                        if ck in config_allowed:
                            continue
                        sub = c_leg.get(ck) or f"disallowed key '{ck}'"
                        rows.append(
                            (
                                (
                                    path_posix,
                                    source_id,
                                    f"table:{table_name}:cfg:{ck}",
                                    2,
                                ),
                                f"table '{table_name}': config: {sub}",
                            )
                        )
            if (
                check_source_table_columns
                and column_allowed is not None
                and "columns" in table
            ):
                raw_columns = table["columns"]
                if not isinstance(raw_columns, list):
                    rows.append(
                        violation_row_parse_error(
                            path_posix,
                            f"source '{source_id}': table '{table_name}': "
                            f"columns must be a list",
                        )
                    )
                    continue
                for i, col in enumerate(raw_columns):
                    if col is None or not isinstance(col, Mapping):
                        rows.append(
                            violation_row_parse_error(
                                path_posix,
                                f"source '{source_id}': table '{table_name}': column at "
                                f"index {i} must be a mapping",
                            )
                        )
                        continue
                    col_name = col.get("name")
                    if not col_name:
                        rows.append(
                            violation_row_parse_error(
                                path_posix,
                                f"source '{source_id}': table '{table_name}': column at "
                                f"index {i} is missing 'name'",
                            )
                        )
                        continue
                    cname = str(col_name)
                    for ckey in sorted(col.keys()):
                        if ckey in column_allowed:
                            continue
                        sub_d = col_leg.get(ckey) or f"disallowed key '{ckey}'"
                        rows.append(
                            (
                                (
                                    path_posix,
                                    source_id,
                                    f"table:{table_name}:col:{cname}:{ckey}",
                                    2,
                                ),
                                f"table '{table_name}': column '{cname}': {sub_d}",
                            )
                        )
    return rows


def _source_table_config_mapping(
    path: Path,
    source_id: str,
    table_name: str,
    table: Mapping[str, Any],
) -> ParseError | dict[str, Any]:
    """``config:`` for one source table row (prefix ``source '…': table '…'`` in errors)."""
    pfx = f"source '{source_id}': table '{table_name}'"
    if "config" not in table:
        return {}
    cfg = table["config"]
    if cfg is None:
        return ParseError(
            path,
            f"{pfx}: config must be a mapping, not null",
        )
    if not isinstance(cfg, MutableMapping):
        return ParseError(
            path,
            f"{pfx}: config must be a mapping, got {type(cfg).__name__}",
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
    `--check-config`**, ``yaml-handling.md`` § Errors).

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


def parse_bool_flag(raw: str) -> bool:
    """Parse Typer string booleans (``--check-config`` / ``--fix-legacy-yaml`` style)."""
    return raw.lower() not in ("false", "0", "no", "f", "off")


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
    check_config: bool = True,
    config_allowed: frozenset[str] | None = None,
    config_legacy_key_messages: Mapping[str, str] | None = None,
    check_columns: bool = True,
    column_allowed: frozenset[str] | None = None,
    column_legacy_key_messages: Mapping[str, str] | None = None,
    resource_label: str = "",
    fix_legacy_yaml: bool = False,
    check_source_tables: bool = False,
    check_source_table_columns: bool = False,
    source_table_allowed: frozenset[str] | None = None,
    source_table_legacy_key_messages: Mapping[str, str] | None = None,
    source_table_column_allowed: frozenset[str] | None = None,
    source_table_column_legacy_key_messages: Mapping[str, str] | None = None,
) -> list[ViolationRow]:
    """Walk *files*, load YAML, and validate top-level keys on each resource entry.

    When *check_config* is ``True`` and *config_allowed* is provided, also validates
    direct keys under each entry's ``config:`` mapping using the same allowlists as
    ``*-allowed-config-keys`` (``specs/hook-families/allowed-keys.md`` § **Nested
    keys (`config`) and `--check-config`**).

    When *check_columns* is ``True`` and *column_allowed* is provided, also validates
    direct keys on each entry in the ``columns:`` list using the per-resource column
    allowlists from ``resource_keys`` (``specs/hook-families/allowed-keys.md`` §
    **Nested keys (`columns:`) and `--check-columns`**).

    When *resource_label* is ``"source"``, *check_source_tables* is ``True``, and
    *source_table_allowed* is not ``None``, also walks ``sources: → tables:`` (and
    optionally ``columns:`` per table) per § **Nested keys** for sources.

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
        check_config: When ``True`` (default) and *config_allowed* is set, also check
            direct keys under each entry's ``config:`` mapping.
        config_allowed: Allowlisted keys under ``config:`` (from ``resource_config_keys``).
            Required for nested checking; pass ``None`` to disable.
        config_legacy_key_messages: Optional legacy-key detail map for ``config`` keys.
        check_columns: When ``True`` (default) and *column_allowed* is set, also check
            direct keys on each entry in the resource's ``columns:`` list.
        column_allowed: Allowlisted keys on each column entry (from ``resource_keys``
            ``*_COLUMN_ALLOWED_KEYS``). Required for column checking; pass ``None`` to
            disable.
        column_legacy_key_messages: Optional legacy-key detail map for column keys.
        resource_label: Singular resource noun (e.g. ``\"model\"``); used in ``config``
            and column shape-error messages when nested checking is active.
        fix_legacy_yaml: When ``True``, run the ``--fix-legacy-yaml`` rewrites
            (``fix-legacy-yaml.md``: ``tests`` → ``data_tests``, top-level ``meta`` / ``tags`` → ``config``) before
            loading. Only **property-YAML** hooks that ship this
            flag (§§1–6 in ``allowed-keys.md``) should pass ``True``; **catalog** and
            **dbt-project** hooks **MUST NOT** expose the flag.
        check_source_tables: For ``source`` only: enable table-row validation.
        check_source_table_columns: For ``source`` only: enable column validation
            under each table (ignored when *check_source_tables* is ``False``).
        source_table_allowed: ``SOURCE_TABLE_ALLOWED_KEYS`` or ``None``.
        source_table_legacy_key_messages: Optional legacy map for table keys.
        source_table_column_allowed: ``SOURCE_TABLE_COLUMN_ALLOWED_KEYS`` or ``None``.
        source_table_column_legacy_key_messages: Optional legacy map for
            source-table column keys.

    Returns:
        Unsorted violation rows.
    """
    rows: list[ViolationRow] = []
    run_config = check_config and config_allowed is not None
    run_columns = check_columns and column_allowed is not None
    run_source_tables = (
        resource_label == "source"
        and check_source_tables
        and source_table_allowed is not None
    )
    for path in files:
        path = path.expanduser()
        if fix_legacy_yaml:
            fix_out = apply_fix_legacy_yaml(
                path,
                check_source_tables=check_source_tables
                if resource_label == "source"
                else False,
                check_source_table_columns=check_source_table_columns
                if resource_label == "source"
                else False,
            )
            if fix_out[0] == "skip":
                continue
            if fix_out[0] == "fail":
                _, err_msgs = fix_out
                for msg in err_msgs:
                    rows.append(violation_row_parse_error(path.as_posix(), msg))
                continue
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
        if run_config:
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
        if run_columns:
            rows.extend(
                _nested_column_violations(
                    path.as_posix(),
                    iter_entries(inner),
                    resource_label=resource_label,
                    column_allowed=column_allowed,  # type: ignore[arg-type]
                    column_legacy_key_messages=column_legacy_key_messages,
                )
            )
        if run_source_tables:
            rows.extend(
                _nested_source_table_violations(
                    path,
                    path.as_posix(),
                    iter_entries(inner),
                    table_allowed=source_table_allowed,  # type: ignore[arg-type]
                    table_legacy_key_messages=source_table_legacy_key_messages,
                    check_config=run_config,
                    config_allowed=config_allowed,
                    config_legacy_key_messages=config_legacy_key_messages,
                    check_source_table_columns=check_source_table_columns,
                    column_allowed=source_table_column_allowed,
                    column_legacy_key_messages=source_table_column_legacy_key_messages,
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
