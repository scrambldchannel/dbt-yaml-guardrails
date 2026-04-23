# Resource key allowlists

**`*-allowed-keys`** hooks use a **default allowlist of top-level keys users may author in property YAML** (per dbt’s **resource properties** reference for each type). The lists **intentionally omit manifest / artifact-only** fields (e.g. `original_file_path`, `package_name`, `relation_name`, `resource_type`, `unrendered_config`) that appear on nodes in `manifest.json` but are not written in `schema.yml`-style files.

**Related:** [`yaml-handling.md`](yaml-handling.md), [`hook-families/allowed-keys.md`](hook-families/allowed-keys.md), [`hooks.md`](hooks.md).

Allowlists target **keys on each resource entry** (e.g. each dict under `models:`), not wrapper keys like `models`. For keys **inside** `config:`, see **[`resource-config-keys.md`](resource-config-keys.md)**.

**`--forbidden`** can still ban keys that appear in a default allowlist if your policy is stricter than dbt’s surface area.

## Models

[Model properties](https://docs.getdbt.com/reference/model-properties) (available top-level + latest YAML / Fusion fields from that page: `agg_time_dimension`, `primary_entity`, `semantic_model`, `metrics`).

| Key | Notes |
| --- | --- |
| `access` | [access](https://docs.getdbt.com/reference/resource-configs/access) (top-level for compatibility) |
| `agg_time_dimension` | Latest YAML / Fusion; default time dimension for metrics |
| `columns` | |
| `config` | `docs` / `access` for the model are typically **under** `config` per dbt |
| `constraints` | |
| `data_tests` | |
| `deprecation_date` | [deprecation_date](https://docs.getdbt.com/reference/resource-properties/deprecation_date) |
| `description` | |
| `latest_version` | |
| `metrics` | [Metric properties](https://docs.getdbt.com/reference/metric-properties) |
| `name` | |
| `primary_entity` | Latest YAML / Fusion |
| `semantic_model` | [Semantic model properties](https://docs.getdbt.com/reference/semantic-model-properties) |
| `time_spine` | [Time spine](https://docs.getdbt.com/docs/build/metricflow-time-spine) |
| `versions` | |
| `tests` | Legacy alias for `data_tests` — **not** in `MODEL_ALLOWED_KEYS` (use legacy message) |

### Default allowlist (`model-allowed-keys`)

**`MODEL_ALLOWED_KEYS`** in **`src/dbt_yaml_guardrails/hook_families/allowed_keys/resource_keys.py`** matches the authorable table above **except** **`tests`**. **Legacy / deprecated** keys are **out** of the set unless handled via **`MODEL_LEGACY_KEY_MESSAGES`**. **`--forbidden`** can still block keys that are in the set.

### Legacy / deprecated (top-level keys)

| Key | Notes | Suggested violation detail |
| --- | --- | --- |
| `sources` | Deprecated in favor of **`exposures`** + `sources`. | [sources](https://docs.getdbt.com/reference/model-properties#sources) |

## Seeds

[Seed properties](https://docs.getdbt.com/reference/seed-properties).

| Key | Notes |
| --- | --- |
| `columns` | |
| `config` | includes `docs` (show / node color) per dbt |
| `data_tests` | |
| `description` | |
| `name` | |
| `tests` | Legacy — **not** in `SEED_ALLOWED_KEYS` |

### Default allowlist (`seed-allowed-keys`)

**`SEED_ALLOWED_KEYS`** matches the table above **except** **`tests`**. See **`SEED_LEGACY_KEY_MESSAGES`** in **`resource_keys.py`**.

### Legacy / deprecated (top-level keys)

| Key | Notes | Suggested violation detail |
| --- | --- | --- |
| `sources` | Deprecated in favor of **`exposures`** + `sources`. | [sources](https://docs.getdbt.com/reference/seed-properties#sources) |

## Snapshots

[Snapshot properties](https://docs.getdbt.com/reference/snapshot-properties).

| Key | Notes |
| --- | --- |
| `columns` | |
| `config` | |
| `data_tests` | |
| `description` | |
| `name` | |
| `tests` | Legacy — **not** in `SNAPSHOT_ALLOWED_KEYS` |

### Default allowlist (`snapshot-allowed-keys`)

**`SNAPSHOT_ALLOWED_KEYS`** matches the table above **except** **`tests`**. See **`resource_keys.py`**.

### Legacy / deprecated (top-level keys)

| Key | Notes | Suggested violation detail |
| --- | --- | --- |
| `sources` | Deprecated in favor of **`exposures`** + `sources`. | [sources](https://docs.getdbt.com/reference/snapshot-properties#sources) |

## Macros

[Macro properties](https://docs.getdbt.com/reference/macro-properties).

| Key | Notes |
| --- | --- |
| `arguments` | |
| `config` | |
| `description` | |
| `name` | |
| `tests` | Legacy — **not** in `MACRO_ALLOWED_KEYS` |

### Default allowlist (`macro-allowed-keys`)

**`MACRO_ALLOWED_KEYS`** matches the table above **except** **`tests`**. See **`resource_keys.py`**.

### Legacy / deprecated (top-level keys)

| Key | Notes | Suggested violation detail |
| --- | --- | --- |
| `sources` | Deprecated in favor of **`exposures`** + `sources`. | [sources](https://docs.getdbt.com/reference/macro-properties#sources) |

## Exposures

[Exposure properties](https://docs.getdbt.com/reference/exposure-properties).

| Key | Notes |
| --- | --- |
| `config` | `meta` / `tags` under `config` in modern dbt |
| `depends_on` | |
| `description` | |
| `enabled` | |
| `label` | |
| `maturity` | |
| `name` | |
| `owner` | |
| `type` | required (dashboard, notebook, …) |
| `url` | |
| `tests` | Legacy — **not** in `EXPOSURE_ALLOWED_KEYS` |

### Default allowlist (`exposure-allowed-keys`)

**`EXPOSURE_ALLOWED_KEYS`** matches the table above **except** **`tests`**. See **`resource_keys.py`**.

### Legacy / deprecated (top-level keys)

| Key | Notes | Suggested violation detail |
| --- | --- | --- |
| `sources` | Deprecated in favor of **`exposures`** + `sources`. | [sources](https://docs.getdbt.com/reference/exposure-properties#sources) |

## Sources

[Source properties](https://docs.getdbt.com/reference/source-properties).

| Key | Notes |
| --- | --- |
| `config` | `meta` / `tags` / freshness under `config` in modern dbt |
| `database` | |
| `description` | |
| `loader` | |
| `name` | |
| `quoting` | |
| `schema` | |
| `tables` | table definitions; columns and `data_tests` live **under** `tables` |

### Default allowlist (`source-allowed-keys`)

**`SOURCE_ALLOWED_KEYS`** is exactly the table above. Deprecated top-level `meta` / `tags` / `overrides` and legacy `tests` are **out** of the set; see **`SOURCE_LEGACY_KEY_MESSAGES`**. **`--forbidden`** can still ban keys in the set.

### Legacy / deprecated (top-level keys)

| Key | Notes | Suggested violation detail |
| --- | --- | --- |
| `meta` | Prefer **`config.meta`**. | Use `config.meta` instead of top-level `meta`. |
| `overrides` | Deprecated in dbt v1.10+ for sources. | Remove `overrides` (deprecated in dbt v1.10+); use other source configuration. |
| `sources` | Deprecated in favor of **`exposures`** + `sources`. | [sources](https://docs.getdbt.com/reference/source-properties#sources) |
| `tags` | Prefer **`config.tags`**. | Use `config.tags` instead of top-level `tags`. |
| `tests` | Use **`data_tests`**. | Rename to `data_tests` (legacy alias `tests` is deprecated). |

## Analyses, unit tests

This repository does not ship `analysis-allowed-keys` or `unit-test-allowed-keys`. For [analysis](https://docs.getdbt.com/reference/analysis-properties) and [unit test](https://docs.getdbt.com/reference/unit-test-properties) property YAML, use the dbt reference for authorable top-level keys; do not assume the wide “node field” lists from older revisions of this spec (manifest overlap).

## Manifest-only fields (not in default allowlists)

Fields such as `original_file_path`, `package_name`, `patch_path`, `relation_name`, `resource_type`, and `unrendered_config` appear on **nodes in `manifest.json`**. They are **not** part of the default `*_ALLOWED_KEYS` sets—users do not author them in property YAML.

When dbt’s published property surface grows (new top-level resource keys in the official reference), update **`src/dbt_yaml_guardrails/hook_families/allowed_keys/resource_keys.py`** and the **user-authorable** tables in this document together.
