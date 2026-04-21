"""Fusion-oriented default allowlists for keys under ``config:`` in dbt property YAML.

``MODEL_CONFIG_ALLOWED_KEYS`` and ``MODEL_CONFIG_LEGACY_KEY_MESSAGES`` are the
implementation source for **model-allowed-config-keys**; they **must** stay
aligned with ``specs/resource-config-keys.md`` (change the spec and this module
together).
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
