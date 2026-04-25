"""model-allowed-column-keys CLI (``specs/hook-families/allowed-column-keys.md``)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping

import typer

from dbt_yaml_guardrails.hook_families.allowed_column_keys.allowed_column_keys_core import (
    run_allowed_column_keys_cli,
)
from dbt_yaml_guardrails.hook_families.allowed_keys.resource_keys import (
    MODEL_COLUMN_ALLOWED_KEYS,
    MODEL_COLUMN_LEGACY_KEY_MESSAGES,
)
from dbt_yaml_guardrails.yaml_handling import (
    ModelEntriesSkip,
    ParseError,
    ParseSuccess,
    extract_model_entries,
    iter_model_entries,
)


def _extract_model_by_name(
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
) -> int:
    return run_allowed_column_keys_cli(
        files,
        required_csv,
        forbidden_csv,
        allowed=MODEL_COLUMN_ALLOWED_KEYS,
        legacy_key_messages=MODEL_COLUMN_LEGACY_KEY_MESSAGES,
        resource_label="model",
        resource_plural="model",
        extract_by_name=_extract_model_by_name,
        iter_entries=iter_model_entries,
        emit=lambda m: typer.echo(m, err=True),
    )


def main(
    files: list[Path] = typer.Argument(default_factory=list),
    required: str = typer.Option("", "--required"),
    forbidden: str = typer.Option(
        "",
        "--forbidden",
        help=(
            "Comma-separated keys that must not appear on any column entry "
            "(stricter than the fixed allowlist in specs/resource-keys.md § Models — Column keys)."
        ),
    ),
) -> None:
    """Validate direct keys on each column entry for model entries."""
    code = _run(files, required, forbidden)
    raise typer.Exit(code)


def cli_main() -> None:
    """Entry point for the ``model-allowed-column-keys`` console script."""
    try:
        typer.run(main)
    except typer.Exit as e:
        sys.exit(e.exit_code)


if __name__ == "__main__":
    cli_main()
