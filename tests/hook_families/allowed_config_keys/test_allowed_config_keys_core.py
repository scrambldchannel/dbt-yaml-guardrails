"""Unit tests for ``allowed_config_keys_core.violations_for_config_keys``."""

from __future__ import annotations

from dbt_yaml_guardrails.hook_families.allowed_config_keys.allowed_config_keys_core import (
    violations_for_config_keys,
)
from dbt_yaml_guardrails.hook_families.allowed_config_keys.resource_config_keys import (
    MODEL_CONFIG_ALLOWED_KEYS,
    MODEL_CONFIG_LEGACY_KEY_MESSAGES,
)


def test_legacy_key_uses_detail() -> None:
    rows = violations_for_config_keys(
        "/tmp/x.yml",
        [("m", {"on": True})],
        allowed=MODEL_CONFIG_ALLOWED_KEYS,
        required=set(),
        forbidden=set(),
        legacy_key_messages=MODEL_CONFIG_LEGACY_KEY_MESSAGES,
    )
    assert len(rows) == 1
    _, detail = rows[0]
    assert "Deprecated key `on`" in detail
    assert "disallowed config key" not in detail


def test_unknown_key_generic() -> None:
    rows = violations_for_config_keys(
        "/tmp/x.yml",
        [("m", {"weird": 1})],
        allowed=MODEL_CONFIG_ALLOWED_KEYS,
        required=set(),
        forbidden=set(),
        legacy_key_messages=MODEL_CONFIG_LEGACY_KEY_MESSAGES,
    )
    assert len(rows) == 1
    _, detail = rows[0]
    assert "disallowed config key 'weird'" in detail
