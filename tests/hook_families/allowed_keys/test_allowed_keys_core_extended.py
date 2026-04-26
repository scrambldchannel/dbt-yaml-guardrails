"""In-process ``collect_violation_rows*`` against real YAML (load → extract → nested checks).

CLI tests use subprocess, so they do not exercise ``allowed_keys_core`` in the test process;
these are the high-value integration checks for the *-allowed-keys pipeline.
``test_allowed_keys_core.py`` covers :func:`violations_for_entries` row shapes (including
``--required`` / ``--forbidden``).
"""

from __future__ import annotations

from pathlib import Path

from dbt_yaml_guardrails.hook_families.allowed_config_keys.resource_config_keys import (
    MODEL_CONFIG_ALLOWED_KEYS,
    SOURCE_CONFIG_ALLOWED_KEYS,
)
from dbt_yaml_guardrails.hook_families.allowed_keys import allowed_keys_core as core
from dbt_yaml_guardrails.hook_families.allowed_keys.resource_keys import (
    DBT_PROJECT_ALLOWED_KEYS,
    DBT_PROJECT_LEGACY_KEY_MESSAGES,
    MODEL_ALLOWED_KEYS,
    MODEL_COLUMN_ALLOWED_KEYS,
    SOURCE_ALLOWED_KEYS,
    SOURCE_TABLE_ALLOWED_KEYS,
    SOURCE_TABLE_COLUMN_ALLOWED_KEYS,
)
from dbt_yaml_guardrails.yaml_handling import (
    ModelEntriesSkip,
    ParseError,
    ParseSuccess,
    SourceEntriesSkip,
    extract_model_entries,
    extract_source_entries,
    iter_model_entries,
    iter_source_entries,
)

_FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "yaml" / "allowed_keys"


def _extract_model(
    success: ParseSuccess,
) -> ParseError | dict[str, dict[str, object]] | None:
    r = extract_model_entries(success)
    if isinstance(r, ModelEntriesSkip):
        return None
    if isinstance(r, ParseError):
        return r
    return r.by_name


def _extract_source(
    success: ParseSuccess,
) -> ParseError | dict[str, dict[str, object]] | None:
    r = extract_source_entries(success)
    if isinstance(r, SourceEntriesSkip):
        return None
    if isinstance(r, ParseError):
        return r
    return r.by_name


def _collect_models(
    files: list[Path],
    *,
    check_config: bool = True,
    config_allowed: frozenset[str] | None = MODEL_CONFIG_ALLOWED_KEYS,
    check_columns: bool = True,
    column_allowed: frozenset[str] | None = MODEL_COLUMN_ALLOWED_KEYS,
) -> list[core.ViolationRow]:
    return core.collect_violation_rows_for_property_paths(
        files,
        set(),
        set(),
        MODEL_ALLOWED_KEYS,
        extract_by_name=_extract_model,
        iter_entries=iter_model_entries,
        check_config=check_config,
        config_allowed=config_allowed,
        check_columns=check_columns,
        column_allowed=column_allowed,
        resource_label="model",
    )


def test_collect_property_yaml_models_top_level_disallowed() -> None:
    p = _FIXTURES / "models" / "models_disallowed_key.yml"
    rows = _collect_models(
        [p],
        check_config=False,
        config_allowed=None,
        check_columns=False,
        column_allowed=None,
    )
    assert any("disallowed" in r[1] for r in rows)


def test_collect_property_yaml_models_nested_config_disallowed(tmp_path: Path) -> None:
    f = tmp_path / "m.yml"
    f.write_text(
        "version: 2\n"
        "models:\n"
        "  - name: n\n"
        "    config:\n"
        "      disallowed_config_key: 1\n",
        encoding="utf-8",
    )
    rows = _collect_models([f])
    assert any("disallowed_config_key" in r[1] for r in rows)


def test_collect_property_yaml_models_column_disallowed() -> None:
    p = _FIXTURES / "models" / "models_disallowed_column_key.yml"
    rows = _collect_models(
        [p],
        check_config=False,
        config_allowed=None,
        check_columns=True,
        column_allowed=MODEL_COLUMN_ALLOWED_KEYS,
    )
    assert any("column 'id'" in r[1] and "bad_column_key" in r[1] for r in rows)


def test_collect_dbt_project_top_level_disallowed() -> None:
    p = _FIXTURES / "dbt_project" / "dbt_project_disallowed_key.yml"
    rows = core.collect_violation_rows_for_dbt_project_paths(
        [p],
        set(),
        set(),
        DBT_PROJECT_ALLOWED_KEYS,
        legacy_key_messages=DBT_PROJECT_LEGACY_KEY_MESSAGES,
    )
    assert any("not_in_allowlist" in r[1] for r in rows)


def test_collect_property_yaml_sources_table_and_table_config() -> None:
    t_dis = _FIXTURES / "sources" / "sources_table_disallowed_key.yml"
    t_cfg = _FIXTURES / "sources" / "sources_table_config_bad.yml"
    rows = core.collect_violation_rows_for_property_paths(
        [t_dis],
        set(),
        set(),
        SOURCE_ALLOWED_KEYS,
        extract_by_name=_extract_source,
        iter_entries=iter_source_entries,
        check_config=True,
        config_allowed=SOURCE_CONFIG_ALLOWED_KEYS,
        resource_label="source",
        check_source_tables=True,
        source_table_allowed=SOURCE_TABLE_ALLOWED_KEYS,
        check_source_table_columns=True,
        source_table_column_allowed=SOURCE_TABLE_COLUMN_ALLOWED_KEYS,
    )
    assert any("not_in_allowlist" in r[1] for r in rows)
    rows_cfg = core.collect_violation_rows_for_property_paths(
        [t_cfg],
        set(),
        set(),
        SOURCE_ALLOWED_KEYS,
        extract_by_name=_extract_source,
        iter_entries=iter_source_entries,
        check_config=True,
        config_allowed=SOURCE_CONFIG_ALLOWED_KEYS,
        resource_label="source",
        check_source_tables=True,
        source_table_allowed=SOURCE_TABLE_ALLOWED_KEYS,
    )
    assert any("not_a_source_config_key" in r[0][2] for r in rows_cfg)
