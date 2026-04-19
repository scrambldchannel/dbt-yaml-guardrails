"""Tests for model-allowed-keys CLI (specs/hooks.md)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "yaml"


def _f(name: str) -> str:
    return str(FIXTURES / name)


def _invoke(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "dbt_yaml_guardrails.model_allowed_keys", *args],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
    )


def test_cli_passes_clean_models() -> None:
    r = _invoke(_f("models_two.yml"))
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_disallowed_key() -> None:
    r = _invoke(_f("models_disallowed_key.yml"))
    assert r.returncode == 1
    assert "disallowed key 'not_in_allowlist'" in r.stderr
    assert "model 'x'" in r.stderr


def test_cli_missing_required() -> None:
    r = _invoke("--required", "description", _f("models_name_only.yml"))
    assert r.returncode == 1
    assert "missing required key 'description'" in r.stderr


def test_cli_skips_no_models_section() -> None:
    r = _invoke(_f("sources_only.yml"))
    assert r.returncode == 0


def test_cli_skips_empty_file() -> None:
    r = _invoke(_f("empty.yml"))
    assert r.returncode == 0


def test_cli_rejects_name_in_required() -> None:
    r = _invoke("--required", "name", _f("models_name_only.yml"))
    assert r.returncode == 2
    assert "do not list 'name'" in r.stderr


def test_cli_strict_default_rejects_unknown_in_allowlist() -> None:
    """--strict is on by default; --allowed must not extend beyond resource-keys."""
    r = _invoke(
        "--allowed",
        "name,description,extra_bad",
        _f("models_name_only.yml"),
    )
    assert r.returncode == 2
    assert "extra_bad" in r.stderr


def test_cli_strict_false_allows_extra_keys_in_allowlist() -> None:
    allowed = (
        "name,description,columns,data_tests,versions,latest_version,version,"
        "constraints,docs,config,tags"
    )
    r = _invoke(
        "--strict",
        "false",
        "--allowed",
        allowed,
        _f("models_with_tags.yml"),
    )
    assert r.returncode == 0
    assert r.stderr == ""
