"""Tests for model-allowed-config-keys CLI (specs/hook-families/allowed-config-keys.md)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_YAML = _REPO_ROOT / "tests" / "fixtures" / "yaml"
_CFG = _YAML / "allowed_config_keys"
_SHARED = _YAML / "shared"


def _f(name: str) -> str:
    return str(_CFG / "models" / name)


def _shared(name: str) -> str:
    return str(_SHARED / name)


def _invoke(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "dbt_yaml_guardrails.hook_families.allowed_config_keys.model_allowed_config_keys",
            *args,
        ],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
    )


def test_cli_passes_clean_config() -> None:
    r = _invoke(_f("config_clean.yml"))
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_disallowed_config_key() -> None:
    r = _invoke(_f("config_disallowed.yml"))
    assert r.returncode == 1
    assert "disallowed config key 'not_a_real_dbt_config_key'" in r.stderr
    assert "model 'bad'" in r.stderr


def test_cli_config_null_is_error() -> None:
    r = _invoke(_f("config_null.yml"))
    assert r.returncode == 1
    assert "config must be a mapping, not null" in r.stderr


def test_cli_config_not_mapping_is_error() -> None:
    r = _invoke(_f("config_not_mapping.yml"))
    assert r.returncode == 1
    assert "config must be a mapping, got str" in r.stderr


def test_cli_legacy_on_key_message() -> None:
    r = _invoke(_f("config_legacy_on.yml"))
    assert r.returncode == 1
    assert "model 'legacy'" in r.stderr
    assert "Deprecated key `on` under config" in r.stderr


def test_cli_skips_no_models_section() -> None:
    r = _invoke(_shared("sources_only.yml"))
    assert r.returncode == 0


def test_cli_skips_empty_file() -> None:
    r = _invoke(_shared("empty.yml"))
    assert r.returncode == 0


def test_cli_forbidden() -> None:
    r = _invoke("--forbidden", "materialized", _f("config_forbidden.yml"))
    assert r.returncode == 1
    assert "forbidden config key 'materialized'" in r.stderr
    assert "model 'x'" in r.stderr


def test_cli_required_missing() -> None:
    r = _invoke("--required", "tags", _f("config_required.yml"))
    assert r.returncode == 1
    assert "missing required config key 'tags'" in r.stderr
    assert "model 'r'" in r.stderr
