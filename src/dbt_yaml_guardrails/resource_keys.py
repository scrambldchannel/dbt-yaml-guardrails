"""Fusion-oriented default allowlists for dbt property YAML (see ``specs/resource-keys.md``)."""

from __future__ import annotations

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

# Canonical set for ``macro-allowed-keys`` — MUST match ``specs/resource-keys.md`` § **Macros**
MACRO_ALLOWED_KEYS: frozenset[str] = frozenset(
    (
        "name",
        "description",
        "config",
        "arguments",
    )
)
