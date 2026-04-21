"""exposure-meta-accepted-values CLI (``specs/hook-families/meta-accepted-values.md``)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping

import typer

from dbt_yaml_guardrails.hook_families.meta_accepted_values.meta_accepted_values_core import (
    run_meta_accepted_values_cli,
)
from dbt_yaml_guardrails.yaml_handling import (
    ExposureEntriesSkip,
    ParseError,
    ParseSuccess,
    extract_exposure_entries,
    iter_exposure_entries,
)


def _extract_exposures_by_name(
    success: ParseSuccess,
) -> ParseError | Mapping[str, Mapping[str, Any]] | None:
    r = extract_exposure_entries(success)
    if isinstance(r, ExposureEntriesSkip):
        return None
    if isinstance(r, ParseError):
        return r
    return r.by_name


def _run(
    files: list[Path],
    key: str,
    values: str,
    optional: bool,
) -> int:
    return run_meta_accepted_values_cli(
        files,
        key,
        values,
        optional,
        resource_kind="exposure",
        extract_by_name=_extract_exposures_by_name,
        iter_entries=iter_exposure_entries,
        emit=lambda m: typer.echo(m, err=True),
    )


def main(
    files: list[Path] = typer.Argument(default_factory=list),
    key: str = typer.Option(
        ...,
        "--key",
        help="Dot path under config.meta (e.g. domain or owner.name).",
    ),
    values: str = typer.Option(
        ...,
        "--values",
        help="Comma-separated allowed values; leaf may be a string or list of strings.",
    ),
    optional: bool = typer.Option(
        False,
        "--optional",
        help="If set, missing path is OK; if present, value must match --values.",
    ),
) -> None:
    """Validate a string or string list at --key under config.meta against --values."""
    code = _run(files, key, values, optional)
    raise typer.Exit(code)


def cli_main() -> None:
    """Entry point for the ``exposure-meta-accepted-values`` console script."""
    try:
        typer.run(main)
    except typer.Exit as e:
        sys.exit(e.exit_code)


if __name__ == "__main__":
    cli_main()
