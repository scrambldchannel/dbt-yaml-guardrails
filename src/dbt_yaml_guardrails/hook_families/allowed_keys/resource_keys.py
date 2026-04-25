"""User-authorable top-level keys for dbt YAML (``specs/resource-keys.md``).

The ``*_ALLOWED_KEYS`` frozensets list keys that a user may **write** in resource
**property YAML** (``schema.yml`` / ``catalogs.yml`` / ``*.yml`` under model-paths,
etc.), as documented in the dbt **resource properties** reference (or, for
``catalogs:``, the v1.10+ catalog wiring docs) for each type. **``DBT_PROJECT_ALLOWED_KEYS``**
covers top-level keys in **``dbt_project.yml``** (see **``resource-keys.md``** § dbt project file).
They intentionally
**do not** include **manifest / artifact-only** fields (e.g. ``original_file_path``,
``package_name``, ``relation_name``) that appear on parsed nodes in ``manifest.json``
but are not declared in property files.

**Legacy keys** (e.g. ``tests`` for ``data_tests``) stay **out** of the allowlist so
``*_legacy_key_messages`` can steer users toward the supported spelling.

The ``*_LEGACY_KEY_MESSAGES`` and **Legacy / deprecated** subsections in the spec
cover keys users should not use; those keys are not in the allowlist unless
explicitly listed for special handling.

``*_COLUMN_ALLOWED_KEYS`` and ``*_COLUMN_LEGACY_KEY_MESSAGES`` cover keys on each
item in a resource's ``columns:`` list (``resource-keys.md`` § Column keys). These
are used by ``*-allowed-keys`` hooks when ``--check-columns`` is active.
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

# Column keys on each item in a model's ``columns:`` list
# (``resource-keys.md`` § Models — Column keys)
MODEL_COLUMN_ALLOWED_KEYS: frozenset[str] = frozenset(
    (
        "constraints",
        "data_tests",
        "data_type",
        "description",
        "granularity",
        "meta",
        "name",
        "quote",
        "tags",
    )
)

MODEL_COLUMN_LEGACY_KEY_MESSAGES: Mapping[str, str] = {
    "tests": "Rename to `data_tests` (legacy alias `tests` is deprecated).",
}

# Column keys on each item in a seed's ``columns:`` list
# (``resource-keys.md`` § Seeds — Column keys)
SEED_COLUMN_ALLOWED_KEYS: frozenset[str] = frozenset(
    (
        "constraints",
        "data_tests",
        "data_type",
        "description",
        "meta",
        "name",
        "quote",
        "tags",
    )
)

SEED_COLUMN_LEGACY_KEY_MESSAGES: Mapping[str, str] = {
    "tests": "Rename to `data_tests` (legacy alias `tests` is deprecated).",
}

# Column keys on each item in a snapshot's ``columns:`` list
# (``resource-keys.md`` § Snapshots — Column keys)
SNAPSHOT_COLUMN_ALLOWED_KEYS: frozenset[str] = frozenset(
    (
        "constraints",
        "data_tests",
        "data_type",
        "description",
        "meta",
        "name",
        "quote",
        "tags",
    )
)

SNAPSHOT_COLUMN_LEGACY_KEY_MESSAGES: Mapping[str, str] = {
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

# dbt 1.10+ [catalogs.yml](https://docs.getdbt.com/docs/dbt-versions/core-upgrade/upgrading-to-v1.10)
# and adapter [write catalog](https://github.com/dbt-labs/dbt-adapters/blob/main/docs/guides/write_catalog.md):
# each list item under `catalogs:`.
CATALOG_ALLOWED_KEYS: frozenset[str] = frozenset(
    (
        "active_write_integration",
        "name",
        "write_integrations",
    )
)

CATALOG_LEGACY_KEY_MESSAGES: Mapping[str, str] = {}


# [dbt_project.yml](https://docs.getdbt.com/reference/dbt_project.yml) — top-level keys.
DBT_PROJECT_ALLOWED_KEYS: frozenset[str] = frozenset(
    (
        "analyses",
        "analysis-paths",
        "asset-paths",
        "clean-targets",
        "config-version",
        "data_tests",
        "dbt-cloud",
        "dispatch",
        "docs-paths",
        "exposures",
        "flags",
        "function-paths",
        "functions",
        "macro-paths",
        "metrics",
        "model-paths",
        "models",
        "name",
        "on-run-end",
        "on-run-start",
        "packages-install-path",
        "profile",
        "query-comment",
        "quoting",
        "require-dbt-version",
        "restrict-access",
        "saved-queries",
        "seed-paths",
        "seeds",
        "semantic-models",
        "snapshot-paths",
        "snapshots",
        "sources",
        "test-paths",
        "vars",
        "version",
    )
)

DBT_PROJECT_LEGACY_KEY_MESSAGES: Mapping[str, str] = {}
