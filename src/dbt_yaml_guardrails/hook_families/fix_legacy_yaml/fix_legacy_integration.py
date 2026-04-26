"""Optional ``--fix-legacy-yaml`` phase for *-allowed-keys (``fix-legacy-yaml.md``)."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from dbt_yaml_guardrails.yaml_handling import ParseError, ParseSkip

from .legacy_rewrite_core import (
    load_property_yaml_roundtrip,
    rewrite_tests_to_data_tests_v1,
    write_roundtrip,
)


def _detail_without_path_prefix(path: Path, line: str) -> str:
    """Strip ``path: `` prefix so :func:`format_violation_line` can prepend *path* once."""
    p = str(path).replace("\\", "/")
    prefix = f"{p}: "
    if line.startswith(prefix):
        return line[len(prefix) :]
    return line


def apply_tests_to_data_tests_fix(
    path: Path,
) -> tuple[Literal["ok", "skip"], None] | tuple[Literal["fail"], tuple[str, ...]]:
    """Apply v1 ``tests`` → ``data_tests`` rewrites in place (ruamel round-trip).

    Returns:
        ``("ok", None)`` or ``("skip", None)`` — proceed or skip file (no validation), same as
        :func:`load_property_yaml` skip for ``skip``.
        ``("fail", (details...))`` — detail strings are **without** a leading path prefix
        (suitable for :func:`~dbt_yaml_guardrails.hook_families.allowed_keys.allowed_keys_core.violation_row_parse_error`).
    """
    path = path.expanduser()
    loaded = load_property_yaml_roundtrip(path)
    if isinstance(loaded, ParseSkip):
        return ("skip", None)
    if isinstance(loaded, ParseError):
        return ("fail", (loaded.message,))

    root = loaded
    renames, conflicts = rewrite_tests_to_data_tests_v1(root, path)
    if conflicts:
        return (
            "fail",
            tuple(_detail_without_path_prefix(path, c) for c in conflicts),
        )

    if renames > 0:
        err = write_roundtrip(path, root)
        if err is not None:
            return ("fail", (err,))

    return ("ok", None)
