"""exposure-allowed-config-keys CLI (``specs/hook-families/allowed-config-keys.md``)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping

import typer

from dbt_yaml_guardrails.hook_families.allowed_config_keys.allowed_config_keys_core import (
    run_allowed_config_keys_cli,
)
from dbt_yaml_guardrails.hook_families.allowed_config_keys.resource_config_keys import (
    EXPOSURE_CONFIG_ALLOWED_KEYS,
    EXPOSURE_CONFIG_LEGACY_KEY_MESSAGES,
)
from dbt_yaml_guardrails.yaml_handling import (
    ExposureEntriesSkip,
    ParseError,
    ParseSuccess,
    extract_exposure_entries,
    iter_exposure_entries,
)


def _extract_exposure_by_name(
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
    required_csv: str,
    forbidden_csv: str,
) -> int:
    return run_allowed_config_keys_cli(
        files,
        required_csv,
        forbidden_csv,
        allowed=EXPOSURE_CONFIG_ALLOWED_KEYS,
        legacy_key_messages=EXPOSURE_CONFIG_LEGACY_KEY_MESSAGES,
        resource_kind="exposure",
        extract_by_name=_extract_exposure_by_name,
        iter_entries=iter_exposure_entries,
        emit=lambda m: typer.echo(m, err=True),
    )


def main(
    files: list[Path] = typer.Argument(default_factory=list),
    required: str = typer.Option("", "--required"),
    forbidden: str = typer.Option(
        "",
        "--forbidden",
        help=(
            "Comma-separated keys that must not appear under config "
            "(stricter than the fixed allowlist in specs/resource-config-keys.md § Exposures)."
        ),
    ),
) -> None:
    """Validate top-level keys under config on each exposure entry."""
    code = _run(files, required, forbidden)
    raise typer.Exit(code)


def cli_main() -> None:
    """Entry point for the ``exposure-allowed-config-keys`` console script."""
    try:
        typer.run(main)
    except typer.Exit as e:
        sys.exit(e.exit_code)


if __name__ == "__main__":
    cli_main()
