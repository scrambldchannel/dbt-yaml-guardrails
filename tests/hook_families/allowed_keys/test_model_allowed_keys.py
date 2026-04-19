"""Tests for model-allowed-keys CLI (specs/hook-families/allowed-keys.md)."""

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
            "dbt_yaml_guardrails.hook_families.allowed_keys.model_allowed_keys",
            *args,
        ],
        cwd=_REPO_ROOT,
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


def test_cli_forbidden_removes_otherwise_allowed_key() -> None:
    r = _invoke("--forbidden", "config", _f("models_config_only.yml"))
    assert r.returncode == 1
    assert "forbidden key 'config'" in r.stderr
    assert "model 'with_config'" in r.stderr


def test_cli_tags_legacy_message() -> None:
    r = _invoke(_f("models_with_tags.yml"))
    assert r.returncode == 1
    assert "model 'tagged'" in r.stderr
    assert "Use `config.tags` instead of top-level `tags`." in r.stderr


def test_cli_tests_legacy_message() -> None:
    r = _invoke(_f("models_with_tests.yml"))
    assert r.returncode == 1
    assert "model 'legacy_tests'" in r.stderr
    assert "Rename to `data_tests` (legacy alias `tests` is deprecated)." in r.stderr
