"""snapshot-allowed-keys CLI (``specs/hook-families/allowed-keys.md``; allowlist in ``resource_keys``)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping

import typer

from dbt_yaml_guardrails.yaml_handling import (
    ParseError,
    ParseSuccess,
    SnapshotEntriesSkip,
    extract_snapshot_entries,
    iter_snapshot_entries,
)

from .allowed_keys_core import (
    collect_violation_rows_for_property_paths,
    finalize_violation_rows,
    message_name_in_required,
    parse_bool_flag,
    parse_csv_keys,
)
from dbt_yaml_guardrails.hook_families.allowed_config_keys.resource_config_keys import (
    SNAPSHOT_CONFIG_ALLOWED_KEYS,
    SNAPSHOT_CONFIG_LEGACY_KEY_MESSAGES,
)

from .resource_keys import (
    SNAPSHOT_ALLOWED_KEYS,
    SNAPSHOT_COLUMN_ALLOWED_KEYS,
    SNAPSHOT_COLUMN_LEGACY_KEY_MESSAGES,
    SNAPSHOT_LEGACY_KEY_MESSAGES,
)


def _extract_snapshot_by_name(
    success: ParseSuccess,
) -> ParseError | Mapping[str, Mapping[str, Any]] | None:
    r = extract_snapshot_entries(success)
    if isinstance(r, SnapshotEntriesSkip):
        return None
    if isinstance(r, ParseError):
        return r
    return r.by_name


def _run(
    files: list[Path],
    required_csv: str,
    forbidden_csv: str,
    check_config: bool = True,
    check_columns: bool = True,
    fix_legacy_yaml: bool = False,
) -> int:
    required = parse_csv_keys(required_csv)
    forbidden = parse_csv_keys(forbidden_csv)

    if "name" in required:
        typer.echo(message_name_in_required(resource_plural="snapshots"), err=True)
        return 2

    if not files:
        return 0

    rows = collect_violation_rows_for_property_paths(
        files,
        required,
        forbidden,
        SNAPSHOT_ALLOWED_KEYS,
        legacy_key_messages=SNAPSHOT_LEGACY_KEY_MESSAGES,
        extract_by_name=_extract_snapshot_by_name,
        iter_entries=iter_snapshot_entries,
        check_config=check_config,
        config_allowed=SNAPSHOT_CONFIG_ALLOWED_KEYS,
        config_legacy_key_messages=SNAPSHOT_CONFIG_LEGACY_KEY_MESSAGES,
        check_columns=check_columns,
        column_allowed=SNAPSHOT_COLUMN_ALLOWED_KEYS,
        column_legacy_key_messages=SNAPSHOT_COLUMN_LEGACY_KEY_MESSAGES,
        resource_label="snapshot",
        fix_legacy_yaml=fix_legacy_yaml,
    )
    return finalize_violation_rows(
        rows,
        resource_label="snapshot",
        emit=lambda m: typer.echo(m, err=True),
    )


def main(
    files: list[Path] = typer.Argument(default_factory=list),
    required: str = typer.Option("", "--required"),
    forbidden: str = typer.Option(
        "",
        "--forbidden",
        help=(
            "Comma-separated keys that must not appear on a snapshot entry "
            "(stricter than the fixed allowlist in specs/resource-keys.md § Snapshots)."
        ),
    ),
    check_config: str = typer.Option(
        "true",
        "--check-config",
        help=(
            "Also validate direct keys under each entry's config: mapping using the "
            "same allowlist as snapshot-allowed-config-keys (default: true). "
            "Pass --check-config false to restore top-level-only behavior."
        ),
    ),
    check_columns: str = typer.Option(
        "true",
        "--check-columns",
        help=(
            "Also validate direct keys on each column entry in columns: lists using "
            "SNAPSHOT_COLUMN_ALLOWED_KEYS (default: true). "
            "Pass --check-columns false to skip column key checks."
        ),
    ),
    fix_legacy_yaml: str = typer.Option(
        "false",
        "--fix-legacy-yaml",
        help=(
            "If true, apply v1 tests→data_tests rewrites in place before validation "
            "(default: false). See specs/hook-families/fix-legacy-yaml.md."
        ),
    ),
) -> None:
    """Validate top-level keys on each snapshot entry."""
    code = _run(
        files,
        required,
        forbidden,
        check_config=parse_bool_flag(check_config),
        check_columns=parse_bool_flag(check_columns),
        fix_legacy_yaml=parse_bool_flag(fix_legacy_yaml),
    )
    raise typer.Exit(code)


def cli_main() -> None:
    """Entry point for the ``snapshot-allowed-keys`` console script."""
    try:
        typer.run(main)
    except typer.Exit as e:
        sys.exit(e.exit_code)


if __name__ == "__main__":
    cli_main()
