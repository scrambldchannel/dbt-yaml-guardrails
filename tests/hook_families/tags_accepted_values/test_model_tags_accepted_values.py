"""Tests for model-tags-accepted-values CLI (specs/hook-families/tags-accepted-values.md)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_YAML = _REPO_ROOT / "tests" / "fixtures" / "yaml"
_MODELS = _YAML / "tags_accepted_values" / "models"
_SHARED = _YAML / "shared"


def _m(name: str) -> str:
    return str(_MODELS / name)


def _shared(name: str) -> str:
    return str(_SHARED / name)


def _invoke(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "dbt_yaml_guardrails.hook_families.tags_accepted_values.model_tags_accepted_values",
            *args,
        ],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
    )


def test_cli_passes_string_tag_ok() -> None:
    r = _invoke("--values", "nightly,finance", _m("tags_string_ok.yml"))
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_passes_list_tags_ok() -> None:
    r = _invoke("--values", "nightly,finance", _m("tags_list_ok.yml"))
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_rejects_disallowed_tag() -> None:
    r = _invoke("--values", "nightly,finance", _m("tags_wrong.yml"))
    assert r.returncode == 1
    assert "model 'm'" in r.stderr
    assert "not an allowed value" in r.stderr


def test_cli_missing_config_passes() -> None:
    r = _invoke("--values", "nightly", _m("tags_no_config.yml"))
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_config_without_tags_passes() -> None:
    r = _invoke("--values", "nightly", _m("tags_config_no_tags.yml"))
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_wrong_leaf_type() -> None:
    r = _invoke("--values", "nightly", _m("tags_wrong_type.yml"))
    assert r.returncode == 1
    assert "must be a string or a sequence of strings" in r.stderr


def test_cli_empty_values_exit_2() -> None:
    r = _invoke("--values", ",", _m("tags_string_ok.yml"))
    assert r.returncode == 2
    assert "--values" in r.stderr


def test_cli_skips_no_models_section() -> None:
    r = _invoke("--values", "a", _shared("sources_only.yml"))
    assert r.returncode == 0


def test_cli_skips_empty_file() -> None:
    r = _invoke("--values", "a", _shared("empty.yml"))
    assert r.returncode == 0
