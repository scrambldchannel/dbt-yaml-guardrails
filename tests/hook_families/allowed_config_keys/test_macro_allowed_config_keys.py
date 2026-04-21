"""Tests for macro-allowed-config-keys CLI."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_CFG = _REPO_ROOT / "tests" / "fixtures" / "yaml" / "allowed_config_keys" / "macros"
_SHARED = _REPO_ROOT / "tests" / "fixtures" / "yaml" / "shared"


def _invoke(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "dbt_yaml_guardrails.hook_families.allowed_config_keys.macro_allowed_config_keys",
            *args,
        ],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
    )


def test_cli_passes() -> None:
    r = _invoke(str(_CFG / "macro_config_clean.yml"))
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_disallowed() -> None:
    r = _invoke(str(_CFG / "macro_config_bad.yml"))
    assert r.returncode == 1
    assert "disallowed config key 'materialized'" in r.stderr
    assert "macro 'm'" in r.stderr


def test_cli_skips_no_macros_section() -> None:
    r = _invoke(str(_SHARED / "sources_only.yml"))
    assert r.returncode == 0
