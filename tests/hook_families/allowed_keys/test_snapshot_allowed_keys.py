"""Tests for snapshot-allowed-keys CLI (specs/hook-families/allowed-keys.md)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_YAML = _REPO_ROOT / "tests" / "fixtures" / "yaml"
_ALLOWED = _YAML / "allowed_keys"
_SHARED = _YAML / "shared"


def _f(name: str) -> str:
    return str(_ALLOWED / "snapshots" / name)


def _shared(name: str) -> str:
    return str(_SHARED / name)


def _invoke(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "dbt_yaml_guardrails.hook_families.allowed_keys.snapshot_allowed_keys",
            *args,
        ],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
    )


def test_cli_passes_clean_snapshots() -> None:
    r = _invoke(_f("snapshots_two.yml"))
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_disallowed_key() -> None:
    r = _invoke(_f("snapshots_disallowed_key.yml"))
    assert r.returncode == 1
    assert "disallowed key 'not_in_allowlist'" in r.stderr
    assert "snapshot 'x'" in r.stderr


def test_cli_missing_required() -> None:
    r = _invoke("--required", "description", _f("snapshots_name_only.yml"))
    assert r.returncode == 1
    assert "missing required key 'description'" in r.stderr


def test_cli_skips_no_snapshots_section() -> None:
    r = _invoke(_shared("sources_only.yml"))
    assert r.returncode == 0


def test_cli_skips_empty_file() -> None:
    r = _invoke(_shared("empty.yml"))
    assert r.returncode == 0


def test_cli_rejects_name_in_required() -> None:
    r = _invoke("--required", "name", _f("snapshots_name_only.yml"))
    assert r.returncode == 2
    assert "do not list 'name'" in r.stderr


def test_cli_forbidden_removes_otherwise_allowed_key() -> None:
    r = _invoke("--forbidden", "config", _f("snapshots_config_only.yml"))
    assert r.returncode == 1
    assert "forbidden key 'config'" in r.stderr
    assert "snapshot 'with_config'" in r.stderr


def test_cli_meta_legacy_message() -> None:
    r = _invoke(_f("snapshots_with_legacy_meta.yml"))
    assert r.returncode == 1
    assert "snapshot 'with_meta'" in r.stderr
    assert "Use `config.meta` instead of top-level `meta`." in r.stderr


# --- --check-columns (default true) ---


def test_cli_check_columns_default_passes_clean_columns() -> None:
    r = _invoke(_f("snapshots_clean_columns.yml"))
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_check_columns_default_flags_disallowed_column_key() -> None:
    r = _invoke(_f("snapshots_disallowed_column_key.yml"))
    assert r.returncode == 1
    assert "snapshot 'snap_x'" in r.stderr
    assert "column 'id': disallowed key 'bad_col_key'" in r.stderr


def test_cli_check_columns_false_ignores_bad_column_key() -> None:
    r = _invoke("--check-columns", "false", _f("snapshots_disallowed_column_key.yml"))
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_check_columns_nameless_column_is_shape_error() -> None:
    r = _invoke(_f("snapshots_nameless_column.yml"))
    assert r.returncode == 1
    assert "column at index 0 is missing 'name'" in r.stderr
