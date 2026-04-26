"""Tests for model-allowed-keys CLI (specs/hook-families/allowed-keys.md)."""

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
    return str(_ALLOWED / "models" / name)


def _cfg(name: str) -> str:
    return str(_ALLOWED_CFG / "models" / name)


def _shared(name: str) -> str:
    return str(_SHARED / name)


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
    r = _invoke(_shared("sources_only.yml"))
    assert r.returncode == 0


def test_cli_skips_empty_file() -> None:
    r = _invoke(_shared("empty.yml"))
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


# --- --check-config (default true) ---


def test_cli_check_config_default_flags_bad_config_key() -> None:
    r = _invoke(_cfg("config_disallowed.yml"))
    assert r.returncode == 1
    assert "model 'bad'" in r.stderr
    assert "config: disallowed key 'not_a_real_dbt_config_key'" in r.stderr


def test_cli_check_config_false_ignores_bad_config_key() -> None:
    r = _invoke("--check-config", "false", _cfg("config_disallowed.yml"))
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_check_config_default_passes_clean_config() -> None:
    r = _invoke(_cfg("config_clean.yml"))
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_check_config_config_null_is_shape_error() -> None:
    r = _invoke(_cfg("config_null.yml"))
    assert r.returncode == 1
    assert "config must be a mapping" in r.stderr


def test_cli_check_config_config_not_mapping_is_shape_error() -> None:
    r = _invoke(_cfg("config_not_mapping.yml"))
    assert r.returncode == 1
    assert "config must be a mapping" in r.stderr


def test_cli_check_config_legacy_config_key_uses_detail() -> None:
    r = _invoke(_cfg("config_legacy_on.yml"))
    assert r.returncode == 1
    assert "model 'legacy'" in r.stderr
    assert "config: Deprecated key `on`" in r.stderr


# --- --check-columns (default true) ---


def test_cli_check_columns_default_passes_clean_columns() -> None:
    r = _invoke(_f("models_clean_columns.yml"))
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_check_columns_default_flags_disallowed_column_key() -> None:
    r = _invoke(_f("models_disallowed_column_key.yml"))
    assert r.returncode == 1
    assert "model 'x'" in r.stderr
    assert "column 'id': disallowed key 'bad_column_key'" in r.stderr


def test_cli_check_columns_false_ignores_bad_column_key() -> None:
    r = _invoke("--check-columns", "false", _f("models_disallowed_column_key.yml"))
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_check_columns_legacy_tests_column_key() -> None:
    r = _invoke(_f("models_legacy_tests_column.yml"))
    assert r.returncode == 1
    assert "model 'legacy_col'" in r.stderr
    assert "column 'id': Rename to `data_tests`" in r.stderr


def test_cli_check_columns_null_columns_is_shape_error() -> None:
    r = _invoke(_f("models_null_columns.yml"))
    assert r.returncode == 1
    assert "columns must be a list" in r.stderr


def test_cli_check_columns_nameless_column_is_shape_error() -> None:
    r = _invoke(_f("models_nameless_column.yml"))
    assert r.returncode == 1
    assert "column at index 0 is missing 'name'" in r.stderr


def test_cli_fix_legacy_yaml_rewrites_tests_then_passes(tmp_path: Path) -> None:
    src = (
        _REPO_ROOT
        / "tests"
        / "fixtures"
        / "yaml"
        / "fix_legacy_yaml"
        / "model_tests_top.yml"
    )
    p = tmp_path / "m.yml"
    p.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    r = _invoke("--fix-legacy-yaml", "true", str(p))
    assert r.returncode == 0, r.stderr
    out = p.read_text(encoding="utf-8")
    assert "data_tests:" in out
    assert "    tests:" not in out


def test_cli_fix_legacy_yaml_default_false_still_reports_legacy_tests(
    tmp_path: Path,
) -> None:
    src = (
        _REPO_ROOT
        / "tests"
        / "fixtures"
        / "yaml"
        / "fix_legacy_yaml"
        / "model_tests_top.yml"
    )
    p = tmp_path / "m.yml"
    p.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    r = _invoke(str(p))
    assert r.returncode == 1
    assert "Rename to `data_tests`" in r.stderr


def test_cli_fix_legacy_yaml_second_run_idempotent(tmp_path: Path) -> None:
    src = (
        _REPO_ROOT
        / "tests"
        / "fixtures"
        / "yaml"
        / "fix_legacy_yaml"
        / "model_tests_top.yml"
    )
    p = tmp_path / "m.yml"
    p.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    r1 = _invoke("--fix-legacy-yaml", "true", str(p))
    assert r1.returncode == 0, r1.stderr
    r2 = _invoke("--fix-legacy-yaml", "true", str(p))
    assert r2.returncode == 0
    assert r2.stderr == ""


def test_cli_fix_legacy_yaml_rewrites_column_level(tmp_path: Path) -> None:
    src = (
        _REPO_ROOT
        / "tests"
        / "fixtures"
        / "yaml"
        / "fix_legacy_yaml"
        / "model_column_tests.yml"
    )
    p = tmp_path / "c.yml"
    p.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    r = _invoke("--fix-legacy-yaml", "true", str(p))
    assert r.returncode == 0, r.stderr
    out = p.read_text(encoding="utf-8")
    assert "data_tests" in out
    assert "        tests:" not in out


def test_cli_fix_legacy_yaml_conflict_both_keys_fails() -> None:
    p = str(
        _REPO_ROOT
        / "tests"
        / "fixtures"
        / "yaml"
        / "fix_legacy_yaml"
        / "model_both_keys.yml"
    )
    r = _invoke("--fix-legacy-yaml", "true", p)
    assert r.returncode == 1
    assert "both present" in r.stderr or "skipping" in r.stderr


def test_cli_fix_legacy_yaml_preserves_key_order_among_siblings(tmp_path: Path) -> None:
    p = tmp_path / "k.yml"
    p.write_text(
        "version: 2\n"
        "models:\n"
        "  - name: a\n"
        "    config: {}\n"
        "    description: d\n"
        "    tests: []\n",
        encoding="utf-8",
    )
    r = _invoke("--fix-legacy-yaml", "true", str(p))
    assert r.returncode == 0, r.stderr
    out = p.read_text(encoding="utf-8")
    i_c, i_desc, i_dt = (
        out.index("config:"),
        out.index("description:"),
        out.index("data_tests"),
    )
    assert i_c < i_desc < i_dt


def test_cli_fix_legacy_yaml_moves_top_level_tags_into_config(tmp_path: Path) -> None:
    src = (
        _REPO_ROOT
        / "tests"
        / "fixtures"
        / "yaml"
        / "allowed_keys"
        / "models"
        / "models_with_tags.yml"
    )
    p = tmp_path / "t.yml"
    p.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    r = _invoke("--fix-legacy-yaml", "true", str(p))
    assert r.returncode == 0, r.stderr
    out = p.read_text(encoding="utf-8")
    assert "config:" in out
    assert "tags:" in out
    # No top-level ``tags:`` on the model row (not at 4 spaces after ``- name``).
    assert "\n    tags:\n" not in out


def test_cli_fix_legacy_yaml_merges_tags_into_existing_config(tmp_path: Path) -> None:
    p = tmp_path / "m.yml"
    p.write_text(
        "version: 2\n"
        "models:\n"
        "  - name: m\n"
        "    config:\n"
        "      materialized: view\n"
        "    tags:\n"
        "      - nightly\n",
        encoding="utf-8",
    )
    r = _invoke("--fix-legacy-yaml", "true", str(p))
    assert r.returncode == 0, r.stderr
    out = p.read_text(encoding="utf-8")
    assert "materialized: view" in out
    assert "nightly" in out
    assert "\n    tags:\n" not in out


def test_cli_fix_legacy_yaml_creates_config_with_meta_and_tags(tmp_path: Path) -> None:
    p = tmp_path / "m.yml"
    p.write_text(
        "version: 2\n"
        "models:\n"
        "  - name: m\n"
        "    description: x\n"
        "    meta:\n"
        "      owner: team\n"
        "    tags:\n"
        "      - raw\n",
        encoding="utf-8",
    )
    r = _invoke("--fix-legacy-yaml", "true", str(p))
    assert r.returncode == 0, r.stderr
    out = p.read_text(encoding="utf-8")
    assert "owner: team" in out
    assert "raw" in out
    assert "\n    meta:\n" not in out
    assert "\n    tags:\n" not in out


def test_cli_fix_legacy_yaml_conflict_top_level_meta_and_config_meta(
    tmp_path: Path,
) -> None:
    p = tmp_path / "m.yml"
    p.write_text(
        "version: 2\n"
        "models:\n"
        "  - name: m\n"
        "    meta:\n"
        "      a: 1\n"
        "    config:\n"
        "      meta:\n"
        "        b: 2\n",
        encoding="utf-8",
    )
    r = _invoke("--fix-legacy-yaml", "true", str(p))
    assert r.returncode == 1
    assert "both present" in r.stderr or "config.meta" in r.stderr


def test_cli_fix_legacy_yaml_tags_second_run_idempotent(tmp_path: Path) -> None:
    src = (
        _REPO_ROOT
        / "tests"
        / "fixtures"
        / "yaml"
        / "allowed_keys"
        / "models"
        / "models_with_tags.yml"
    )
    p = tmp_path / "t.yml"
    p.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    r1 = _invoke("--fix-legacy-yaml", "true", str(p))
    assert r1.returncode == 0, r1.stderr
    r2 = _invoke("--fix-legacy-yaml", "true", str(p))
    assert r2.returncode == 0
    assert r2.stderr == ""
