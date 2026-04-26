"""Legacy rewrite scenarios: ``specs/hook-families/fix-legacy-yaml.md`` (v1 and v2).

Fixtures live under ``tests/fixtures/yaml/fix_legacy_yaml/`` so scenarios stay readable
YAML and load the same way as production (``load_property_yaml_roundtrip``).
"""

from __future__ import annotations

from pathlib import Path


from dbt_yaml_guardrails.hook_families.fix_legacy_yaml import legacy_rewrite_core as lrc
from dbt_yaml_guardrails.yaml_handling import ParseError, ParseSkip

_FIX = Path(__file__).resolve().parents[2] / "fixtures" / "yaml" / "fix_legacy_yaml"


def _rt_load(path: Path) -> object:
    r = lrc.load_property_yaml_roundtrip(path)
    assert not isinstance(r, (ParseError, ParseSkip))
    return r


# --- v1: ``tests`` → ``data_tests`` ---


def test_v1_renames_top_level_tests_from_file() -> None:
    p = _FIX / "model_tests_top.yml"
    n, c = lrc.rewrite_tests_to_data_tests_v1(_rt_load(p), p)
    assert n == 1 and c == []


def test_v1_conflict_resource_has_tests_and_data_tests_from_file() -> None:
    p = _FIX / "model_both_keys.yml"
    n, c = lrc.rewrite_tests_to_data_tests_v1(_rt_load(p), p)
    assert n == 0 and len(c) == 1 and "both present" in c[0]


def test_v1_renames_column_tests_from_file() -> None:
    p = _FIX / "model_column_tests.yml"
    n, c = lrc.rewrite_tests_to_data_tests_v1(_rt_load(p), p)
    assert n == 1 and c == []


def test_v1_column_conflict_both_keys_from_file() -> None:
    p = _FIX / "model_column_tests_conflict_both_keys.yml"
    n, c = lrc.rewrite_tests_to_data_tests_v1(_rt_load(p), p)
    assert n == 0
    assert any("column 'id'" in m and "both present" in m for m in c)


# --- v2: top-level ``meta`` / ``tags`` → ``config`` ---


def test_v2_moves_tags_into_config_from_file() -> None:
    p = _FIX / "model_v2_top_level_tags_only.yml"
    root = _rt_load(p)
    n, c = lrc.rewrite_top_level_meta_tags_to_config(root, p)
    assert c == [] and n == 1
    m0 = root["models"][0]  # type: ignore[index]
    assert m0["config"]["tags"] == ["a"]  # type: ignore[index]
    assert "tags" not in m0  # type: ignore[operator]


def test_v2_merges_meta_into_existing_config_from_file() -> None:
    p = _FIX / "model_v2_top_level_meta_into_config.yml"
    root = _rt_load(p)
    n, c = lrc.rewrite_top_level_meta_tags_to_config(root, p)
    assert c == [] and n == 1
    m0 = root["models"][0]  # type: ignore[index]
    assert m0["config"]["meta"]["k"] == "v"  # type: ignore[index]
    assert "meta" not in m0  # type: ignore[operator]


def test_v2_rejects_config_null_with_tags_from_file() -> None:
    p = _FIX / "model_v2_config_null_with_tags.yml"
    n, c = lrc.rewrite_top_level_meta_tags_to_config(_rt_load(p), p)
    assert n == 0
    assert any("not a mapping" in m for m in c)


def test_v2_rejects_top_level_and_config_key_collision_from_file() -> None:
    p = _FIX / "model_v2_tags_top_and_config.yml"
    n, c = lrc.rewrite_top_level_meta_tags_to_config(_rt_load(p), p)
    assert n == 0
    assert any("both present" in m for m in c)


# --- round-trip write (end of fix pass) ---


def test_write_roundtrip_serializes_parsed_root(tmp_path: Path) -> None:
    p = _FIX / "model_tests_top.yml"
    root = lrc.load_property_yaml_roundtrip(p)
    assert not isinstance(root, (ParseError, ParseSkip))
    out = tmp_path / "out.yml"
    assert lrc.write_roundtrip(out, root) is None
    assert "models" in out.read_text(encoding="utf-8")
