"""macro-allowed-keys CLI (``specs/hooks.md``; allowlist in ``resource_keys``)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping

import typer

from dbt_yaml_guardrails.allowed_keys_core import (
    collect_violation_rows_for_property_paths,
    finalize_violation_rows,
    message_name_in_required,
    parse_csv_keys,
)
from dbt_yaml_guardrails.resource_keys import MACRO_ALLOWED_KEYS
from dbt_yaml_guardrails.yaml_handling import (
    MacroEntriesSkip,
    ParseError,
    ParseSuccess,
    extract_macro_entries,
    iter_macro_entries,
)


def _extract_macro_by_name(
    success: ParseSuccess,
) -> ParseError | Mapping[str, Mapping[str, Any]] | None:
    r = extract_macro_entries(success)
    if isinstance(r, MacroEntriesSkip):
        return None
    if isinstance(r, ParseError):
        return r
    return r.by_name


def _run(
    files: list[Path],
    required_csv: str,
    forbidden_csv: str,
) -> int:
    required = parse_csv_keys(required_csv)
    forbidden = parse_csv_keys(forbidden_csv)

    if "name" in required:
        typer.echo(message_name_in_required(resource_plural="macros"), err=True)
        return 2

    if not files:
        return 0

    rows = collect_violation_rows_for_property_paths(
        files,
        required,
        forbidden,
        MACRO_ALLOWED_KEYS,
        extract_by_name=_extract_macro_by_name,
        iter_entries=iter_macro_entries,
    )
    return finalize_violation_rows(
        rows,
        resource_label="macro",
        emit=lambda m: typer.echo(m, err=True),
    )


def main(
    files: list[Path] = typer.Argument(default_factory=list),
    required: str = typer.Option("", "--required"),
    forbidden: str = typer.Option(
        "",
        "--forbidden",
        help=(
            "Comma-separated keys that must not appear on a macro entry "
            "(stricter than the fixed allowlist in specs/resource-keys.md § Macros)."
        ),
    ),
) -> None:
    """Validate top-level keys on each macro entry."""
    code = _run(files, required, forbidden)
    raise typer.Exit(code)


def cli_main() -> None:
    """Entry point for the ``macro-allowed-keys`` console script."""
    try:
        typer.run(main)
    except typer.Exit as e:
        sys.exit(e.exit_code)


if __name__ == "__main__":
    cli_main()
