"""source-allowed-meta-keys CLI (``specs/hook-families/allowed-meta-keys.md``)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping

import typer

from dbt_yaml_guardrails.hook_families.allowed_meta_keys.allowed_meta_keys_core import (
    run_allowed_meta_keys_cli,
)
from dbt_yaml_guardrails.yaml_handling import (
    ParseError,
    ParseSuccess,
    SourceEntriesSkip,
    extract_source_entries,
    iter_source_entries,
)


def _extract_sources_by_name(
    success: ParseSuccess,
) -> ParseError | Mapping[str, Mapping[str, Any]] | None:
    r = extract_source_entries(success)
    if isinstance(r, SourceEntriesSkip):
        return None
    if isinstance(r, ParseError):
        return r
    return r.by_name


def _run(
    files: list[Path],
    required_csv: str,
    forbidden_csv: str,
    allowed_option: str | None,
) -> int:
    return run_allowed_meta_keys_cli(
        files,
        required_csv,
        forbidden_csv,
        allowed_option,
        resource_kind="source",
        extract_by_name=_extract_sources_by_name,
        iter_entries=iter_source_entries,
        emit=lambda m: typer.echo(m, err=True),
    )


def main(
    files: list[Path] = typer.Argument(default_factory=list),
    required: str = typer.Option("", "--required"),
    forbidden: str = typer.Option("", "--forbidden"),
    allowed: str | None = typer.Option(
        None,
        "--allowed",
        help=(
            "Comma-separated meta keys that may appear under config.meta "
            "(optional; if set, enables allowlist mode per specs/hook-families/allowed-meta-keys.md)."
        ),
    ),
) -> None:
    """Validate keys on config.meta for each source entry."""
    code = _run(files, required, forbidden, allowed)
    raise typer.Exit(code)


def cli_main() -> None:
    """Entry point for the ``source-allowed-meta-keys`` console script."""
    try:
        typer.run(main)
    except typer.Exit as e:
        sys.exit(e.exit_code)


if __name__ == "__main__":
    cli_main()
