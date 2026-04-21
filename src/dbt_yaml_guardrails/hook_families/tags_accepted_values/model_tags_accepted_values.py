"""model-tags-accepted-values CLI (``specs/hook-families/tags-accepted-values.md``)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping

import typer

from dbt_yaml_guardrails.hook_families.tags_accepted_values.tags_accepted_values_core import (
    run_tags_accepted_values_cli,
)
from dbt_yaml_guardrails.yaml_handling import (
    ModelEntriesSkip,
    ParseError,
    ParseSuccess,
    extract_model_entries,
    iter_model_entries,
)


def _extract_models_by_name(
    success: ParseSuccess,
) -> ParseError | Mapping[str, Mapping[str, Any]] | None:
    r = extract_model_entries(success)
    if isinstance(r, ModelEntriesSkip):
        return None
    if isinstance(r, ParseError):
        return r
    return r.by_name


def _run(files: list[Path], values: str) -> int:
    return run_tags_accepted_values_cli(
        files,
        values,
        resource_kind="model",
        extract_by_name=_extract_models_by_name,
        iter_entries=iter_model_entries,
        emit=lambda m: typer.echo(m, err=True),
    )


def main(
    files: list[Path] = typer.Argument(default_factory=list),
    values: str = typer.Option(
        ...,
        "--values",
        help="Comma-separated allowed tag values (config.tags string or list).",
    ),
) -> None:
    """Validate config.tags against --values per model entry."""
    code = _run(files, values)
    raise typer.Exit(code)


def cli_main() -> None:
    """Entry point for the ``model-tags-accepted-values`` console script."""
    try:
        typer.run(main)
    except typer.Exit as e:
        sys.exit(e.exit_code)


if __name__ == "__main__":
    cli_main()
