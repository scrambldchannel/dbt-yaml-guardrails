"""model-allowed-keys CLI (``specs/hooks.md``)."""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from dbt_yaml_guardrails.yaml_handling import (
    ModelEntriesResult,
    ModelEntriesSkip,
    ParseError,
    ParseSkip,
    extract_model_entries,
    iter_model_entries,
    load_property_yaml,
)

# Fixed allowlist — keep aligned with ``specs/resource-keys.md`` § Models.
DEFAULT_ALLOWED_KEYS: frozenset[str] = frozenset(
    (
        "name",
        "description",
        "columns",
        "data_tests",
        "versions",
        "latest_version",
        "version",
        "constraints",
        "docs",
        "config",
    )
)


def _parse_csv_keys(raw: str) -> set[str]:
    return {part.strip() for part in raw.split(",") if part.strip()}


def _run(
    files: list[Path],
    required_csv: str,
    forbidden_csv: str,
) -> int:
    required = _parse_csv_keys(required_csv)
    forbidden = _parse_csv_keys(forbidden_csv)
    allowed = DEFAULT_ALLOWED_KEYS

    if "name" in required:
        typer.echo(
            "error: do not list 'name' in --required (it is always present on real models)",
            err=True,
        )
        return 2

    if not files:
        return 0

    records: list[tuple[str, str, str]] = []

    for path in files:
        path = path.expanduser()
        loaded = load_property_yaml(path)
        if isinstance(loaded, ParseSkip):
            continue
        if isinstance(loaded, ParseError):
            records.append((path.as_posix(), "", loaded.message))
            continue
        extracted = extract_model_entries(loaded)
        if isinstance(extracted, ModelEntriesSkip):
            continue
        if isinstance(extracted, ParseError):
            records.append((path.as_posix(), "", extracted.message))
            continue
        assert isinstance(extracted, ModelEntriesResult)

        for model_name, entry in iter_model_entries(extracted.by_name):
            keys = set(entry.keys())
            for req in sorted(required):
                if req not in keys:
                    records.append(
                        (
                            path.as_posix(),
                            model_name,
                            f"missing required key '{req}'",
                        )
                    )
            for key in sorted(keys):
                if key in forbidden:
                    records.append(
                        (
                            path.as_posix(),
                            model_name,
                            f"forbidden key '{key}'",
                        )
                    )
                elif key not in allowed:
                    records.append(
                        (
                            path.as_posix(),
                            model_name,
                            f"disallowed key '{key}'",
                        )
                    )

    if not records:
        return 0

    records.sort(key=lambda r: (r[0], r[1], r[2]))
    for fspath, model, detail in records:
        if model:
            line = f"{fspath}: model '{model}': {detail}"
        else:
            line = f"{fspath}: {detail}"
        typer.echo(line, err=True)

    return 1


def main(
    files: list[Path] = typer.Argument(default_factory=list),
    required: str = typer.Option("", "--required"),
    forbidden: str = typer.Option(
        "",
        "--forbidden",
        help=(
            "Comma-separated keys that must not appear on a model entry "
            "(stricter than the fixed allowlist in specs/resource-keys.md § Models)."
        ),
    ),
) -> None:
    """Validate top-level keys on each model entry."""
    code = _run(files, required, forbidden)
    raise typer.Exit(code)


def cli_main() -> None:
    """Entry point for the ``model-allowed-keys`` console script."""
    try:
        typer.run(main)
    except typer.Exit as e:
        sys.exit(e.exit_code)


if __name__ == "__main__":
    cli_main()
