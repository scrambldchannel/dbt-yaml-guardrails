"""seed-allowed-column-keys CLI (``specs/hook-families/allowed-column-keys.md``)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping

import typer

from dbt_yaml_guardrails.hook_families.allowed_column_keys.allowed_column_keys_core import (
    run_allowed_column_keys_cli,
)
from dbt_yaml_guardrails.hook_families.allowed_keys.allowed_keys_core import (
    parse_bool_flag,
)
from dbt_yaml_guardrails.hook_families.allowed_keys.resource_keys import (
    SEED_COLUMN_ALLOWED_KEYS,
    SEED_COLUMN_LEGACY_KEY_MESSAGES,
)
from dbt_yaml_guardrails.yaml_handling import (
    ParseError,
    ParseSuccess,
    SeedEntriesSkip,
    extract_seed_entries,
    iter_seed_entries,
)


def _extract_seed_by_name(
    success: ParseSuccess,
) -> ParseError | Mapping[str, Mapping[str, Any]] | None:
    r = extract_seed_entries(success)
    if isinstance(r, SeedEntriesSkip):
        return None
    if isinstance(r, ParseError):
        return r
    return r.by_name


def _run(
    files: list[Path],
    required_csv: str,
    forbidden_csv: str,
    fix_legacy_yaml: bool = False,
) -> int:
    return run_allowed_column_keys_cli(
        files,
        required_csv,
        forbidden_csv,
        allowed=SEED_COLUMN_ALLOWED_KEYS,
        legacy_key_messages=SEED_COLUMN_LEGACY_KEY_MESSAGES,
        resource_label="seed",
        resource_plural="seed",
        extract_by_name=_extract_seed_by_name,
        iter_entries=iter_seed_entries,
        emit=lambda m: typer.echo(m, err=True),
        fix_legacy_yaml=fix_legacy_yaml,
    )


def main(
    files: list[Path] = typer.Argument(default_factory=list),
    required: str = typer.Option("", "--required"),
    forbidden: str = typer.Option(
        "",
        "--forbidden",
        help=(
            "Comma-separated keys that must not appear on any column entry "
            "(stricter than the fixed allowlist in specs/resource-keys.md § Seeds — Column keys)."
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
    """Validate direct keys on each column entry for seed entries."""
    code = _run(
        files, required, forbidden, fix_legacy_yaml=parse_bool_flag(fix_legacy_yaml)
    )
    raise typer.Exit(code)


def cli_main() -> None:
    """Entry point for the ``seed-allowed-column-keys`` console script."""
    try:
        typer.run(main)
    except typer.Exit as e:
        sys.exit(e.exit_code)


if __name__ == "__main__":
    cli_main()
