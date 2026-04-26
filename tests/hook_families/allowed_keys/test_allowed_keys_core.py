"""Unit tests for ``allowed_keys_core.violations_for_entries``."""

from __future__ import annotations

from dbt_yaml_guardrails.hook_families.allowed_keys.allowed_keys_core import (
    violations_for_entries,
)
from dbt_yaml_guardrails.hook_families.allowed_keys.resource_keys import (
    MODEL_ALLOWED_KEYS,
    MODEL_LEGACY_KEY_MESSAGES,
)


def test_legacy_key_uses_detail_not_generic_disallowed() -> None:
    rows = violations_for_entries(
        "/tmp/x.yml",
        [("m", {"name": "m", "tags": []})],
        allowed=MODEL_ALLOWED_KEYS,
        required=set(),
        forbidden=set(),
        legacy_key_messages=MODEL_LEGACY_KEY_MESSAGES,
    )
    assert len(rows) == 1
    _, detail = rows[0]
    assert "config.tags" in detail
    assert "disallowed key" not in detail


def test_unknown_key_still_generic() -> None:
    rows = violations_for_entries(
        "/tmp/x.yml",
        [("m", {"name": "m", "weird": 1})],
        allowed=MODEL_ALLOWED_KEYS,
        required=set(),
        forbidden=set(),
        legacy_key_messages=MODEL_LEGACY_KEY_MESSAGES,
    )
    assert len(rows) == 1
    _, detail = rows[0]
    assert "disallowed key 'weird'" in detail


def test_missing_required_key() -> None:
    rows = violations_for_entries(
        "/a.yml",
        [("m", {"name": "m"})],
        allowed=MODEL_ALLOWED_KEYS,
        required={"description"},
        forbidden=set(),
    )
    sk, detail = rows[0]
    assert sk[3] == 0
    assert "missing required" in detail


def test_forbidden_wins_over_allowlist() -> None:
    rows = violations_for_entries(
        "/a.yml",
        [("m", {"name": "m", "tags": []})],
        allowed=MODEL_ALLOWED_KEYS,
        required=set(),
        forbidden={"tags"},
    )
    sk, detail = rows[0]
    assert sk[3] == 1
    assert "forbidden" in detail
