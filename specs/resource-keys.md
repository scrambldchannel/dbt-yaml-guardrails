# Resource key allowlists

Fusion-oriented **fixed allowed keys** **per resource type** for **`dbt-*-allowed-keys`** hooks (see **`hook-families/allowed-keys.md`** and **`hooks.md`**). **`--forbidden`** can additionally ban keys from the default set for stricter projects.

**Related:** [`yaml-handling.md`](yaml-handling.md), [`hook-families/allowed-keys.md`](hook-families/allowed-keys.md), [`hooks.md`](hooks.md).

Allowlists describe **keys on the resource object** the hook targets (e.g. each dict under `models:`), not wrapper keys like `models` itself.

For keys **inside** each entry’s **`config:`** mapping ( **`*-allowed-config-keys`** ), see **[`resource-config-keys.md`](resource-config-keys.md)**.

## Models

| Key | Notes |
| --- | --- |
| `access` | [access](https://docs.getdbt.com/reference/resource-configs/access) |
| `alias` | |
| `build` | [build](https://docs.getdbt.com/reference/resource-configs/build) |
| `columns` | |
| `config` | |
| `constraints` | |
| `data_tests` | |
| `deprecation_date` | [deprecation_date](https://docs.getdbt.com/reference/resource-properties/deprecation_date) |
| `description` | |
| `docs` | Nested object (`show`); [model properties](https://docs.getdbt.com/reference/model-properties) |
| `latest_version` | [latest_version](https://docs.getdbt.com/reference/resource-properties/latest_version) |
| `name` | |
| `original_file_path` | |
| `package_name` | |
| `patch_path` | |
| `relation_name` | |
| `resource_type` | |
| `time_spine` | [time_spine](https://docs.getdbt.com/reference/model-properties#time_spine) |
| `tests` | Legacy alias for `data_tests` |
| `unrendered_config` | |
| `versions` | |

### Legacy / deprecated (top-level keys)

| Key | Notes | Suggested violation detail |
| --- | --- | --- |
| `sources` | Deprecated in favor of **`exposures`** + `sources`. | [sources](https://docs.getdbt.com/reference/model-properties#sources) |

## Seeds

| Key | Notes |
| --- | --- |
| `access` | [access](https://docs.getdbt.com/reference/resource-configs/access) |
| `alias` | |
| `build` | |
| `columns` | |
| `config` | |
| `data_tests` | |
| `deprecation_date` | |
| `description` | |
| `docs` | Nested object (`show`); [seed properties](https://docs.getdbt.com/reference/seed-properties) |
| `latest_version` | |
| `name` | |
| `original_file_path` | |
| `package_name` | |
| `patch_path` | |
| `relation_name` | |
| `resource_type` | |
| `tests` | Legacy alias for `data_tests` |
| `unrendered_config` | |
| `versions` | |

### Legacy / deprecated (top-level keys)

| Key | Notes | Suggested violation detail |
| --- | --- | --- |
| `sources` | Deprecated in favor of **`exposures`** + `sources`. | [sources](https://docs.getdbt.com/reference/seed-properties#sources) |

## Snapshots

| Key | Notes |
| --- | --- |
| `access` | [access](https://docs.getdbt.com/reference/resource-configs/access) |
| `alias` | |
| `build` | |
| `columns` | |
| `config` | |
| `data_tests` | |
| `deprecation_date` | |
| `description` | |
| `docs` | Nested object (`show`); [snapshot properties](https://docs.getdbt.com/reference/snapshot-properties) |
| `latest_version` | |
| `name` | |
| `original_file_path` | |
| `package_name` | |
| `patch_path` | |
| `relation_name` | |
| `resource_type` | |
| `tests` | Legacy alias for `data_tests` |
| `unrendered_config` | |
| `versions` | |

### Legacy / deprecated (top-level keys)

| Key | Notes | Suggested violation detail |
| --- | --- | --- |
| `sources` | Deprecated in favor of **`exposures`** + `sources`. | [sources](https://docs.getdbt.com/reference/snapshot-properties#sources) |

## Macros

| Key | Notes |
| --- | --- |
| `access` | [access](https://docs.getdbt.com/reference/resource-configs/access) |
| `alias` | |
| `build` | |
| `columns` | |
| `config` | |
| `data_tests` | |
| `deprecation_date` | |
| `description` | |
| `docs` | Nested object (`show`); [macro properties](https://docs.getdbt.com/reference/macro-properties) |
| `latest_version` | |
| `name` | |
| `original_file_path` | |
| `package_name` | |
| `patch_path` | |
| `relation_name` | |
| `resource_type` | |
| `tests` | Legacy alias for `data_tests` |
| `unrendered_config` | |
| `versions` | |

### Legacy / deprecated (top-level keys)

| Key | Notes | Suggested violation detail |
| --- | --- | --- |
| `sources` | Deprecated in favor of **`exposures`** + `sources`. | [sources](https://docs.getdbt.com/reference/macro-properties#sources) |

## Exposures

| Key | Notes |
| --- | --- |
| `access` | [access](https://docs.getdbt.com/reference/resource-configs/access) |
| `alias` | |
| `build` | |
| `columns` | |
| `config` | |
| `data_tests` | |
| `deprecation_date` | |
| `description` | |
| `docs` | Nested object (`show`); [exposure properties](https://docs.getdbt.com/reference/exposure-properties) |
| `latest_version` | |
| `name` | |
| `original_file_path` | |
| `package_name` | |
| `patch_path` | |
| `relation_name` | |
| `resource_type` | |
| `tests` | Legacy alias for `data_tests` |
| `unrendered_config` | |
| `versions` | |

### Legacy / deprecated (top-level keys)

| Key | Notes | Suggested violation detail |
| --- | --- | --- |
| `sources` | Deprecated in favor of **`exposures`** + `sources`. | [sources](https://docs.getdbt.com/reference/exposure-properties#sources) |

## Sources

| Key | Notes |
| --- | --- |
| `access` | [access](https://docs.getdbt.com/reference/resource-configs/access) |
| `alias` | |
| `build` | |
| `columns` | |
| `config` | |
| `data_tests` | |
| `database` | [database](https://docs.getdbt.com/reference/resource-properties/database) |
| `deprecation_date` | |
| `description` | |
| `docs` | Nested object (`show`); [source properties](https://docs.getdbt.com/reference/source-properties) |
| `latest_version` | |
| `loader` | [loader](https://docs.getdbt.com/reference/resource-properties/loader) |
| `name` | |
| `original_file_path` | |
| `package_name` | |
| `patch_path` | |
| `quoting` | [quoting](https://docs.getdbt.com/reference/resource-properties/quoting) |
| `relation_name` | |
| `resource_type` | |
| `schema` | [schema](https://docs.getdbt.com/reference/resource-properties/schema) |
| `tables` | List of table definitions; [source properties](https://docs.getdbt.com/reference/source-properties) |
| `tests` | Legacy alias for `data_tests` |
| `unrendered_config` | |
| `versions` | |

### Default allowlist (`source-allowed-keys`)

The frozen set **`SOURCE_ALLOWED_KEYS`** in **`src/dbt_yaml_guardrails/hook_families/allowed_keys/resource_keys.py`** (used by **`source-allowed-keys`**) is the dbt-typical subset: **`columns`**, **`config`**, **`data_tests`**, **`database`**, **`description`**, **`loader`**, **`name`**, **`quoting`**, **`schema`**, **`tables`**. Other top-level keys in the table above may be allowed or called out as legacy; extend **`SOURCE_ALLOWED_KEYS`** and this subsection together when broadening the hook’s defaults.

### Legacy / deprecated (top-level keys)

| Key | Notes | Suggested violation detail |
| --- | --- | --- |
| `meta` | Prefer **`config.meta`**. | Use `config.meta` instead of top-level `meta`. |
| `overrides` | Deprecated in dbt v1.10+ for sources. | Remove `overrides` (deprecated in dbt v1.10+); use other source configuration. |
| `sources` | Deprecated in favor of **`exposures`** + `sources`. | [sources](https://docs.getdbt.com/reference/source-properties#sources) |
| `tags` | Prefer **`config.tags`**. | Use `config.tags` instead of top-level `tags`. |
| `tests` | Use **`data_tests`**. | Rename to `data_tests` (legacy alias `tests` is deprecated). |

## Analyses

| Key | Notes |
| --- | --- |
| `access` | [access](https://docs.getdbt.com/reference/resource-configs/access) |
| `alias` | |
| `build` | |
| `columns` | |
| `config` | |
| `data_tests` | |
| `deprecation_date` | |
| `description` | |
| `docs` | Nested object (`show`); [analysis properties](https://docs.getdbt.com/reference/analysis-properties) |
| `latest_version` | |
| `name` | |
| `original_file_path` | |
| `package_name` | |
| `patch_path` | |
| `relation_name` | |
| `resource_type` | |
| `tests` | Legacy alias for `data_tests` |
| `unrendered_config` | |
| `versions` | |

### Legacy / deprecated (top-level keys)

| Key | Notes | Suggested violation detail |
| --- | --- | --- |
| `sources` | Deprecated in favor of **`exposures`** + `sources`. | [sources](https://docs.getdbt.com/reference/analysis-properties#sources) |

## Unit tests

| Key | Notes |
| --- | --- |
| `access` | [access](https://docs.getdbt.com/reference/resource-configs/access) |
| `alias` | |
| `build` | |
| `columns` | |
| `config` | |
| `data_tests` | |
| `deprecation_date` | |
| `description` | |
| `docs` | Nested object (`show`); [unit test properties](https://docs.getdbt.com/reference/unit-test-properties) |
| `latest_version` | |
| `name` | |
| `original_file_path` | |
| `package_name` | |
| `patch_path` | |
| `relation_name` | |
| `resource_type` | |
| `tests` | Legacy alias for `data_tests` |
| `unrendered_config` | |
| `versions` | |

### Legacy / deprecated (top-level keys)

| Key | Notes | Suggested violation detail |
| --- | --- | --- |
| `sources` | Deprecated in favor of **`exposures`** + `sources`. | [sources](https://docs.getdbt.com/reference/unit-test-properties#sources) |

When new resource types or Fusion keys are added, extend these tables and **`resource_keys.py`** (or a sibling module) so the implementation and hook behavior stay aligned.
