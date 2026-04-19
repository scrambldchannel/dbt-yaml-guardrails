"""Tests for exposure-allowed-keys CLI (specs/hook-families/allowed-keys.md)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_FIXTURES_YAML = _REPO_ROOT / "tests" / "fixtures" / "yaml"


def _f(name: str) -> str:
    return str(_FIXTURES_YAML / name)


def _invoke(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "dbt_yaml_guardrails.hook_families.allowed_keys.exposure_allowed_keys",
            *args,
        ],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
    )


def test_cli_passes_clean_exposures() -> None:
    r = _invoke(_f("exposures_two.yml"))
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_disallowed_key() -> None:
    r = _invoke(_f("exposures_disallowed_key.yml"))
    assert r.returncode == 1
    assert "disallowed key 'not_in_allowlist'" in r.stderr
    assert "exposure 'x'" in r.stderr


def test_cli_missing_required() -> None:
    r = _invoke("--required", "description", _f("exposures_name_only.yml"))
    assert r.returncode == 1
    assert "missing required key 'description'" in r.stderr


def test_cli_skips_no_exposures_section() -> None:
    r = _invoke(_f("sources_only.yml"))
    assert r.returncode == 0


def test_cli_skips_empty_file() -> None:
    r = _invoke(_f("empty.yml"))
    assert r.returncode == 0


def test_cli_rejects_name_in_required() -> None:
    r = _invoke("--required", "name", _f("exposures_name_only.yml"))
    assert r.returncode == 2
    assert "do not list 'name'" in r.stderr


def test_cli_forbidden_removes_otherwise_allowed_key() -> None:
    r = _invoke("--forbidden", "config", _f("exposures_config_only.yml"))
    assert r.returncode == 1
    assert "forbidden key 'config'" in r.stderr
    assert "exposure 'with_config'" in r.stderr


def test_cli_meta_legacy_message() -> None:
    r = _invoke(_f("exposures_with_legacy_meta.yml"))
    assert r.returncode == 1
    assert "exposure 'with_meta'" in r.stderr
    assert "Use `config.meta` instead of top-level `meta`." in r.stderr


def test_cli_tags_legacy_message() -> None:
    r = _invoke(_f("exposures_with_legacy_tags.yml"))
    assert r.returncode == 1
    assert "exposure 'with_tags'" in r.stderr
    assert "unless your dbt version documents an exception" in r.stderr
