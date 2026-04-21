# Resource config key allowlists

Fusion-oriented **default allowed keys** **under each resource’s `config:` mapping** for the **`*-allowed-config-keys`** hook family (see **[`hook-families/allowed-config-keys.md`](hook-families/allowed-config-keys.md)** and **[`hooks.md`](hooks.md)**). **`--forbidden`** can additionally ban keys from the default set.

**Related:** [`yaml-handling.md`](yaml-handling.md), [`resource-keys.md`](resource-keys.md) (top-level keys on each resource entry), [`hook-families/allowed-config-keys.md`](hook-families/allowed-config-keys.md).

**Source of truth (implementation):** **`MODEL_CONFIG_ALLOWED_KEYS`** in **`src/dbt_yaml_guardrails/hook_families/allowed_config_keys/resource_config_keys.py`** (cross-adapter model rows **plus** the **Adapter-specific** union for models). Other resource types **TBD**.

**Sources:** [Model configs](https://docs.getdbt.com/reference/model-configs), [Seed configs](https://docs.getdbt.com/reference/seed-configs), [Snapshot configs](https://docs.getdbt.com/reference/snapshot-configs), [Macro properties](https://docs.getdbt.com/reference/macro-properties), [Exposure properties](https://docs.getdbt.com/reference/exposure-properties), [access](https://docs.getdbt.com/reference/resource-configs/access), [group](https://docs.getdbt.com/reference/resource-configs/group), [static_analysis](https://docs.getdbt.com/reference/resource-configs/static-analysis) (Fusion). Default tables list **cross-adapter** keys from those pages; **Fusion** adds **`static_analysis`** on models, seeds, and snapshots per [Fusion docs](https://docs.getdbt.com/docs/fusion/new-concepts).

**Adapter-specific keys:** Resolving **which** warehouse adapter a project uses (profile / target) is **out of scope** for the hook. The default allowlist is therefore a **union** of documented adapter **`config`** keys—primarily from dbt’s **[BigQuery](https://docs.getdbt.com/reference/resource-configs/bigquery-configs)**, **[Snowflake](https://docs.getdbt.com/reference/resource-configs/snowflake-configs)**, **[Redshift](https://docs.getdbt.com/reference/resource-configs/redshift-configs)**, **[Postgres](https://docs.getdbt.com/reference/resource-configs/postgres-configs)**, **[Databricks](https://docs.getdbt.com/reference/resource-configs/databricks-configs)**, and **[Apache Spark](https://docs.getdbt.com/reference/resource-configs/spark-configs)** pages—so legitimate keys are not flagged merely because they only apply on another platform. Implementations **MUST** include this union in the frozen default set alongside the cross-adapter table for each resource type.

## Models — default keys under `config`

| Key | Notes |
| --- | --- |
| `access` | [access](https://docs.getdbt.com/reference/resource-configs/access) |
| `alias` | |
| `contract` | |
| `database` | |
| `enabled` | |
| `event_time` | [event_time](https://docs.getdbt.com/reference/resource-configs/event-time) |
| `freshness` | [freshness](https://docs.getdbt.com/reference/resource-configs/freshness) (e.g. `build_after` nested) |
| `full_refresh` | |
| `grants` | |
| `group` | [group](https://docs.getdbt.com/reference/resource-configs/group) |
| `incremental_strategy` | Common for incremental materializations; see [incremental models](https://docs.getdbt.com/docs/build/incremental-models#configuring-incremental-models) |
| `materialized` | |
| `meta` | |
| `on_configuration_change` | Materialized views; [on_configuration_change](https://docs.getdbt.com/reference/resource-configs/on_configuration_change) |
| `persist_docs` | |
| `post_hook` | Property YAML uses `post_hook` ([pre-hook / post-hook](https://docs.getdbt.com/reference/resource-configs/pre-hook-post-hook)) |
| `pre_hook` | |
| `schema` | |
| `sql_header` | |
| `static_analysis` | Fusion: `off` \| `baseline` \| `strict` ([static_analysis](https://docs.getdbt.com/reference/resource-configs/static-analysis)) |
| `tags` | |
| `unique_key` | |

### Adapter-specific (union across adapters — models)

These keys appear in adapter docs as **model** `config` entries. **Out of scope:** detecting the active adapter—hooks use this **full union** as the default allowlist.

| Key | Notes |
| --- | --- |
| `access_control_list` | Databricks Python models ([submission methods](https://docs.getdbt.com/reference/resource-configs/databricks-configs#python-submission-methods)) |
| `additional_libs` | Databricks Python models |
| `auto_liquid_cluster` | Databricks ([tables](https://docs.getdbt.com/reference/resource-configs/databricks-configs#configuring-tables)) |
| `auto_refresh` | Redshift materialized views ([Redshift](https://docs.getdbt.com/reference/resource-configs/redshift-configs)) |
| `automatic_clustering` | Snowflake ([clustering](https://docs.getdbt.com/reference/resource-configs/snowflake-configs#configuring-table-clustering)) |
| `backup` | Redshift materialized views |
| `bind` | Redshift late-binding views ([Redshift](https://docs.getdbt.com/reference/resource-configs/redshift-configs)) |
| `buckets` | Databricks / Spark bucketing ([Databricks](https://docs.getdbt.com/reference/resource-configs/databricks-configs#configuring-tables), [Spark](https://docs.getdbt.com/reference/resource-configs/spark-configs#configuring-tables)) |
| `cluster_by` | BigQuery clustering; Snowflake clustering; overlaps naming only ([BigQuery](https://docs.getdbt.com/reference/resource-configs/bigquery-configs#clustering-clause), [Snowflake](https://docs.getdbt.com/reference/resource-configs/snowflake-configs#configuring-table-clustering)) |
| `clustered_by` | Databricks / Spark ([Databricks](https://docs.getdbt.com/reference/resource-configs/databricks-configs#configuring-tables), [Spark](https://docs.getdbt.com/reference/resource-configs/spark-configs#configuring-tables)) |
| `cluster_id` | Databricks Python models |
| `compression` | Databricks ([tables](https://docs.getdbt.com/reference/resource-configs/databricks-configs#configuring-tables)) |
| `compute_region` | BigQuery Python models ([BigQuery](https://docs.getdbt.com/reference/resource-configs/bigquery-configs#python-model-configuration)) |
| `create_notebook` | Databricks Python models |
| `databricks_tags` | Databricks Unity Catalog tags ([Databricks](https://docs.getdbt.com/reference/resource-configs/databricks-configs#configuring-tables)) |
| `dataproc_cluster_name` | BigQuery Python models (Dataproc) |
| `dist` | Redshift distkey ([Redshift](https://docs.getdbt.com/reference/resource-configs/redshift-configs#using-sortkey-and-distkey)) |
| `enable_change_history` | BigQuery incremental ([BigQuery](https://docs.getdbt.com/reference/resource-configs/bigquery-configs#change-history)) |
| `enable_list_inference` | BigQuery Python models |
| `enable_refresh` | BigQuery materialized views ([BigQuery](https://docs.getdbt.com/reference/resource-configs/bigquery-configs#materialized-views)) |
| `external_access_integrations` | Snowflake Python models ([Snowflake](https://docs.getdbt.com/reference/resource-configs/snowflake-configs#python-model-configuration)) |
| `file_format` | Databricks / Spark ([Databricks](https://docs.getdbt.com/reference/resource-configs/databricks-configs#configuring-tables), [Spark](https://docs.getdbt.com/reference/resource-configs/spark-configs#configuring-tables)) |
| `gcs_bucket` | BigQuery Python models |
| `grant_access_to` | BigQuery authorized views ([BigQuery](https://docs.getdbt.com/reference/resource-configs/bigquery-configs#authorized-views)) |
| `hours_to_expiration` | BigQuery table expiration ([BigQuery](https://docs.getdbt.com/reference/resource-configs/bigquery-configs#controlling-table-expiration)) |
| `http_path` | Databricks Python models (compute routing) |
| `immutable_where` | Snowflake dynamic tables ([Snowflake](https://docs.getdbt.com/reference/resource-configs/snowflake-configs)) |
| `imports` | Snowflake Python models (staged packages) |
| `include_full_name_in_path` | Databricks ([tables](https://docs.getdbt.com/reference/resource-configs/databricks-configs#configuring-tables)) |
| `indexes` | Postgres tables / materialized views ([Postgres](https://docs.getdbt.com/reference/resource-configs/postgres-configs#indexes)) |
| `index_url` | Databricks Python models (`packages` install source) |
| `initialize` | Snowflake dynamic tables ([Snowflake](https://docs.getdbt.com/reference/resource-configs/snowflake-configs)) |
| `intermediate_format` | BigQuery Python models |
| `job_cluster_config` | Databricks Python models |
| `kms_key_name` | BigQuery encryption ([BigQuery](https://docs.getdbt.com/reference/resource-configs/bigquery-configs#using-kms-encryption)) |
| `labels` | BigQuery labels ([BigQuery](https://docs.getdbt.com/reference/resource-configs/bigquery-configs#specifying-labels)) |
| `liquid_clustered_by` | Databricks Liquid Clustering ([Databricks](https://docs.getdbt.com/reference/resource-configs/databricks-configs#configuring-tables)) |
| `location_root` | Databricks / Spark external paths ([Databricks](https://docs.getdbt.com/reference/resource-configs/databricks-configs#configuring-tables), [Spark](https://docs.getdbt.com/reference/resource-configs/spark-configs#configuring-tables)) |
| `max_staleness` | BigQuery materialized views ([BigQuery](https://docs.getdbt.com/reference/resource-configs/bigquery-configs#auto-refresh)) |
| `notebook_template_id` | BigQuery Python models |
| `overwrite_columns` | Snowflake `insert_overwrite` incremental ([Snowflake](https://docs.getdbt.com/reference/resource-configs/snowflake-configs#overwrite_columns)) |
| `packages` | Snowflake / BigQuery / Databricks Python models |
| `partition_by` | BigQuery partitioning; Databricks / Spark partitioning (shapes differ by adapter) ([BigQuery](https://docs.getdbt.com/reference/resource-configs/bigquery-configs#partition-clause)) |
| `partition_expiration_days` | BigQuery ([BigQuery](https://docs.getdbt.com/reference/resource-configs/bigquery-configs#additional-partition-configs)) |
| `partitions` | BigQuery `insert_overwrite` static partitions ([BigQuery](https://docs.getdbt.com/reference/resource-configs/bigquery-configs#static-partitions)) |
| `python_job_config` | Databricks Python models (`workflow_job` and related) |
| `python_version` | Snowflake Python models ([Snowflake](https://docs.getdbt.com/reference/resource-configs/snowflake-configs#python-model-configuration)) |
| `query_group` | Redshift WLM ([Redshift](https://docs.getdbt.com/reference/resource-configs/redshift-configs#session-configuration)) |
| `query_tag` | Snowflake session query tag ([Snowflake](https://docs.getdbt.com/reference/resource-configs/snowflake-configs#query-tags)) |
| `query_tags` | Databricks query tags ([Databricks](https://docs.getdbt.com/reference/resource-configs/databricks-configs#query-tags)) |
| `refresh_interval_minutes` | BigQuery materialized views ([BigQuery](https://docs.getdbt.com/reference/resource-configs/bigquery-configs#auto-refresh)) |
| `refresh_mode` | Snowflake dynamic tables ([Snowflake](https://docs.getdbt.com/reference/resource-configs/snowflake-configs)) |
| `require_partition_filter` | BigQuery ([BigQuery](https://docs.getdbt.com/reference/resource-configs/bigquery-configs#additional-partition-configs)) |
| `resource_tags` | BigQuery IAM resource tags ([BigQuery](https://docs.getdbt.com/reference/resource-configs/bigquery-configs#resource-tags)) |
| `schedule` | Databricks materialized views / streaming tables ([Databricks](https://docs.getdbt.com/reference/resource-configs/databricks-configs#materialized-views-and-streaming-tables)) |
| `scheduler` | Snowflake dynamic tables ([Snowflake](https://docs.getdbt.com/reference/resource-configs/snowflake-configs)) |
| `secrets` | Snowflake Python models ([Snowflake](https://docs.getdbt.com/reference/resource-configs/snowflake-configs#python-model-configuration)) |
| `snowflake_initialization_warehouse` | Snowflake dynamic tables ([Snowflake](https://docs.getdbt.com/reference/resource-configs/snowflake-configs)) |
| `snowflake_warehouse` | Snowflake virtual warehouse ([Snowflake](https://docs.getdbt.com/reference/resource-configs/snowflake-configs)) |
| `sort` | Redshift sortkey ([Redshift](https://docs.getdbt.com/reference/resource-configs/redshift-configs#using-sortkey-and-distkey)) |
| `sort_type` | Redshift (`interleaved` / `compound`) |
| `submission_method` | BigQuery Python models; Databricks Python models |
| `table_format` | Databricks Iceberg uniform ([Databricks](https://docs.getdbt.com/reference/resource-configs/databricks-configs#configuring-tables)) |
| `target_lag` | Snowflake dynamic tables ([Snowflake](https://docs.getdbt.com/reference/resource-configs/snowflake-configs)) |
| `tblproperties` | Databricks / Spark ([Databricks](https://docs.getdbt.com/reference/resource-configs/databricks-configs#setting-table-properties), [Spark](https://docs.getdbt.com/reference/resource-configs/spark-configs#configuring-tables)) |
| `timeout` | Databricks / BigQuery Python models |
| `tmp_relation_type` | Snowflake incremental temp relation ([Snowflake](https://docs.getdbt.com/reference/resource-configs/snowflake-configs#temporary-tables)) |
| `transient` | Snowflake transient tables / dynamic tables ([Snowflake](https://docs.getdbt.com/reference/resource-configs/snowflake-configs)) |
| `unlogged` | Postgres unlogged tables ([Postgres](https://docs.getdbt.com/reference/resource-configs/postgres-configs#unlogged)) |

### Legacy / deprecated (under `config` — models)

| Key | Notes | Suggested violation detail |
| --- | --- | --- |
| `on` | Deprecated value for **`static_analysis`**; use **`strict`**. | [static_analysis](https://docs.getdbt.com/reference/resource-configs/static-analysis) |
| `unsafe` | Deprecated value for **`static_analysis`**. | Use **`baseline`** or **`strict`**. |

## Seeds — default keys under `config`

| Key | Notes |
| --- | --- |
| `alias` | |
| `column_types` | [column_types](https://docs.getdbt.com/reference/resource-configs/column_types) |
| `database` | |
| `delimiter` | [delimiter](https://docs.getdbt.com/reference/resource-configs/delimiter) |
| `enabled` | |
| `event_time` | |
| `full_refresh` | |
| `grants` | |
| `meta` | |
| `persist_docs` | |
| `post_hook` | |
| `pre_hook` | |
| `quote_columns` | [quote_columns](https://docs.getdbt.com/reference/resource-configs/quote_columns) |
| `schema` | |
| `static_analysis` | Fusion ([Fusion docs](https://docs.getdbt.com/docs/fusion/new-concepts)) |
| `tags` | |

### Adapter-specific (union across adapters — seeds)

Seeds use a smaller surface area than models; the default allowlist **includes** every key in **Models § Adapter-specific** that adapter docs allow on **`config`** for seeds (e.g. BigQuery **`labels`**, **`resource_tags`**, **`kms_key_name`**, **`hours_to_expiration`**; Databricks / Spark **`file_format`**, **`location_root`**, **`tblproperties`**). **Out of scope:** resolving the active adapter—use the same **union** as models.

## Snapshots — default keys under `config`

| Key | Notes |
| --- | --- |
| `alias` | |
| `check_cols` | [check_cols](https://docs.getdbt.com/reference/resource-configs/check_cols) |
| `database` | |
| `dbt_valid_to_current` | [dbt_valid_to_current](https://docs.getdbt.com/reference/resource-configs/dbt_valid_to_current) |
| `enabled` | |
| `event_time` | |
| `grants` | |
| `hard_deletes` | [hard_deletes](https://docs.getdbt.com/reference/resource-configs/hard-deletes) |
| `meta` | Same pattern as other nodes |
| `persist_docs` | |
| `post_hook` | |
| `pre_hook` | |
| `schema` | |
| `snapshot_meta_column_names` | [snapshot_meta_column_names](https://docs.getdbt.com/reference/resource-configs/snapshot_meta_column_names) |
| `static_analysis` | Fusion |
| `strategy` | `timestamp` \| `check` |
| `tags` | |
| `unique_key` | |
| `updated_at` | For `strategy: timestamp` |

### Adapter-specific (union across adapters — snapshots)

The default allowlist **includes** every key in **Models § Adapter-specific** that adapter docs allow on **`config`** for snapshots (e.g. Redshift **`dist`**, **`sort`**, **`sort_type`**, **`query_group`**; Snowflake **`transient`**, **`cluster_by`**, **`query_tag`**, **`snowflake_warehouse`**; BigQuery **`partition_by`**, **`cluster_by`**, **`labels`**, **`kms_key_name`**, **`hours_to_expiration`**, **`grant_access_to`**). **Out of scope:** resolving the active adapter—use the same **union** as models.

## Macros — default keys under `config`

| Key | Notes |
| --- | --- |
| `docs` | Nested object (`show`); [macro properties](https://docs.getdbt.com/reference/macro-properties) |
| `meta` | |

## Exposures — default keys under `config`

| Key | Notes |
| --- | --- |
| `enabled` | [Exposure properties](https://docs.getdbt.com/reference/exposure-properties) (`config` block) |
| `meta` | |
| `tags` | |
