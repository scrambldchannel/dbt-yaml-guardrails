"""Tests for catalog-allowed-keys CLI (specs/hook-families/allowed-keys.md)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_YAML = _REPO_ROOT / "tests" / "fixtures" / "yaml"
_ALLOWED = _YAML / "allowed_keys"
_SHARED = _YAML / "shared"


def _f(name: str) -> str:
    return str(_ALLOWED / "catalogs" / name)


def _shared(name: str) -> str:
    return str(_SHARED / name)


def _invoke(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "dbt_yaml_guardrails.hook_families.allowed_keys.catalog_allowed_keys",
            *args,
        ],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
    )


def test_cli_passes_clean_catalogs() -> None:
    r = _invoke(_f("catalogs_two.yml"))
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_disallowed_key() -> None:
    r = _invoke(_f("catalogs_disallowed_key.yml"))
    assert r.returncode == 1
    assert "disallowed key 'not_in_allowlist'" in r.stderr
    assert "catalog 'x'" in r.stderr


def test_cli_missing_required() -> None:
    r = _invoke("--required", "write_integrations", _f("catalogs_name_only.yml"))
    assert r.returncode == 1
    assert "missing required key 'write_integrations'" in r.stderr


def test_cli_skips_no_catalogs_section() -> None:
    r = _invoke(_shared("minimal_version2.yml"))
    assert r.returncode == 0


def test_cli_skips_empty_file() -> None:
    r = _invoke(_shared("empty.yml"))
    assert r.returncode == 0


def test_cli_rejects_name_in_required() -> None:
    r = _invoke("--required", "name", _f("catalogs_name_only.yml"))
    assert r.returncode == 2
    assert "do not list 'name'" in r.stderr


def test_cli_forbidden_removes_otherwise_allowed_key() -> None:
    r = _invoke("--forbidden", "write_integrations", _f("catalogs_write_only.yml"))
    assert r.returncode == 1
    assert "forbidden key 'write_integrations'" in r.stderr
    assert "catalog 'with_write'" in r.stderr
