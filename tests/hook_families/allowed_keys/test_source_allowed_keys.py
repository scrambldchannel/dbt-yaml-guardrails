"""Tests for source-allowed-keys CLI (specs/hook-families/allowed-keys.md)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_YAML = _REPO_ROOT / "tests" / "fixtures" / "yaml"
_ALLOWED = _YAML / "allowed_keys"
_ALLOWED_CFG = _YAML / "allowed_config_keys"
_SHARED = _YAML / "shared"


def _f(name: str) -> str:
    return str(_ALLOWED / "sources" / name)


def _cfg(name: str) -> str:
    return str(_ALLOWED_CFG / "sources" / name)


def _shared(name: str) -> str:
    return str(_SHARED / name)


def _invoke(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "dbt_yaml_guardrails.hook_families.allowed_keys.source_allowed_keys",
            *args,
        ],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
    )


def test_cli_passes_clean_sources() -> None:
    r = _invoke(_f("sources_two.yml"))
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_disallowed_key() -> None:
    r = _invoke(_f("sources_disallowed_key.yml"))
    assert r.returncode == 1
    assert "disallowed key 'not_in_allowlist'" in r.stderr
    assert "source 'x'" in r.stderr


def test_cli_missing_required() -> None:
    r = _invoke("--required", "description", _f("sources_name_only.yml"))
    assert r.returncode == 1
    assert "missing required key 'description'" in r.stderr


def test_cli_skips_no_sources_section() -> None:
    r = _invoke(_shared("minimal_version2.yml"))
    assert r.returncode == 0


def test_cli_skips_empty_file() -> None:
    r = _invoke(_shared("empty.yml"))
    assert r.returncode == 0


def test_cli_rejects_name_in_required() -> None:
    r = _invoke("--required", "name", _f("sources_name_only.yml"))
    assert r.returncode == 2
    assert "do not list 'name'" in r.stderr


def test_cli_forbidden_removes_otherwise_allowed_key() -> None:
    r = _invoke("--forbidden", "config", _f("sources_config_only.yml"))
    assert r.returncode == 1
    assert "forbidden key 'config'" in r.stderr
    assert "source 'with_config'" in r.stderr


def test_cli_meta_legacy_message() -> None:
    r = _invoke(_f("sources_with_legacy_meta.yml"))
    assert r.returncode == 1
    assert "source 'with_meta'" in r.stderr
    assert "Use `config.meta` instead of top-level `meta`." in r.stderr


# --- --check-config (default true) ---


def test_cli_check_config_default_flags_bad_config_key() -> None:
    r = _invoke(_cfg("source_config_bad.yml"))
    assert r.returncode == 1
    assert "config: disallowed key" in r.stderr


def test_cli_check_config_false_ignores_bad_config_key() -> None:
    r = _invoke("--check-config", "false", _cfg("source_config_bad.yml"))
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_check_config_default_passes_clean_config() -> None:
    r = _invoke(_cfg("source_config_clean.yml"))
    assert r.returncode == 0
    assert r.stderr == ""


# --- nested sources: ... → tables: / columns: ---


def test_cli_passes_with_tables_and_columns() -> None:
    r = _invoke(_f("sources_with_tables_and_columns.yml"))
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_table_disallowed_key() -> None:
    r = _invoke(_f("sources_table_disallowed_key.yml"))
    assert r.returncode == 1
    assert "source 'raw'" in r.stderr
    assert "table 't1'" in r.stderr
    assert "disallowed key 'not_in_allowlist'" in r.stderr


def test_cli_column_disallowed_key() -> None:
    r = _invoke(_f("sources_column_disallowed_key.yml"))
    assert r.returncode == 1
    assert "source 'raw'" in r.stderr
    assert "table 't1'" in r.stderr
    assert "column 'id'" in r.stderr
    assert "disallowed key 'not_a_valid_column_key'" in r.stderr


def test_cli_check_source_tables_false_needs_check_source_table_columns_false() -> None:
    r = _invoke(
        "--check-source-tables",
        "false",
        _f("sources_with_tables_and_columns.yml"),
    )
    assert r.returncode == 2
    assert "incompatible" in r.stderr

    r2 = _invoke(
        "--check-source-tables",
        "false",
        "--check-source-table-columns",
        "false",
        _f("sources_with_tables_and_columns.yml"),
    )
    assert r2.returncode == 0
    assert r2.stderr == ""


def test_cli_check_source_table_columns_false_skips_column_keys() -> None:
    r = _invoke(
        "--check-source-table-columns",
        "false",
        _f("sources_column_disallowed_key.yml"),
    )
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_table_config_bad_key_when_check_config() -> None:
    r = _invoke(_f("sources_table_config_bad.yml"))
    assert r.returncode == 1
    assert "source 'raw'" in r.stderr
    assert "table 't1': config: disallowed key" in r.stderr


def test_cli_table_config_ignored_when_check_config_false() -> None:
    r = _invoke(
        "--check-config",
        "false",
        _f("sources_table_config_bad.yml"),
    )
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_column_tests_legacy_message() -> None:
    r = _invoke(_f("sources_column_tests_legacy.yml"))
    assert r.returncode == 1
    assert "column 'id'" in r.stderr
    assert "Rename to `data_tests`" in r.stderr


def test_cli_table_tests_legacy_message() -> None:
    r = _invoke(_f("sources_table_tests_legacy.yml"))
    assert r.returncode == 1
    assert "table 't1'" in r.stderr
    assert "Rename to `data_tests`" in r.stderr
