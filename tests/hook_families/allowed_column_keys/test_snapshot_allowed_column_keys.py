"""Tests for snapshot-allowed-column-keys CLI (specs/hook-families/allowed-column-keys.md)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_YAML = _REPO_ROOT / "tests" / "fixtures" / "yaml"
_COL = _YAML / "allowed_column_keys"
_SHARED = _YAML / "shared"


def _f(name: str) -> str:
    return str(_COL / "snapshots" / name)


def _shared(name: str) -> str:
    return str(_SHARED / name)


def _invoke(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "dbt_yaml_guardrails.hook_families.allowed_column_keys.snapshot_allowed_column_keys",
            *args,
        ],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
    )


def test_cli_passes_clean_columns() -> None:
    r = _invoke(_f("columns_clean.yml"))
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_disallowed_column_key() -> None:
    r = _invoke(_f("columns_disallowed_key.yml"))
    assert r.returncode == 1
    assert "snapshot 'bad_snapshot'" in r.stderr
    assert "column 'id': disallowed key 'not_a_real_column_key'" in r.stderr


def test_cli_required_missing() -> None:
    r = _invoke("--required", "description", _f("columns_disallowed_key.yml"))
    assert r.returncode == 1
    assert "snapshot 'bad_snapshot'" in r.stderr
    assert "column 'id': missing required key 'description'" in r.stderr


def test_cli_rejects_name_in_required() -> None:
    r = _invoke("--required", "name", _f("columns_clean.yml"))
    assert r.returncode == 2
    assert "do not list 'name'" in r.stderr


def test_cli_skips_no_snapshots_section() -> None:
    r = _invoke(_shared("sources_only.yml"))
    assert r.returncode == 0


def test_cli_skips_empty_file() -> None:
    r = _invoke(_shared("empty.yml"))
    assert r.returncode == 0
