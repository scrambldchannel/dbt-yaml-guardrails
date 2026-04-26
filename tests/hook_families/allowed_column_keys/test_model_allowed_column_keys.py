"""Tests for model-allowed-column-keys CLI (specs/hook-families/allowed-column-keys.md)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_YAML = _REPO_ROOT / "tests" / "fixtures" / "yaml"
_COL = _YAML / "allowed_column_keys"
_SHARED = _YAML / "shared"


def _f(name: str) -> str:
    return str(_COL / "models" / name)


def _shared(name: str) -> str:
    return str(_SHARED / name)


def _invoke(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "dbt_yaml_guardrails.hook_families.allowed_column_keys.model_allowed_column_keys",
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
    assert "model 'bad_model'" in r.stderr
    assert "column 'id': disallowed key 'bad_column_key'" in r.stderr


def test_cli_legacy_tests_column_key() -> None:
    r = _invoke(_f("columns_legacy_tests.yml"))
    assert r.returncode == 1
    assert "model 'legacy_model'" in r.stderr
    assert "column 'id': Rename to `data_tests`" in r.stderr


def test_cli_required_missing() -> None:
    r = _invoke("--required", "description", _f("columns_missing_required.yml"))
    assert r.returncode == 1
    assert "model 'no_desc_model'" in r.stderr
    assert "column 'id': missing required key 'description'" in r.stderr


def test_cli_required_present_passes() -> None:
    r = _invoke("--required", "description", _f("columns_clean.yml"))
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_forbidden() -> None:
    r = _invoke("--forbidden", "meta", _f("columns_forbidden.yml"))
    assert r.returncode == 1
    assert "model 'forbidden_model'" in r.stderr
    assert "column 'id': forbidden key 'meta'" in r.stderr


def test_cli_rejects_name_in_required() -> None:
    r = _invoke("--required", "name", _f("columns_clean.yml"))
    assert r.returncode == 2
    assert "do not list 'name'" in r.stderr


def test_cli_null_columns_is_shape_error() -> None:
    r = _invoke(_f("columns_null.yml"))
    assert r.returncode == 1
    assert "columns must be a list" in r.stderr


def test_cli_nameless_column_is_shape_error() -> None:
    r = _invoke(_f("columns_nameless.yml"))
    assert r.returncode == 1
    assert "column at index 0 is missing 'name'" in r.stderr


def test_cli_skips_entry_with_no_columns_key() -> None:
    r = _invoke("--required", "description", _f("columns_no_columns_key.yml"))
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_skips_no_models_section() -> None:
    r = _invoke(_shared("sources_only.yml"))
    assert r.returncode == 0


def test_cli_skips_empty_file() -> None:
    r = _invoke(_shared("empty.yml"))
    assert r.returncode == 0


def test_cli_fix_legacy_yaml_rewrites_column_tests(tmp_path: Path) -> None:
    src = _COL / "models" / "columns_legacy_tests.yml"
    p = tmp_path / "c.yml"
    p.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    r = _invoke("--fix-legacy-yaml", "true", str(p))
    assert r.returncode == 0, r.stderr
    out = p.read_text(encoding="utf-8")
    assert "data_tests" in out
    assert "        tests:" not in out
