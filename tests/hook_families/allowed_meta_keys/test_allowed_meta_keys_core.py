"""Unit tests for ``violations_for_meta_keys``."""

from __future__ import annotations

from dbt_yaml_guardrails.hook_families.allowed_meta_keys.allowed_meta_keys_core import (
    violations_for_meta_keys,
)


def test_allowlist_mode_forbidden_wins_over_effective_allow() -> None:
    rows = violations_for_meta_keys(
        "/x.yml",
        "m",
        {"owner", "bad"},
        required=set(),
        forbidden={"bad"},
        allowed=frozenset({"owner", "bad"}),
    )
    details = [d for _, d in rows]
    assert any("forbidden meta key 'bad'" in d for d in details)
    assert not any("not allowed" in d for d in details if "bad" in d)


def test_no_allowlist_only_forbidden() -> None:
    rows = violations_for_meta_keys(
        "/x.yml",
        "m",
        {"owner", "bad"},
        required=set(),
        forbidden={"bad"},
        allowed=None,
    )
    assert len(rows) == 1
    assert "forbidden meta key 'bad'" in rows[0][1]


def test_no_allowlist_unknown_key_ok() -> None:
    rows = violations_for_meta_keys(
        "/x.yml",
        "m",
        {"owner", "anything"},
        required=set(),
        forbidden=set(),
        allowed=None,
    )
    assert rows == []
