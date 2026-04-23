"""User-authorable top-level keys for dbt property YAML (``specs/resource-keys.md``).

The ``*_ALLOWED_KEYS`` frozensets list keys that a user may **write** in resource
**property YAML** (``schema.yml`` / ``*.yml`` under model-paths, etc.), as documented in
the dbt **resource properties** reference for each type. They intentionally **do not**
include **manifest / artifact-only** fields (e.g. ``original_file_path``,
``package_name``, ``relation_name``) that appear on parsed nodes in ``manifest.json``
but are not declared in property files.

**Legacy keys** (e.g. ``tests`` for ``data_tests``) stay **out** of the allowlist so
``*_legacy_key_messages`` can steer users toward the supported spelling.

The ``*_LEGACY_KEY_MESSAGES`` and **Legacy / deprecated** subsections in the spec
cover keys users should not use; those keys are not in the allowlist unless
explicitly listed for special handling.
"""

from __future__ import annotations

from typing import Mapping

# [Model properties](https://docs.getdbt.com/reference/model-properties) “Available
# top-level model properties” + latest-YAML fields from the same page (``agg_time_dimension``,
# ``primary_entity`` in the latest example). Excludes ``tests`` (use ``MODEL_LEGACY_KEY_MESSAGES``).
MODEL_ALLOWED_KEYS: frozenset[str] = frozenset(
    (
        "access",
        "agg_time_dimension",
        "columns",
        "config",
        "constraints",
        "data_tests",
        "deprecation_date",
        "description",
        "latest_version",
        "metrics",
        "name",
        "primary_entity",
        "semantic_model",
        "time_spine",
        "versions",
    )
)

MODEL_LEGACY_KEY_MESSAGES: Mapping[str, str] = {
    "meta": "Use `config.meta` instead of top-level `meta`.",
    "sources": "Deprecated: prefer `exposures` and `sources` per dbt model properties; remove top-level `sources`.",
    "tags": "Use `config.tags` instead of top-level `tags`.",
    "tests": "Rename to `data_tests` (legacy alias `tests` is deprecated).",
}

# [Macro properties](https://docs.getdbt.com/reference/macro-properties)
MACRO_ALLOWED_KEYS: frozenset[str] = frozenset(
    (
        "arguments",
        "config",
        "description",
        "name",
    )
)

MACRO_LEGACY_KEY_MESSAGES: Mapping[str, str] = {
    "meta": "Use `config.meta` instead of top-level `meta`.",
    "tags": "Use `config.tags` instead of top-level `tags`.",
    "tests": "Rename to `data_tests` (legacy alias `tests` is deprecated).",
}

# [Seed properties](https://docs.getdbt.com/reference/seed-properties)
SEED_ALLOWED_KEYS: frozenset[str] = frozenset(
    (
        "columns",
        "config",
        "data_tests",
        "description",
        "name",
    )
)

SEED_LEGACY_KEY_MESSAGES: Mapping[str, str] = {
    "meta": "Use `config.meta` instead of top-level `meta`.",
    "tags": "Use `config.tags` instead of top-level `tags`.",
    "tests": "Rename to `data_tests` (legacy alias `tests` is deprecated).",
}

# [Snapshot properties](https://docs.getdbt.com/reference/snapshot-properties)
SNAPSHOT_ALLOWED_KEYS: frozenset[str] = frozenset(
    (
        "columns",
        "config",
        "data_tests",
        "description",
        "name",
    )
)

SNAPSHOT_LEGACY_KEY_MESSAGES: Mapping[str, str] = {
    "meta": "Use `config.meta` instead of top-level `meta`.",
    "tags": "Use `config.tags` instead of top-level `tags`.",
    "tests": "Rename to `data_tests` (legacy alias `tests` is deprecated).",
}

# [Exposure properties](https://docs.getdbt.com/reference/exposure-properties)
EXPOSURE_ALLOWED_KEYS: frozenset[str] = frozenset(
    (
        "config",
        "depends_on",
        "description",
        "enabled",
        "label",
        "maturity",
        "name",
        "owner",
        "type",
        "url",
    )
)

EXPOSURE_LEGACY_KEY_MESSAGES: Mapping[str, str] = {
    "meta": "Use `config.meta` instead of top-level `meta`.",
    "tags": "Use `config.tags` instead of top-level `tags` (unless your dbt version documents an exception).",
    "tests": "Rename to `data_tests` (legacy alias `tests` is deprecated).",
}

# [Source properties](https://docs.getdbt.com/reference/source-properties)
SOURCE_ALLOWED_KEYS: frozenset[str] = frozenset(
    (
        "config",
        "database",
        "description",
        "loader",
        "name",
        "quoting",
        "schema",
        "tables",
    )
)

SOURCE_LEGACY_KEY_MESSAGES: Mapping[str, str] = {
    "meta": "Use `config.meta` instead of top-level `meta`.",
    "overrides": "Remove `overrides` (deprecated in dbt v1.10+); use other source configuration.",
    "sources": "Deprecated in favor of **`exposures`** + `sources`.",
    "tags": "Use `config.tags` instead of top-level `tags`.",
    "tests": "Rename to `data_tests` (legacy alias `tests` is deprecated).",
}
