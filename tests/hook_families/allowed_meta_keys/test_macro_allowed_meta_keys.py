"""Tests for macro-allowed-meta-keys CLI (specs/hook-families/allowed-meta-keys.md)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_YAML = _REPO_ROOT / "tests" / "fixtures" / "yaml"
_MACROS = _YAML / "allowed_meta_keys" / "macros"
_SHARED = _YAML / "shared"


def _f(name: str) -> str:
    return str(_MACROS / name)


def _shared(name: str) -> str:
    return str(_SHARED / name)


def _invoke(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "dbt_yaml_guardrails.hook_families.allowed_meta_keys.macro_allowed_meta_keys",
            *args,
        ],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
    )


def test_cli_passes_clean_with_required() -> None:
    r = _invoke("--required", "owner", _f("meta_clean.yml"))
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_forbidden_meta_key() -> None:
    r = _invoke("--forbidden", "bad_key", _f("meta_forbidden.yml"))
    assert r.returncode == 1
    assert "forbidden meta key 'bad_key'" in r.stderr
    assert "macro 'm'" in r.stderr


def test_cli_missing_required_meta_key() -> None:
    r = _invoke("--required", "owner", _f("meta_required_missing.yml"))
    assert r.returncode == 1
    assert "missing required meta key 'owner'" in r.stderr


def test_cli_allowlist_rejects_unknown_meta_key() -> None:
    r = _invoke("--allowed", "owner", _f("meta_allowlist_extra.yml"))
    assert r.returncode == 1
    assert "meta key 'extra' not allowed" in r.stderr


def test_cli_bad_config_meta_shape() -> None:
    r = _invoke("--required", "owner", _f("meta_bad_meta_type.yml"))
    assert r.returncode == 1
    assert "config.meta must be a mapping" in r.stderr


def test_cli_skips_no_macros_section() -> None:
    r = _invoke("--required", "owner", _shared("sources_only.yml"))
    assert r.returncode == 0


def test_cli_skips_empty_file() -> None:
    r = _invoke("--required", "owner", _shared("empty.yml"))
    assert r.returncode == 0


def test_cli_no_policy_noop() -> None:
    r = _invoke(_f("meta_forbidden.yml"))
    assert r.returncode == 0
    assert r.stderr == ""
