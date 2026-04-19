"""macro-allowed-keys CLI (``specs/hooks.md``; allowlist in ``resource_keys``)."""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from dbt_yaml_guardrails.allowed_keys_core import (
    ViolationRow,
    parse_csv_keys,
    print_violation_rows,
    sort_violation_rows,
    violation_row_parse_error,
    violations_for_entries,
)
from dbt_yaml_guardrails.resource_keys import MACRO_ALLOWED_KEYS
from dbt_yaml_guardrails.yaml_handling import (
    MacroEntriesResult,
    MacroEntriesSkip,
    ParseError,
    ParseSkip,
    extract_macro_entries,
    iter_macro_entries,
    load_property_yaml,
)


def _run(
    files: list[Path],
    required_csv: str,
    forbidden_csv: str,
) -> int:
    required = parse_csv_keys(required_csv)
    forbidden = parse_csv_keys(forbidden_csv)
    allowed = MACRO_ALLOWED_KEYS

    if "name" in required:
        typer.echo(
            "error: do not list 'name' in --required (it is always present on real macros)",
            err=True,
        )
        return 2

    if not files:
        return 0

    rows: list[ViolationRow] = []

    for path in files:
        path = path.expanduser()
        loaded = load_property_yaml(path)
        if isinstance(loaded, ParseSkip):
            continue
        if isinstance(loaded, ParseError):
            rows.append(violation_row_parse_error(path.as_posix(), loaded.message))
            continue
        extracted = extract_macro_entries(loaded)
        if isinstance(extracted, MacroEntriesSkip):
            continue
        if isinstance(extracted, ParseError):
            rows.append(violation_row_parse_error(path.as_posix(), extracted.message))
            continue
        assert isinstance(extracted, MacroEntriesResult)

        rows.extend(
            violations_for_entries(
                path.as_posix(),
                iter_macro_entries(extracted.by_name),
                allowed=allowed,
                required=required,
                forbidden=forbidden,
            )
        )

    if not rows:
        return 0

    sort_violation_rows(rows)
    print_violation_rows(
        rows, resource_label="macro", emit=lambda m: typer.echo(m, err=True)
    )
    return 1


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
