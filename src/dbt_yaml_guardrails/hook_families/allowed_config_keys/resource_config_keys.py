"""Fusion-oriented default allowlists for keys under ``config:`` in dbt property YAML.

The ``*_CONFIG_ALLOWED_KEYS`` and ``*_CONFIG_LEGACY_KEY_MESSAGES`` values are the
implementation source for **`*-allowed-config-keys`**; they **must** stay aligned
with ``specs/resource-config-keys.md`` (change the spec and this module together).
"""

from __future__ import annotations

from typing import Mapping

# Cross-adapter model keys under ``config`` — MUST match ``specs/resource-config-keys.md``
# § **Models — default keys under `config`**.
_MODEL_CONFIG_CROSS_ADAPTER: tuple[str, ...] = (
    "access",
    "alias",
    "contract",
    "database",
    "enabled",
    "event_time",
    "freshness",
    "full_refresh",
    "grants",
    "group",
    "incremental_strategy",
    "materialized",
    "meta",
    "on_configuration_change",
    "persist_docs",
    "post_hook",
    "pre_hook",
    "schema",
    "sql_header",
    "static_analysis",
    "tags",
    "unique_key",
)

# Adapter union for models — MUST match ``specs/resource-config-keys.md``
# § **Adapter-specific (union across adapters — models)**.
_MODEL_CONFIG_ADAPTER: tuple[str, ...] = (
    "access_control_list",
    "additional_libs",
    "auto_liquid_cluster",
    "auto_refresh",
    "automatic_clustering",
    "backup",
    "bind",
    "buckets",
    "cluster_by",
    "clustered_by",
    "cluster_id",
    "compression",
    "compute_region",
    "create_notebook",
    "databricks_tags",
    "dataproc_cluster_name",
    "dist",
    "enable_change_history",
    "enable_list_inference",
    "enable_refresh",
    "external_access_integrations",
    "file_format",
    "gcs_bucket",
    "grant_access_to",
    "hours_to_expiration",
    "http_path",
    "immutable_where",
    "imports",
    "include_full_name_in_path",
    "indexes",
    "index_url",
    "initialize",
    "intermediate_format",
    "job_cluster_config",
    "kms_key_name",
    "labels",
    "liquid_clustered_by",
    "location_root",
    "max_staleness",
    "notebook_template_id",
    "overwrite_columns",
    "packages",
    "partition_by",
    "partition_expiration_days",
    "partitions",
    "python_job_config",
    "python_version",
    "query_group",
    "query_tag",
    "query_tags",
    "refresh_interval_minutes",
    "refresh_mode",
    "require_partition_filter",
    "resource_tags",
    "schedule",
    "scheduler",
    "secrets",
    "snowflake_initialization_warehouse",
    "snowflake_warehouse",
    "sort",
    "sort_type",
    "submission_method",
    "table_format",
    "target_lag",
    "tblproperties",
    "timeout",
    "tmp_relation_type",
    "transient",
    "unlogged",
)

MODEL_CONFIG_ALLOWED_KEYS: frozenset[str] = frozenset(
    _MODEL_CONFIG_CROSS_ADAPTER + _MODEL_CONFIG_ADAPTER
)

# Legacy keys under ``config`` — MUST match ``specs/resource-config-keys.md``
# § **Legacy / deprecated (under `config` — models)** **Suggested violation detail**.
MODEL_CONFIG_LEGACY_KEY_MESSAGES: Mapping[str, str] = {
    "on": (
        "Deprecated key `on` under config for `static_analysis`; use `strict` "
        "(see static_analysis in dbt resource configs)."
    ),
    "unsafe": (
        "Deprecated key `unsafe` under config for `static_analysis`; use "
        "`baseline` or `strict`."
    ),
}

# ---------------------------------------------------------------------------
# Seeds — MUST match ``specs/resource-config-keys.md`` § **Seeds**
# ---------------------------------------------------------------------------

_SEED_CONFIG_CROSS_ADAPTER: tuple[str, ...] = (
    "alias",
    "column_types",
    "database",
    "delimiter",
    "enabled",
    "event_time",
    "full_refresh",
    "grants",
    "meta",
    "persist_docs",
    "post_hook",
    "pre_hook",
    "quote_columns",
    "schema",
    "static_analysis",
    "tags",
)

# Adapter keys documented for seeds (subset of the model union) — see spec § Adapter-specific (seeds).
_SEED_CONFIG_ADAPTER: tuple[str, ...] = (
    "auto_liquid_cluster",
    "automatic_clustering",
    "cluster_by",
    "clustered_by",
    "buckets",
    "compression",
    "databricks_tags",
    "dist",
    "file_format",
    "grant_access_to",
    "hours_to_expiration",
    "include_full_name_in_path",
    "indexes",
    "kms_key_name",
    "labels",
    "liquid_clustered_by",
    "location_root",
    "partition_by",
    "partition_expiration_days",
    "query_group",
    "query_tag",
    "query_tags",
    "require_partition_filter",
    "resource_tags",
    "snowflake_warehouse",
    "sort",
    "sort_type",
    "table_format",
    "tblproperties",
    "transient",
    "unlogged",
)

SEED_CONFIG_ALLOWED_KEYS: frozenset[str] = frozenset(
    _SEED_CONFIG_CROSS_ADAPTER + _SEED_CONFIG_ADAPTER
)

SEED_CONFIG_LEGACY_KEY_MESSAGES: Mapping[str, str] = {}

# ---------------------------------------------------------------------------
# Snapshots — MUST match ``specs/resource-config-keys.md`` § **Snapshots**
# ---------------------------------------------------------------------------

_SNAPSHOT_CONFIG_CROSS_ADAPTER: tuple[str, ...] = (
    "alias",
    "check_cols",
    "database",
    "dbt_valid_to_current",
    "enabled",
    "event_time",
    "grants",
    "hard_deletes",
    "meta",
    "persist_docs",
    "post_hook",
    "pre_hook",
    "schema",
    "snapshot_meta_column_names",
    "static_analysis",
    "strategy",
    "tags",
    "unique_key",
    "updated_at",
)

# Model adapter keys that do not apply to snapshots (Python models, dynamic tables, …).
_SNAPSHOT_CONFIG_ADAPTER_EXCLUDE: frozenset[str] = frozenset(
    (
        "access_control_list",
        "additional_libs",
        "cluster_id",
        "compute_region",
        "create_notebook",
        "dataproc_cluster_name",
        "enable_change_history",
        "enable_list_inference",
        "enable_refresh",
        "external_access_integrations",
        "gcs_bucket",
        "http_path",
        "imports",
        "index_url",
        "intermediate_format",
        "job_cluster_config",
        "max_staleness",
        "notebook_template_id",
        "packages",
        "partitions",
        "python_job_config",
        "python_version",
        "refresh_interval_minutes",
        "schedule",
        "secrets",
        "submission_method",
        "timeout",
        "immutable_where",
        "initialize",
        "overwrite_columns",
        "refresh_mode",
        "scheduler",
        "snowflake_initialization_warehouse",
        "target_lag",
        "tmp_relation_type",
    )
)

_SNAPSHOT_CONFIG_ADAPTER: tuple[str, ...] = tuple(
    sorted(frozenset(_MODEL_CONFIG_ADAPTER) - _SNAPSHOT_CONFIG_ADAPTER_EXCLUDE)
)

SNAPSHOT_CONFIG_ALLOWED_KEYS: frozenset[str] = frozenset(
    _SNAPSHOT_CONFIG_CROSS_ADAPTER + _SNAPSHOT_CONFIG_ADAPTER
)

SNAPSHOT_CONFIG_LEGACY_KEY_MESSAGES: Mapping[str, str] = {}

# ---------------------------------------------------------------------------
# Macros — MUST match ``specs/resource-config-keys.md`` § **Macros**
# ---------------------------------------------------------------------------

MACRO_CONFIG_ALLOWED_KEYS: frozenset[str] = frozenset(("docs", "meta"))

MACRO_CONFIG_LEGACY_KEY_MESSAGES: Mapping[str, str] = {}

# ---------------------------------------------------------------------------
# Exposures — MUST match ``specs/resource-config-keys.md`` § **Exposures**
# ---------------------------------------------------------------------------

EXPOSURE_CONFIG_ALLOWED_KEYS: frozenset[str] = frozenset(("enabled", "meta", "tags"))

EXPOSURE_CONFIG_LEGACY_KEY_MESSAGES: Mapping[str, str] = {}

# ---------------------------------------------------------------------------
# Sources — MUST match ``specs/resource-config-keys.md`` § **Sources**
# ---------------------------------------------------------------------------

SOURCE_CONFIG_ALLOWED_KEYS: frozenset[str] = frozenset(
    (
        "enabled",
        "event_time",
        "freshness",
        "meta",
        "tags",
    )
)

SOURCE_CONFIG_LEGACY_KEY_MESSAGES: Mapping[str, str] = {}
