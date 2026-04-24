"""Tests for specs/yaml-handling.md (load_property_yaml, extract_model_entries)."""

from __future__ import annotations

from pathlib import Path

from dbt_yaml_guardrails.yaml_handling import (
    SKIP_EMPTY_OR_WHITESPACE,
    SKIP_NO_CATALOGS_SECTION,
    SKIP_NO_EXPOSURES_SECTION,
    SKIP_NO_MACROS_SECTION,
    SKIP_NO_MODELS_SECTION,
    SKIP_NO_SEEDS_SECTION,
    SKIP_NO_SNAPSHOTS_SECTION,
    SKIP_NO_SOURCES_SECTION,
    CatalogEntriesResult,
    CatalogEntriesSkip,
    ExposureEntriesResult,
    ExposureEntriesSkip,
    MacroEntriesResult,
    MacroEntriesSkip,
    ModelEntriesResult,
    ModelEntriesSkip,
    ParseError,
    ParseSkip,
    ParseSuccess,
    SeedEntriesResult,
    SeedEntriesSkip,
    SnapshotEntriesResult,
    SnapshotEntriesSkip,
    SourceEntriesResult,
    SourceEntriesSkip,
    extract_catalog_entries,
    extract_exposure_entries,
    extract_macro_entries,
    extract_model_entries,
    extract_seed_entries,
    extract_snapshot_entries,
    extract_source_entries,
    iter_catalog_entries,
    iter_exposure_entries,
    iter_macro_entries,
    iter_model_entries,
    iter_seed_entries,
    iter_snapshot_entries,
    iter_source_entries,
    load_dbt_project_yaml,
    load_property_yaml,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "yaml"


def _f(rel: str) -> Path:
    """*rel* is under ``fixtures/yaml/`` (e.g. ``shared/empty.yml``)."""
    return FIXTURES / rel


def _success(name: str) -> ParseSuccess:
    out = load_property_yaml(_f(name))
    assert isinstance(out, ParseSuccess)
    return out


def test_empty_file_skip() -> None:
    out = load_property_yaml(_f("shared/empty.yml"))
    assert isinstance(out, ParseSkip)
    assert out.reason == SKIP_EMPTY_OR_WHITESPACE


def test_whitespace_only_skip() -> None:
    out = load_property_yaml(_f("shared/whitespace_only.yml"))
    assert isinstance(out, ParseSkip)
    assert out.reason == SKIP_EMPTY_OR_WHITESPACE


def test_invalid_utf8_error(tmp_path: Path) -> None:
    path = tmp_path / "bad.bin"
    path.write_bytes(b"\xff\xfe\x00")
    out = load_property_yaml(path)
    assert isinstance(out, ParseError)
    assert "UTF-8" in out.message


def test_bom_and_minimal_yaml_success(tmp_path: Path) -> None:
    path = tmp_path / "bom.yml"
    path.write_bytes(b"\xef\xbb\xbfversion: 2\nmodels: []\n")
    out = load_property_yaml(path)
    assert isinstance(out, ParseSuccess)
    assert out.root["version"] == 2
    assert out.root["models"] == []


def test_minimal_version2_success() -> None:
    out = load_property_yaml(_f("shared/minimal_version2.yml"))
    assert isinstance(out, ParseSuccess)
    assert out.root == {"version": 2, "models": []}


def test_no_version_success() -> None:
    out = load_property_yaml(_f("shared/no_version.yml"))
    assert isinstance(out, ParseSuccess)
    assert out.root == {"models": []}


def test_invalid_syntax_error() -> None:
    out = load_property_yaml(_f("shared/invalid_syntax.yml"))
    assert isinstance(out, ParseError)
    assert "Invalid YAML" in out.message


def test_multi_document_error() -> None:
    out = load_property_yaml(_f("shared/multi_document.yml"))
    assert isinstance(out, ParseError)
    assert "exactly one YAML document" in out.message


def test_duplicate_keys_error() -> None:
    out = load_property_yaml(_f("shared/duplicate_keys.yml"))
    assert isinstance(out, ParseError)
    assert "Invalid YAML" in out.message


def test_root_scalar_error() -> None:
    out = load_property_yaml(_f("shared/root_scalar.yml"))
    assert isinstance(out, ParseError)
    assert "mapping at the document root" in out.message


def test_bad_version_error() -> None:
    out = load_property_yaml(_f("shared/bad_version.yml"))
    assert isinstance(out, ParseError)
    assert "version must be" in out.message


def test_version_string_two_ok() -> None:
    out = load_property_yaml(_f("shared/version_string_two.yml"))
    assert isinstance(out, ParseSuccess)
    assert out.root["version"] == "2"


def test_version_float_rejected(tmp_path: Path) -> None:
    path = tmp_path / "v.yml"
    path.write_text("version: 2.0\nmodels: []\n", encoding="utf-8")
    out = load_property_yaml(path)
    assert isinstance(out, ParseError)
    assert "version must be" in out.message


# --- extract_model_entries (Phase 2 / dbt shape) ---


def test_extract_no_models_section_skip() -> None:
    out = extract_model_entries(_success("shared/sources_only.yml"))
    assert isinstance(out, ModelEntriesSkip)
    assert out.reason == SKIP_NO_MODELS_SECTION


def test_extract_models_empty_list() -> None:
    out = extract_model_entries(_success("shared/minimal_version2.yml"))
    assert isinstance(out, ModelEntriesResult)
    assert out.by_name == {}


def test_extract_models_two() -> None:
    out = extract_model_entries(_success("allowed_keys/models/models_two.yml"))
    assert isinstance(out, ModelEntriesResult)
    assert set(out.by_name) == {"alpha", "beta"}
    assert out.by_name["alpha"]["description"] == "First"
    assert out.by_name["beta"]["config"] == {"materialized": "view"}


def test_extract_duplicate_model_name() -> None:
    out = extract_model_entries(
        _success("allowed_keys/models/models_duplicate_name.yml")
    )
    assert isinstance(out, ParseError)
    assert "Duplicate model name" in out.message


def test_extract_missing_model_name() -> None:
    out = extract_model_entries(_success("allowed_keys/models/models_missing_name.yml"))
    assert isinstance(out, ParseError)
    assert "missing required key 'name'" in out.message


def test_extract_models_not_list() -> None:
    out = extract_model_entries(_success("allowed_keys/models/models_not_list.yml"))
    assert isinstance(out, ParseError)
    assert "models must be a list" in out.message


def test_extract_models_null() -> None:
    out = extract_model_entries(_success("allowed_keys/models/models_null.yml"))
    assert isinstance(out, ParseError)
    assert "not null" in out.message


def test_iter_model_entries_sorted_names() -> None:
    out = extract_model_entries(_success("allowed_keys/models/models_two.yml"))
    assert isinstance(out, ModelEntriesResult)
    names = [n for n, _ in iter_model_entries(out.by_name)]
    assert names == ["alpha", "beta"]


# --- extract_macro_entries ---


def test_extract_no_macros_section_skip() -> None:
    out = extract_macro_entries(_success("shared/sources_only.yml"))
    assert isinstance(out, MacroEntriesSkip)
    assert out.reason == SKIP_NO_MACROS_SECTION


def test_extract_macros_empty_list() -> None:
    out = extract_macro_entries(_success("allowed_keys/macros/macros_empty.yml"))
    assert isinstance(out, MacroEntriesResult)
    assert out.by_name == {}


def test_extract_macros_two() -> None:
    out = extract_macro_entries(_success("allowed_keys/macros/macros_two.yml"))
    assert isinstance(out, MacroEntriesResult)
    assert set(out.by_name) == {"my_macro", "other_macro"}
    assert out.by_name["my_macro"]["description"] == "Does something"


def test_extract_duplicate_macro_name() -> None:
    out = extract_macro_entries(
        _success("allowed_keys/macros/macros_duplicate_name.yml")
    )
    assert isinstance(out, ParseError)
    assert "Duplicate macro name" in out.message


def test_iter_macro_entries_sorted_names() -> None:
    out = extract_macro_entries(_success("allowed_keys/macros/macros_two.yml"))
    assert isinstance(out, MacroEntriesResult)
    names = [n for n, _ in iter_macro_entries(out.by_name)]
    assert names == ["my_macro", "other_macro"]


# --- extract_seed_entries ---


def test_extract_no_seeds_section_skip() -> None:
    out = extract_seed_entries(_success("shared/sources_only.yml"))
    assert isinstance(out, SeedEntriesSkip)
    assert out.reason == SKIP_NO_SEEDS_SECTION


def test_extract_seeds_empty_list() -> None:
    out = extract_seed_entries(_success("allowed_keys/seeds/seeds_empty.yml"))
    assert isinstance(out, SeedEntriesResult)
    assert out.by_name == {}


def test_extract_seeds_two() -> None:
    out = extract_seed_entries(_success("allowed_keys/seeds/seeds_two.yml"))
    assert isinstance(out, SeedEntriesResult)
    assert set(out.by_name) == {"my_seed", "other_seed"}
    assert out.by_name["my_seed"]["description"] == "Raw data"


def test_extract_duplicate_seed_name() -> None:
    out = extract_seed_entries(_success("allowed_keys/seeds/seeds_duplicate_name.yml"))
    assert isinstance(out, ParseError)
    assert "Duplicate seed name" in out.message


def test_iter_seed_entries_sorted_names() -> None:
    out = extract_seed_entries(_success("allowed_keys/seeds/seeds_two.yml"))
    assert isinstance(out, SeedEntriesResult)
    names = [n for n, _ in iter_seed_entries(out.by_name)]
    assert names == ["my_seed", "other_seed"]


# --- extract_snapshot_entries ---


def test_extract_no_snapshots_section_skip() -> None:
    out = extract_snapshot_entries(_success("shared/sources_only.yml"))
    assert isinstance(out, SnapshotEntriesSkip)
    assert out.reason == SKIP_NO_SNAPSHOTS_SECTION


def test_extract_snapshots_empty_list() -> None:
    out = extract_snapshot_entries(
        _success("allowed_keys/snapshots/snapshots_empty.yml")
    )
    assert isinstance(out, SnapshotEntriesResult)
    assert out.by_name == {}


def test_extract_snapshots_two() -> None:
    out = extract_snapshot_entries(_success("allowed_keys/snapshots/snapshots_two.yml"))
    assert isinstance(out, SnapshotEntriesResult)
    assert set(out.by_name) == {"my_snapshot", "other_snapshot"}


def test_iter_snapshot_entries_sorted_names() -> None:
    out = extract_snapshot_entries(_success("allowed_keys/snapshots/snapshots_two.yml"))
    assert isinstance(out, SnapshotEntriesResult)
    names = [n for n, _ in iter_snapshot_entries(out.by_name)]
    assert names == ["my_snapshot", "other_snapshot"]


# --- extract_exposure_entries ---


def test_extract_no_exposures_section_skip() -> None:
    out = extract_exposure_entries(_success("shared/sources_only.yml"))
    assert isinstance(out, ExposureEntriesSkip)
    assert out.reason == SKIP_NO_EXPOSURES_SECTION


def test_extract_exposures_empty_list() -> None:
    out = extract_exposure_entries(
        _success("allowed_keys/exposures/exposures_empty.yml")
    )
    assert isinstance(out, ExposureEntriesResult)
    assert out.by_name == {}


def test_extract_exposures_two() -> None:
    out = extract_exposure_entries(_success("allowed_keys/exposures/exposures_two.yml"))
    assert isinstance(out, ExposureEntriesResult)
    assert set(out.by_name) == {"dash_a", "app_b"}
    assert out.by_name["dash_a"]["type"] == "dashboard"


def test_iter_exposure_entries_sorted_names() -> None:
    out = extract_exposure_entries(_success("allowed_keys/exposures/exposures_two.yml"))
    assert isinstance(out, ExposureEntriesResult)
    names = [n for n, _ in iter_exposure_entries(out.by_name)]
    assert names == ["app_b", "dash_a"]


# --- extract_source_entries ---


def test_extract_no_sources_section_skip() -> None:
    out = extract_source_entries(_success("shared/minimal_version2.yml"))
    assert isinstance(out, SourceEntriesSkip)
    assert out.reason == SKIP_NO_SOURCES_SECTION


def test_extract_sources_empty_list() -> None:
    out = extract_source_entries(_success("allowed_keys/sources/sources_empty.yml"))
    assert isinstance(out, SourceEntriesResult)
    assert out.by_name == {}


def test_extract_sources_two() -> None:
    out = extract_source_entries(_success("allowed_keys/sources/sources_two.yml"))
    assert isinstance(out, SourceEntriesResult)
    assert set(out.by_name) == {"raw", "staging"}
    assert out.by_name["raw"]["tables"] == []
    assert out.by_name["staging"]["config"]["meta"]["team"] == "analytics"


def test_extract_duplicate_source_name() -> None:
    out = extract_source_entries(
        _success("allowed_keys/sources/sources_duplicate_name.yml")
    )
    assert isinstance(out, ParseError)
    assert "Duplicate source name" in out.message


def test_iter_source_entries_sorted_names() -> None:
    out = extract_source_entries(_success("allowed_keys/sources/sources_two.yml"))
    assert isinstance(out, SourceEntriesResult)
    names = [n for n, _ in iter_source_entries(out.by_name)]
    assert names == ["raw", "staging"]


def test_extract_sources_null() -> None:
    out = extract_source_entries(_success("allowed_keys/sources/sources_null.yml"))
    assert isinstance(out, ParseError)
    assert "not null" in out.message


# --- extract_catalog_entries ---


def test_extract_no_catalogs_section_skip() -> None:
    out = extract_catalog_entries(_success("shared/minimal_version2.yml"))
    assert isinstance(out, CatalogEntriesSkip)
    assert out.reason == SKIP_NO_CATALOGS_SECTION


def test_extract_catalogs_empty_list() -> None:
    out = extract_catalog_entries(_success("allowed_keys/catalogs/catalogs_empty.yml"))
    assert isinstance(out, CatalogEntriesResult)
    assert out.by_name == {}


def test_extract_catalogs_two() -> None:
    out = extract_catalog_entries(_success("allowed_keys/catalogs/catalogs_two.yml"))
    assert isinstance(out, CatalogEntriesResult)
    assert set(out.by_name) == {"cat_a", "cat_b"}
    assert "write_integrations" in out.by_name["cat_a"]
    assert out.by_name["cat_b"]["active_write_integration"] == "int_b"


def test_extract_duplicate_catalog_name() -> None:
    out = extract_catalog_entries(
        _success("allowed_keys/catalogs/catalogs_duplicate_name.yml")
    )
    assert isinstance(out, ParseError)
    assert "Duplicate catalog name" in out.message


def test_iter_catalog_entries_sorted_names() -> None:
    out = extract_catalog_entries(_success("allowed_keys/catalogs/catalogs_two.yml"))
    assert isinstance(out, CatalogEntriesResult)
    names = [n for n, _ in iter_catalog_entries(out.by_name)]
    assert names == ["cat_a", "cat_b"]


def test_extract_catalogs_null() -> None:
    out = extract_catalog_entries(_success("allowed_keys/catalogs/catalogs_null.yml"))
    assert isinstance(out, ParseError)
    assert "not null" in out.message


# --- load_dbt_project_yaml ---


def test_load_dbt_project_clean() -> None:
    out = load_dbt_project_yaml(_f("allowed_keys/dbt_project/dbt_project_clean.yml"))
    assert isinstance(out, ParseSuccess)
    assert out.root["name"] == "my_project"
    assert out.root["version"] == "1.0.0"


def test_load_dbt_project_accepts_version_not_two(tmp_path: Path) -> None:
    """dbt project ``version`` is semver/config, not property YAML document v2."""
    p = tmp_path / "dbt_project.yml"
    p.write_text(
        "name: p\nconfig-version: 2\nversion: 3\nmodel-paths: [m]\n",
        encoding="utf-8",
    )
    out = load_dbt_project_yaml(p)
    assert isinstance(out, ParseSuccess)
    assert out.root["version"] == 3


def test_load_dbt_project_empty_skip() -> None:
    out = load_dbt_project_yaml(_f("shared/empty.yml"))
    assert isinstance(out, ParseSkip)
    assert out.reason == SKIP_EMPTY_OR_WHITESPACE
