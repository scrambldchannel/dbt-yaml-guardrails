"""Tests for dbt-project-allowed-keys CLI (specs/hook-families/allowed-keys.md §8)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_YAML = _REPO_ROOT / "tests" / "fixtures" / "yaml"
_ALLOWED = _YAML / "allowed_keys"
_SHARED = _YAML / "shared"


def _f(name: str) -> str:
    return str(_ALLOWED / "dbt_project" / name)


def _shared(name: str) -> str:
    return str(_SHARED / name)


def _invoke(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "dbt_yaml_guardrails.hook_families.allowed_keys.dbt_project_allowed_keys",
            *args,
        ],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
    )


def test_cli_passes_clean() -> None:
    r = _invoke(_f("dbt_project_clean.yml"))
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_disallowed_key() -> None:
    r = _invoke(_f("dbt_project_disallowed_key.yml"))
    assert r.returncode == 1
    assert "project: disallowed key 'not_in_allowlist'" in r.stderr


def test_cli_missing_required() -> None:
    r = _invoke("--required", "profile", _f("dbt_project_name_only.yml"))
    assert r.returncode == 1
    assert "project: missing required key 'profile'" in r.stderr


def test_cli_skips_empty_file() -> None:
    r = _invoke(_shared("empty.yml"))
    assert r.returncode == 0


def test_cli_required_name_allowed() -> None:
    """Unlike list-resource hooks, ``--required name`` is valid (spec)."""
    r = _invoke("--required", "name", _f("dbt_project_name_only.yml"))
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_forbidden_vars() -> None:
    r = _invoke("--forbidden", "vars", _f("dbt_project_with_vars.yml"))
    assert r.returncode == 1
    assert "project: forbidden key 'vars'" in r.stderr


def test_cli_does_not_accept_fix_legacy_yaml() -> None:
    r = _invoke("--fix-legacy-yaml", "true", _f("dbt_project_clean.yml"))
    assert r.returncode == 2
    combined = r.stdout + r.stderr
    assert "No such option" in combined or "fix-legacy-yaml" in combined
