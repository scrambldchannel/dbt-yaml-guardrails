"""model-allowed-meta-keys CLI (``specs/hook-families/allowed-meta-keys.md``)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping

import typer

from dbt_yaml_guardrails.hook_families.allowed_keys.allowed_keys_core import (
    finalize_violation_rows,
    parse_csv_keys,
)
from dbt_yaml_guardrails.hook_families.allowed_meta_keys.allowed_meta_keys_core import (
    collect_violation_rows_for_model_meta_paths,
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


def _run(
    files: list[Path],
    required_csv: str,
    forbidden_csv: str,
    allowed_option: str | None,
) -> int:
    required = parse_csv_keys(required_csv)
    forbidden = parse_csv_keys(forbidden_csv)
    if allowed_option is None:
        allowed: frozenset[str] | None = None
    else:
        allowed = frozenset(parse_csv_keys(allowed_option))

    if allowed is None and not required and not forbidden:
        return 0

    if not files:
        return 0

    rows = collect_violation_rows_for_model_meta_paths(
        files,
        required,
        forbidden,
        allowed,
        extract_by_name=_extract_models_by_name,
        iter_entries=iter_model_entries,
    )
    return finalize_violation_rows(
        rows,
        resource_label="model",
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
    """Validate keys on config.meta for each model entry."""
    code = _run(files, required, forbidden, allowed)
    raise typer.Exit(code)


def cli_main() -> None:
    """Entry point for the ``model-allowed-meta-keys`` console script."""
    try:
        typer.run(main)
    except typer.Exit as e:
        sys.exit(e.exit_code)


if __name__ == "__main__":
    cli_main()
