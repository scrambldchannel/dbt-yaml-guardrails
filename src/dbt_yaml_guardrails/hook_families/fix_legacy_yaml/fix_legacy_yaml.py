"""CLI: ``fix-legacy-yaml`` — ``specs/hook-families/fix-legacy-yaml.md``."""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from dbt_yaml_guardrails.yaml_handling import ParseError, ParseSkip

from .legacy_rewrite_core import (
    load_property_yaml_roundtrip,
    rewrite_tests_to_data_tests_v1,
    write_roundtrip,
)


def main(
    files: list[Path] = typer.Argument(default_factory=list),
    write: bool = typer.Option(
        False,
        "--write",
        help=(
            "Write files in place after rewrites. Without this, check only "
            "(exit 1 if any file would change or has conflicts)."
        ),
    ),
) -> None:
    """Rewrite legacy ``tests`` keys to ``data_tests`` in dbt property YAML (v1).

    Default is check mode: exit 0 if nothing to do, exit 1 if any file would change
    or has conflicts. Use --write to apply changes.
    """
    if not files:
        raise typer.Exit(0)

    any_issue = False
    for path in files:
        path = path.expanduser()
        loaded = load_property_yaml_roundtrip(path)
        if isinstance(loaded, ParseSkip):
            continue
        if isinstance(loaded, ParseError):
            typer.echo(f"{path}: {loaded.message}", err=True)
            any_issue = True
            continue

        root = loaded
        renames, conflicts = rewrite_tests_to_data_tests_v1(root, path)
        for line in conflicts:
            typer.echo(line, err=True)

        needs_attention = renames > 0 or bool(conflicts)
        if not needs_attention:
            continue
        if not write:
            any_issue = True
            continue
        if renames > 0:
            err = write_roundtrip(path, root)
            if err is not None:
                typer.echo(f"{path}: {err}", err=True)
                any_issue = True
        if conflicts:
            any_issue = True

    raise typer.Exit(1 if any_issue else 0)


def cli_main() -> None:
    try:
        typer.run(main)
    except typer.Exit as e:
        sys.exit(e.exit_code)


if __name__ == "__main__":
    cli_main()
