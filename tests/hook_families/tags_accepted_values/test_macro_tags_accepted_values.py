"""Tests for macro-tags-accepted-values CLI (specs/hook-families/tags-accepted-values.md)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_FIX = _REPO_ROOT / "tests" / "fixtures" / "yaml" / "tags_accepted_values" / "macros"


def _invoke(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "dbt_yaml_guardrails.hook_families.tags_accepted_values.macro_tags_accepted_values",
            *args,
        ],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
    )


def test_cli_passes() -> None:
    r = _invoke("--values", "utils,ops", str(_FIX / "tags_ok.yml"))
    assert r.returncode == 0
    assert r.stderr == ""
