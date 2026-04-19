"""Fusion-oriented default allowlists for dbt property YAML.

The ``*_ALLOWED_KEYS`` and ``*_LEGACY_KEY_MESSAGES`` values are the implementation
source for the **`*-allowed-keys`** family; they **must** stay aligned with
``specs/resource-keys.md`` (change the spec and this module together).
"""

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

# Canonical set for ``seed-allowed-keys`` — MUST match ``specs/resource-keys.md`` § **Seeds**
SEED_ALLOWED_KEYS: frozenset[str] = frozenset(
    (
        "name",
        "description",
        "config",
        "data_tests",
        "columns",
    )
)

# Legacy keys → stderr detail — MUST match ``specs/resource-keys.md`` § Seeds **Suggested violation detail**
SEED_LEGACY_KEY_MESSAGES: Mapping[str, str] = {
    "tests": "Rename to `data_tests` (legacy alias `tests` is deprecated).",
    "meta": "Use `config.meta` instead of top-level `meta`.",
    "tags": "Use `config.tags` instead of top-level `tags`.",
}

# Canonical set for ``snapshot-allowed-keys`` — MUST match ``specs/resource-keys.md`` § **Snapshots**
SNAPSHOT_ALLOWED_KEYS: frozenset[str] = frozenset(
    (
        "name",
        "description",
        "config",
        "data_tests",
        "columns",
    )
)

# Legacy keys → stderr detail — MUST match ``specs/resource-keys.md`` § Snapshots **Suggested violation detail**
SNAPSHOT_LEGACY_KEY_MESSAGES: Mapping[str, str] = {
    "tests": "Rename to `data_tests` (legacy alias `tests` is deprecated).",
    "meta": "Use `config.meta` instead of top-level `meta`.",
    "tags": "Use `config.tags` instead of top-level `tags`.",
}

# Canonical set for ``exposure-allowed-keys`` — MUST match ``specs/resource-keys.md`` § **Exposures**
EXPOSURE_ALLOWED_KEYS: frozenset[str] = frozenset(
    (
        "name",
        "description",
        "type",
        "url",
        "maturity",
        "enabled",
        "config",
        "owner",
        "depends_on",
        "label",
    )
)

# Legacy keys → stderr detail — MUST match ``specs/resource-keys.md`` § Exposures **Suggested violation detail**
EXPOSURE_LEGACY_KEY_MESSAGES: Mapping[str, str] = {
    "meta": "Use `config.meta` instead of top-level `meta`.",
    "tags": "Use `config.tags` instead of top-level `tags` (unless your dbt version documents an exception).",
}
