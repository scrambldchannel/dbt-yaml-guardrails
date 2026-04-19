"""Tests for specs/yaml-handling.md (load_property_yaml, extract_model_entries)."""

from __future__ import annotations

from pathlib import Path

from dbt_yaml_guardrails.yaml_handling import (
    SKIP_EMPTY_OR_WHITESPACE,
    SKIP_NO_MACROS_SECTION,
    SKIP_NO_MODELS_SECTION,
    MacroEntriesResult,
    MacroEntriesSkip,
    ModelEntriesResult,
    ModelEntriesSkip,
    ParseError,
    ParseSkip,
    ParseSuccess,
    extract_macro_entries,
    extract_model_entries,
    iter_macro_entries,
    iter_model_entries,
    load_property_yaml,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "yaml"


def _f(name: str) -> Path:
    return FIXTURES / name


def _success(name: str) -> ParseSuccess:
    out = load_property_yaml(_f(name))
    assert isinstance(out, ParseSuccess)
    return out


def test_empty_file_skip() -> None:
    out = load_property_yaml(_f("empty.yml"))
    assert isinstance(out, ParseSkip)
    assert out.reason == SKIP_EMPTY_OR_WHITESPACE


def test_whitespace_only_skip() -> None:
    out = load_property_yaml(_f("whitespace_only.yml"))
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
    out = load_property_yaml(_f("minimal_version2.yml"))
    assert isinstance(out, ParseSuccess)
    assert out.root == {"version": 2, "models": []}


def test_no_version_success() -> None:
    out = load_property_yaml(_f("no_version.yml"))
    assert isinstance(out, ParseSuccess)
    assert out.root == {"models": []}


def test_invalid_syntax_error() -> None:
    out = load_property_yaml(_f("invalid_syntax.yml"))
    assert isinstance(out, ParseError)
    assert "Invalid YAML" in out.message


def test_multi_document_error() -> None:
    out = load_property_yaml(_f("multi_document.yml"))
    assert isinstance(out, ParseError)
    assert "exactly one YAML document" in out.message


def test_duplicate_keys_error() -> None:
    out = load_property_yaml(_f("duplicate_keys.yml"))
    assert isinstance(out, ParseError)
    assert "Invalid YAML" in out.message


def test_root_scalar_error() -> None:
    out = load_property_yaml(_f("root_scalar.yml"))
    assert isinstance(out, ParseError)
    assert "mapping at the document root" in out.message


def test_bad_version_error() -> None:
    out = load_property_yaml(_f("bad_version.yml"))
    assert isinstance(out, ParseError)
    assert "version must be" in out.message


def test_version_string_two_ok() -> None:
    out = load_property_yaml(_f("version_string_two.yml"))
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
    out = extract_model_entries(_success("sources_only.yml"))
    assert isinstance(out, ModelEntriesSkip)
    assert out.reason == SKIP_NO_MODELS_SECTION


def test_extract_models_empty_list() -> None:
    out = extract_model_entries(_success("minimal_version2.yml"))
    assert isinstance(out, ModelEntriesResult)
    assert out.by_name == {}


def test_extract_models_two() -> None:
    out = extract_model_entries(_success("models_two.yml"))
    assert isinstance(out, ModelEntriesResult)
    assert set(out.by_name) == {"alpha", "beta"}
    assert out.by_name["alpha"]["description"] == "First"
    assert out.by_name["beta"]["config"] == {"materialized": "view"}


def test_extract_duplicate_model_name() -> None:
    out = extract_model_entries(_success("models_duplicate_name.yml"))
    assert isinstance(out, ParseError)
    assert "Duplicate model name" in out.message


def test_extract_missing_model_name() -> None:
    out = extract_model_entries(_success("models_missing_name.yml"))
    assert isinstance(out, ParseError)
    assert "missing required key 'name'" in out.message


def test_extract_models_not_list() -> None:
    out = extract_model_entries(_success("models_not_list.yml"))
    assert isinstance(out, ParseError)
    assert "models must be a list" in out.message


def test_extract_models_null() -> None:
    out = extract_model_entries(_success("models_null.yml"))
    assert isinstance(out, ParseError)
    assert "not null" in out.message


def test_iter_model_entries_sorted_names() -> None:
    out = extract_model_entries(_success("models_two.yml"))
    assert isinstance(out, ModelEntriesResult)
    names = [n for n, _ in iter_model_entries(out.by_name)]
    assert names == ["alpha", "beta"]


# --- extract_macro_entries ---


def test_extract_no_macros_section_skip() -> None:
    out = extract_macro_entries(_success("sources_only.yml"))
    assert isinstance(out, MacroEntriesSkip)
    assert out.reason == SKIP_NO_MACROS_SECTION


def test_extract_macros_empty_list() -> None:
    out = extract_macro_entries(_success("macros_empty.yml"))
    assert isinstance(out, MacroEntriesResult)
    assert out.by_name == {}


def test_extract_macros_two() -> None:
    out = extract_macro_entries(_success("macros_two.yml"))
    assert isinstance(out, MacroEntriesResult)
    assert set(out.by_name) == {"my_macro", "other_macro"}
    assert out.by_name["my_macro"]["description"] == "Does something"


def test_extract_duplicate_macro_name() -> None:
    out = extract_macro_entries(_success("macros_duplicate_name.yml"))
    assert isinstance(out, ParseError)
    assert "Duplicate macro name" in out.message


def test_iter_macro_entries_sorted_names() -> None:
    out = extract_macro_entries(_success("macros_two.yml"))
    assert isinstance(out, MacroEntriesResult)
    names = [n for n, _ in iter_macro_entries(out.by_name)]
    assert names == ["my_macro", "other_macro"]
