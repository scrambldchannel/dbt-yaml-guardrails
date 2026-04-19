"""Tests for specs/yaml-handling.md Phases 1–3 (load_property_yaml)."""

from __future__ import annotations

from pathlib import Path

from dbt_yaml_guardrails.yaml_handling import (
    SKIP_EMPTY_OR_WHITESPACE,
    ParseError,
    ParseSkip,
    ParseSuccess,
    load_property_yaml,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "yaml"


def _f(name: str) -> Path:
    return FIXTURES / name


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
