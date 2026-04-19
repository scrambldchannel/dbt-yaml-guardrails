"""Fusion-oriented default allowlists for dbt property YAML (see ``specs/resource-keys.md``)."""

from __future__ import annotations

from typing import Mapping

# Canonical set for ``model-allowed-keys`` — MUST match ``specs/resource-keys.md`` § **Models**
# (the markdown table mirrors this constant; change both together).
MODEL_ALLOWED_KEYS: frozenset[str] = frozenset(
    (
        "name",
        "description",
        "columns",
        "data_tests",
        "versions",
        "latest_version",
        "version",
        "constraints",
        "docs",
        "config",
    )
)

# Legacy keys → stderr detail — MUST match ``specs/resource-keys.md`` § Models **Suggested violation detail**
MODEL_LEGACY_KEY_MESSAGES: Mapping[str, str] = {
    "tests": "Rename to `data_tests` (legacy alias `tests` is deprecated).",
    "meta": "Use `config.meta` instead of top-level `meta`.",
    "tags": "Use `config.tags` instead of top-level `tags`.",
}

# Canonical set for ``macro-allowed-keys`` — MUST match ``specs/resource-keys.md`` § **Macros**
MACRO_ALLOWED_KEYS: frozenset[str] = frozenset(
    (
        "name",
        "description",
        "config",
        "arguments",
    )
)

# Legacy keys → stderr detail — MUST match ``specs/resource-keys.md`` § Macros **Suggested violation detail**
MACRO_LEGACY_KEY_MESSAGES: Mapping[str, str] = {
    "meta": "Use `config.meta` instead of top-level `meta`.",
    "tags": "Use `config.tags` instead of top-level `tags`.",
}
