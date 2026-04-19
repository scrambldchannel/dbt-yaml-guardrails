"""Tests for snapshot-meta-accepted-values CLI (specs/hook-families/meta-accepted-values.md)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_YAML = _REPO_ROOT / "tests" / "fixtures" / "yaml"
_SNAPSHOTS = _YAML / "meta_accepted_values" / "snapshots"
_SHARED = _YAML / "shared"


def _f(name: str) -> str:
    return str(_SNAPSHOTS / name)


def _shared(name: str) -> str:
    return str(_SHARED / name)


def _invoke(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "dbt_yaml_guardrails.hook_families.meta_accepted_values.snapshot_meta_accepted_values",
            *args,
        ],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
    )


def test_cli_passes_domain_ok() -> None:
    r = _invoke(
        "--key",
        "domain",
        "--values",
        "sales,hr,finance",
        _f("domain_ok.yml"),
    )
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_rejects_wrong_value() -> None:
    r = _invoke(
        "--key",
        "domain",
        "--values",
        "sales,hr,finance",
        _f("domain_wrong.yml"),
    )
    assert r.returncode == 1
    assert "snapshot 'm'" in r.stderr
    assert "not an allowed value" in r.stderr


def test_cli_missing_required_path() -> None:
    r = _invoke(
        "--key",
        "domain",
        "--values",
        "sales",
        _f("domain_missing.yml"),
    )
    assert r.returncode == 1
    assert "missing required meta path 'domain'" in r.stderr


def test_cli_optional_missing_ok() -> None:
    r = _invoke(
        "--key",
        "domain",
        "--values",
        "sales",
        "--optional",
        _f("domain_optional_missing.yml"),
    )
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_leaf_not_string() -> None:
    r = _invoke(
        "--key",
        "domain",
        "--values",
        "sales",
        _f("domain_wrong_type.yml"),
    )
    assert r.returncode == 1
    assert "must be a string" in r.stderr


def test_cli_nested_owner_name_ok() -> None:
    r = _invoke(
        "--key",
        "owner.name",
        "--values",
        "alex,annemarie,trevor",
        _f("owner_name_ok.yml"),
    )
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_intermediate_not_mapping() -> None:
    r = _invoke(
        "--key",
        "owner.name",
        "--values",
        "alex",
        _f("owner_name_bad_intermediate.yml"),
    )
    assert r.returncode == 1
    assert "expected mapping before leaf 'name'" in r.stderr


def test_cli_bad_config_meta_shape() -> None:
    r = _invoke("--key", "domain", "--values", "sales", _f("meta_bad_meta_type.yml"))
    assert r.returncode == 1
    assert "config.meta must be a mapping" in r.stderr


def test_cli_skips_no_snapshots_section() -> None:
    r = _invoke("--key", "domain", "--values", "sales", _shared("sources_only.yml"))
    assert r.returncode == 0


def test_cli_skips_empty_file() -> None:
    r = _invoke("--key", "domain", "--values", "sales", _shared("empty.yml"))
    assert r.returncode == 0


def test_cli_invalid_key_exit_2() -> None:
    r = _invoke("--key", "a..b", "--values", "x", _f("domain_ok.yml"))
    assert r.returncode == 2
    assert "--key" in r.stderr


def test_cli_empty_values_exit_2() -> None:
    r = _invoke("--key", "domain", "--values", ",", _f("domain_ok.yml"))
    assert r.returncode == 2
    assert "--values" in r.stderr
