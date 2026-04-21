"""Tests for seed-tags-accepted-values CLI (specs/hook-families/tags-accepted-values.md)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SEEDS = _REPO_ROOT / "tests" / "fixtures" / "yaml" / "tags_accepted_values" / "seeds"


def _invoke(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "dbt_yaml_guardrails.hook_families.tags_accepted_values.seed_tags_accepted_values",
            *args,
        ],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
    )


def test_cli_passes() -> None:
    r = _invoke("--values", "marketing,raw", str(_SEEDS / "tags_ok.yml"))
    assert r.returncode == 0
    assert r.stderr == ""
