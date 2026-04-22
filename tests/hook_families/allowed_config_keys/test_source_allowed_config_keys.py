"""Tests for source-allowed-config-keys CLI."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_CFG = _REPO_ROOT / "tests" / "fixtures" / "yaml" / "allowed_config_keys" / "sources"
_SHARED = _REPO_ROOT / "tests" / "fixtures" / "yaml" / "shared"


def _invoke(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "dbt_yaml_guardrails.hook_families.allowed_config_keys."
            "source_allowed_config_keys",
            *args,
        ],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
    )


def test_cli_passes() -> None:
    r = _invoke(str(_CFG / "source_config_clean.yml"))
    assert r.returncode == 0
    assert r.stderr == ""


def test_cli_disallowed() -> None:
    r = _invoke(str(_CFG / "source_config_bad.yml"))
    assert r.returncode == 1
    assert "disallowed config key 'not_allowed'" in r.stderr
    assert "source 's'" in r.stderr


def test_cli_skips_no_sources_section() -> None:
    r = _invoke(str(_SHARED / "minimal_version2.yml"))
    assert r.returncode == 0
