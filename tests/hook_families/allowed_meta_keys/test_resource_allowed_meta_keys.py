"""Tests for seed/snapshot/exposure/macro *-allowed-meta-keys CLIs."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_YAML = _REPO_ROOT / "tests" / "fixtures" / "yaml"
_SHARED = _YAML / "shared"


def _f(kind: str, name: str) -> str:
    return str(_YAML / "allowed_meta_keys" / kind / name)


def _shared(name: str) -> str:
    return str(_SHARED / name)


def _invoke(module: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", module, *args],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
    )


@pytest.mark.parametrize(
    ("module", "fixture_dir"),
    [
        (
            "dbt_yaml_guardrails.hook_families.allowed_meta_keys.seed_allowed_meta_keys",
            "seeds",
        ),
        (
            "dbt_yaml_guardrails.hook_families.allowed_meta_keys.snapshot_allowed_meta_keys",
            "snapshots",
        ),
        (
            "dbt_yaml_guardrails.hook_families.allowed_meta_keys.exposure_allowed_meta_keys",
            "exposures",
        ),
        (
            "dbt_yaml_guardrails.hook_families.allowed_meta_keys.macro_allowed_meta_keys",
            "macros",
        ),
    ],
)
def test_cli_passes_clean_with_required(module: str, fixture_dir: str) -> None:
    r = _invoke(module, "--required", "owner", _f(fixture_dir, "meta_clean.yml"))
    assert r.returncode == 0
    assert r.stderr == ""


@pytest.mark.parametrize(
    ("module", "fixture_dir", "label"),
    [
        (
            "dbt_yaml_guardrails.hook_families.allowed_meta_keys.seed_allowed_meta_keys",
            "seeds",
            "seed",
        ),
        (
            "dbt_yaml_guardrails.hook_families.allowed_meta_keys.snapshot_allowed_meta_keys",
            "snapshots",
            "snapshot",
        ),
        (
            "dbt_yaml_guardrails.hook_families.allowed_meta_keys.exposure_allowed_meta_keys",
            "exposures",
            "exposure",
        ),
        (
            "dbt_yaml_guardrails.hook_families.allowed_meta_keys.macro_allowed_meta_keys",
            "macros",
            "macro",
        ),
    ],
)
def test_cli_forbidden_meta_key(module: str, fixture_dir: str, label: str) -> None:
    r = _invoke(module, "--forbidden", "bad_key", _f(fixture_dir, "meta_forbidden.yml"))
    assert r.returncode == 1
    assert "forbidden meta key 'bad_key'" in r.stderr
    assert f"{label} 'm'" in r.stderr


@pytest.mark.parametrize(
    ("module", "fixture_dir"),
    [
        (
            "dbt_yaml_guardrails.hook_families.allowed_meta_keys.seed_allowed_meta_keys",
            "seeds",
        ),
        (
            "dbt_yaml_guardrails.hook_families.allowed_meta_keys.snapshot_allowed_meta_keys",
            "snapshots",
        ),
        (
            "dbt_yaml_guardrails.hook_families.allowed_meta_keys.exposure_allowed_meta_keys",
            "exposures",
        ),
        (
            "dbt_yaml_guardrails.hook_families.allowed_meta_keys.macro_allowed_meta_keys",
            "macros",
        ),
    ],
)
def test_cli_missing_required_meta_key(module: str, fixture_dir: str) -> None:
    r = _invoke(
        module, "--required", "owner", _f(fixture_dir, "meta_required_missing.yml")
    )
    assert r.returncode == 1
    assert "missing required meta key 'owner'" in r.stderr


@pytest.mark.parametrize(
    ("module", "fixture_dir"),
    [
        (
            "dbt_yaml_guardrails.hook_families.allowed_meta_keys.seed_allowed_meta_keys",
            "seeds",
        ),
        (
            "dbt_yaml_guardrails.hook_families.allowed_meta_keys.snapshot_allowed_meta_keys",
            "snapshots",
        ),
        (
            "dbt_yaml_guardrails.hook_families.allowed_meta_keys.exposure_allowed_meta_keys",
            "exposures",
        ),
        (
            "dbt_yaml_guardrails.hook_families.allowed_meta_keys.macro_allowed_meta_keys",
            "macros",
        ),
    ],
)
def test_cli_allowlist_rejects_unknown_meta_key(module: str, fixture_dir: str) -> None:
    r = _invoke(
        module, "--allowed", "owner", _f(fixture_dir, "meta_allowlist_extra.yml")
    )
    assert r.returncode == 1
    assert "meta key 'extra' not allowed" in r.stderr


@pytest.mark.parametrize(
    ("module", "fixture_dir"),
    [
        (
            "dbt_yaml_guardrails.hook_families.allowed_meta_keys.seed_allowed_meta_keys",
            "seeds",
        ),
        (
            "dbt_yaml_guardrails.hook_families.allowed_meta_keys.snapshot_allowed_meta_keys",
            "snapshots",
        ),
        (
            "dbt_yaml_guardrails.hook_families.allowed_meta_keys.exposure_allowed_meta_keys",
            "exposures",
        ),
        (
            "dbt_yaml_guardrails.hook_families.allowed_meta_keys.macro_allowed_meta_keys",
            "macros",
        ),
    ],
)
def test_cli_bad_config_meta_shape(module: str, fixture_dir: str) -> None:
    r = _invoke(
        module, "--required", "owner", _f(fixture_dir, "meta_bad_meta_type.yml")
    )
    assert r.returncode == 1
    assert "config.meta must be a mapping" in r.stderr


@pytest.mark.parametrize(
    "module",
    [
        "dbt_yaml_guardrails.hook_families.allowed_meta_keys.seed_allowed_meta_keys",
        "dbt_yaml_guardrails.hook_families.allowed_meta_keys.snapshot_allowed_meta_keys",
        "dbt_yaml_guardrails.hook_families.allowed_meta_keys.exposure_allowed_meta_keys",
        "dbt_yaml_guardrails.hook_families.allowed_meta_keys.macro_allowed_meta_keys",
    ],
)
def test_cli_skips_no_target_section(module: str) -> None:
    r = _invoke(module, "--required", "owner", _shared("sources_only.yml"))
    assert r.returncode == 0


@pytest.mark.parametrize(
    "module",
    [
        "dbt_yaml_guardrails.hook_families.allowed_meta_keys.seed_allowed_meta_keys",
        "dbt_yaml_guardrails.hook_families.allowed_meta_keys.snapshot_allowed_meta_keys",
        "dbt_yaml_guardrails.hook_families.allowed_meta_keys.exposure_allowed_meta_keys",
        "dbt_yaml_guardrails.hook_families.allowed_meta_keys.macro_allowed_meta_keys",
    ],
)
def test_cli_skips_empty_file(module: str) -> None:
    r = _invoke(module, "--required", "owner", _shared("empty.yml"))
    assert r.returncode == 0


@pytest.mark.parametrize(
    ("module", "fixture_dir"),
    [
        (
            "dbt_yaml_guardrails.hook_families.allowed_meta_keys.seed_allowed_meta_keys",
            "seeds",
        ),
        (
            "dbt_yaml_guardrails.hook_families.allowed_meta_keys.snapshot_allowed_meta_keys",
            "snapshots",
        ),
        (
            "dbt_yaml_guardrails.hook_families.allowed_meta_keys.exposure_allowed_meta_keys",
            "exposures",
        ),
        (
            "dbt_yaml_guardrails.hook_families.allowed_meta_keys.macro_allowed_meta_keys",
            "macros",
        ),
    ],
)
def test_cli_no_policy_noop(module: str, fixture_dir: str) -> None:
    r = _invoke(module, _f(fixture_dir, "meta_forbidden.yml"))
    assert r.returncode == 0
    assert r.stderr == ""
