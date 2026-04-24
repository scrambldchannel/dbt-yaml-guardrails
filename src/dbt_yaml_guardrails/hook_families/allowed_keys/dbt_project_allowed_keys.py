"""dbt-project-allowed-keys CLI (``specs/hook-families/allowed-keys.md`` §8; allowlist in ``resource_keys``)."""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from .allowed_keys_core import (
    collect_violation_rows_for_dbt_project_paths,
    finalize_violation_rows,
    parse_csv_keys,
)
from .resource_keys import (
    DBT_PROJECT_ALLOWED_KEYS,
    DBT_PROJECT_LEGACY_KEY_MESSAGES,
)


def _run(
    files: list[Path],
    required_csv: str,
    forbidden_csv: str,
) -> int:
    required = parse_csv_keys(required_csv)
    forbidden = parse_csv_keys(forbidden_csv)

    if not files:
        return 0

    rows = collect_violation_rows_for_dbt_project_paths(
        files,
        required,
        forbidden,
        DBT_PROJECT_ALLOWED_KEYS,
        legacy_key_messages=DBT_PROJECT_LEGACY_KEY_MESSAGES,
    )
    return finalize_violation_rows(
        rows,
        resource_label="project",
        emit=lambda m: typer.echo(m, err=True),
    )


def main(
    files: list[Path] = typer.Argument(default_factory=list),
    required: str = typer.Option("", "--required"),
    forbidden: str = typer.Option(
        "",
        "--forbidden",
        help=(
            "Comma-separated top-level keys that must not appear in dbt_project.yml "
            "(stricter than the fixed allowlist in specs/resource-keys.md § dbt project file)."
        ),
    ),
) -> None:
    """Validate top-level keys in dbt_project.yml (single project per file)."""
    code = _run(files, required, forbidden)
    raise typer.Exit(code)


def cli_main() -> None:
    """Entry point for the ``dbt-project-allowed-keys`` console script."""
    try:
        typer.run(main)
    except typer.Exit as e:
        sys.exit(e.exit_code)


if __name__ == "__main__":
    cli_main()
