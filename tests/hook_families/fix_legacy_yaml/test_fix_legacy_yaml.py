"""Tests for ``fix-legacy-yaml`` (``specs/hook-families/fix-legacy-yaml.md``)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_YAML = _REPO_ROOT / "tests" / "fixtures" / "yaml" / "fix_legacy_yaml"
_MODULE = "dbt_yaml_guardrails.hook_families.fix_legacy_yaml.fix_legacy_yaml"


def _f(name: str) -> str:
    return str(_YAML / name)


def _invoke(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", _MODULE, *args],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
    )


def test_check_clean_no_tests_key() -> None:
    p = (
        _REPO_ROOT
        / "tests"
        / "fixtures"
        / "yaml"
        / "allowed_keys"
        / "models"
        / "models_name_only.yml"
    )
    r = _invoke(str(p))
    assert r.returncode == 0
    assert r.stderr == ""


def test_check_fails_when_tests_present_top_level() -> None:
    r = _invoke(_f("model_tests_top.yml"))
    assert r.returncode == 1


def test_write_renames_model_top_level(tmp_path: Path) -> None:
    src = Path(_f("model_tests_top.yml"))
    p = tmp_path / "t.yml"
    p.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    r = _invoke("--write", str(p))
    assert r.returncode == 0, r.stderr
    out = p.read_text(encoding="utf-8")
    assert "data_tests:" in out
    assert "\n    tests:" not in out  # legacy key only; not substring of data_tests
    r2 = _invoke(str(p))
    assert r2.returncode == 0
    assert r2.stderr == ""


def test_write_renames_column_level(tmp_path: Path) -> None:
    src = Path(_f("model_column_tests.yml"))
    p = tmp_path / "c.yml"
    p.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    r = _invoke("--write", str(p))
    assert r.returncode == 0
    out = p.read_text(encoding="utf-8")
    assert "data_tests" in out
    assert "    tests:" not in out


def test_check_conflict_both_keys() -> None:
    r = _invoke(_f("model_both_keys.yml"))
    assert r.returncode == 1
    assert "both present" in r.stderr or "skipping" in r.stderr


def test_key_order_preserved_model(tmp_path: Path) -> None:
    p = tmp_path / "k.yml"
    p.write_text(
        "version: 2\n"
        "models:\n"
        "  - name: a\n"
        "    z_last: 1\n"
        "    tests: []\n"
        "    b_mid: 2\n",
        encoding="utf-8",
    )
    r = _invoke("--write", str(p))
    assert r.returncode == 0, r.stderr
    lines = [
        ln.rstrip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()
    ]
    keys_line = [
        ln
        for ln in lines
        if "name:" in ln or "z_last" in ln or "data_tests" in ln or "b_mid" in ln
    ]
    i_z = next(i for i, ln in enumerate(keys_line) if "z_last" in ln)
    i_d = next(i for i, ln in enumerate(keys_line) if "data_tests" in ln)
    i_b = next(i for i, ln in enumerate(keys_line) if "b_mid" in ln)
    assert i_z < i_d < i_b
