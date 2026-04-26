"""source-allowed-keys CLI (``specs/hook-families/allowed-keys.md``; allowlist in ``resource_keys``)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping

import typer

from dbt_yaml_guardrails.yaml_handling import (
    ParseError,
    ParseSuccess,
    SourceEntriesSkip,
    extract_source_entries,
    iter_source_entries,
)

from .allowed_keys_core import (
    collect_violation_rows_for_property_paths,
    finalize_violation_rows,
    message_name_in_required,
    parse_bool_flag,
    parse_csv_keys,
)
from dbt_yaml_guardrails.hook_families.allowed_config_keys.resource_config_keys import (
    SOURCE_CONFIG_ALLOWED_KEYS,
    SOURCE_CONFIG_LEGACY_KEY_MESSAGES,
)

from .resource_keys import (
    SOURCE_ALLOWED_KEYS,
    SOURCE_LEGACY_KEY_MESSAGES,
    SOURCE_TABLE_ALLOWED_KEYS,
    SOURCE_TABLE_COLUMN_ALLOWED_KEYS,
    SOURCE_TABLE_COLUMN_LEGACY_KEY_MESSAGES,
    SOURCE_TABLE_LEGACY_KEY_MESSAGES,
)


def _extract_source_by_name(
    success: ParseSuccess,
) -> ParseError | Mapping[str, Mapping[str, Any]] | None:
    r = extract_source_entries(success)
    if isinstance(r, SourceEntriesSkip):
        return None
    if isinstance(r, ParseError):
        return r
    return r.by_name


def _message_contradictory_source_table_flags() -> str:
    return (
        "error: --check-source-tables false is incompatible with "
        "--check-source-table-columns true; pass --check-source-table-columns false "
        "when disabling table checks (column checks require table checks)"
    )


def _run(
    files: list[Path],
    required_csv: str,
    forbidden_csv: str,
    check_config: bool = True,
    check_source_tables: bool = True,
    check_source_table_columns: bool = True,
    fix_legacy_yaml: bool = False,
) -> int:
    required = parse_csv_keys(required_csv)
    forbidden = parse_csv_keys(forbidden_csv)

    if "name" in required:
        typer.echo(message_name_in_required(resource_plural="sources"), err=True)
        return 2

    if not check_source_tables and check_source_table_columns:
        typer.echo(_message_contradictory_source_table_flags(), err=True)
        return 2

    if not files:
        return 0

    st_allowed = SOURCE_TABLE_ALLOWED_KEYS if check_source_tables else None
    stc_allowed = (
        SOURCE_TABLE_COLUMN_ALLOWED_KEYS
        if (check_source_tables and check_source_table_columns)
        else None
    )

    rows = collect_violation_rows_for_property_paths(
        files,
        required,
        forbidden,
        SOURCE_ALLOWED_KEYS,
        legacy_key_messages=SOURCE_LEGACY_KEY_MESSAGES,
        extract_by_name=_extract_source_by_name,
        iter_entries=iter_source_entries,
        check_config=check_config,
        config_allowed=SOURCE_CONFIG_ALLOWED_KEYS,
        config_legacy_key_messages=SOURCE_CONFIG_LEGACY_KEY_MESSAGES,
        check_columns=False,
        column_allowed=None,
        column_legacy_key_messages=None,
        resource_label="source",
        fix_legacy_yaml=fix_legacy_yaml,
        check_source_tables=check_source_tables,
        check_source_table_columns=check_source_table_columns,
        source_table_allowed=st_allowed,
        source_table_legacy_key_messages=SOURCE_TABLE_LEGACY_KEY_MESSAGES,
        source_table_column_allowed=stc_allowed,
        source_table_column_legacy_key_messages=SOURCE_TABLE_COLUMN_LEGACY_KEY_MESSAGES,
    )
    return finalize_violation_rows(
        rows,
        resource_label="source",
        emit=lambda m: typer.echo(m, err=True),
    )


def main(
    files: list[Path] = typer.Argument(default_factory=list),
    required: str = typer.Option("", "--required"),
    forbidden: str = typer.Option(
        "",
        "--forbidden",
        help=(
            "Comma-separated keys that must not appear on a source entry "
            "(stricter than the fixed allowlist in specs/resource-keys.md § Sources)."
        ),
    ),
    check_config: str = typer.Option(
        "true",
        "--check-config",
        help=(
            "Also validate direct keys under each entry's config: mapping using the "
            "same allowlist as source-allowed-config-keys (default: true). "
            "On each source table row, also validates table config: when --check-source-tables is on. "
            "Pass --check-config false to restore top-level-only behavior."
        ),
    ),
    check_source_tables: str = typer.Option(
        "true",
        "--check-source-tables",
        help=(
            "Also validate top-level keys (and with --check-config, table config: ) "
            "on each row under sources: … → tables: (default: true). "
            "If false, pass --check-source-table-columns false as well (exit 2 otherwise)."
        ),
    ),
    check_source_table_columns: str = typer.Option(
        "true",
        "--check-source-table-columns",
        help=(
            "When --check-source-tables is true, also validate top-level keys on each "
            "item under each table's columns: list (default: true). No effect if "
            "--check-source-tables is false."
        ),
    ),
    fix_legacy_yaml: str = typer.Option(
        "false",
        "--fix-legacy-yaml",
        help=(
            "If true, apply v1 tests→data_tests rewrites in place before validation "
            "(default: false). Nested source table/column rewrites only when "
            "--check-source-tables / --check-source-table-columns enable those paths. "
            "See specs/hook-families/fix-legacy-yaml.md."
        ),
    ),
) -> None:
    """Validate top-level keys on each source entry."""
    code = _run(
        files,
        required,
        forbidden,
        check_config=parse_bool_flag(check_config),
        check_source_tables=parse_bool_flag(check_source_tables),
        check_source_table_columns=parse_bool_flag(check_source_table_columns),
        fix_legacy_yaml=parse_bool_flag(fix_legacy_yaml),
    )
    raise typer.Exit(code)


def cli_main() -> None:
    """Entry point for the ``source-allowed-keys`` console script."""
    try:
        typer.run(main)
    except typer.Exit as e:
        sys.exit(e.exit_code)


if __name__ == "__main__":
    cli_main()
