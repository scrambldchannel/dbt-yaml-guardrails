# Resource key allowlists

**`*-allowed-keys`** hooks use **default allowlists of top-level keys** users may author: in **property YAML** (per dbt’s **resource properties** reference for each type), or in **`dbt_project.yml`** (per the [dbt project file](https://docs.getdbt.com/reference/dbt_project.yml) reference), depending on the hook. The lists **intentionally omit manifest / artifact-only** fields (e.g. `original_file_path`, `package_name`, `relation_name`, `resource_type`, `unrendered_config`) that appear on nodes in `manifest.json` but are not written in YAML.

**Related:** [`yaml-handling.md`](yaml-handling.md), [`hook-families/allowed-keys.md`](hook-families/allowed-keys.md), [`hook-families/fix-legacy-yaml.md`](hook-families/fix-legacy-yaml.md) (normative **example** layout for v2 top-level `meta` / `tags` → `config` on resource entries), [`hooks.md`](hooks.md).

For **property YAML**, allowlists target **keys on each resource entry** (e.g. each dict under `models:`), not wrapper keys like `models`. For the **dbt project file**, the allowlist targets **top-level keys of the root mapping** only (see **§ dbt project file**). For keys **inside** `config:` on resource entries, see **[`resource-config-keys.md`](resource-config-keys.md)**. For keys on **column entries** (items in each resource's `columns:` list), see **§ Column keys** under the applicable resource section below (currently: **Models**, **Seeds**, **Snapshots**). Legacy top-level `meta` / `tags` are listed per resource in **§ Legacy / deprecated** and implemented as `*_LEGACY_KEY_MESSAGES` in **`resource_keys.py`**; the **[`fix-legacy-yaml.md`](hook-families/fix-legacy-yaml.md)** spec defines matching **example YAML** conventions for the *fixed* shape (`config.meta` / `config.tags`) in **§ v2: top-level `meta` and `tags` → `config` (resource entries)**.

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

### Column keys (`model-allowed-keys --check-columns`)

[Column properties](https://docs.getdbt.com/reference/resource-properties/columns) — keys on each item in a model's `columns:` list. `meta` and `tags` may appear **either** directly on the column entry **or** nested under a column-level `config:` block (dbt supports both). `config` child keys on column entries are **not** validated by this hook (out of scope). **`tests`** is legacy; use `data_tests`.

> **Stability note:** This column key surface targets **dbt Fusion and the latest dbt Core versions** (1.10+). The allowed set may grow as dbt adds or formalises column-level properties. When dbt deprecates or renames a column key, add a row to the **Legacy / deprecated** table below and a matching entry in **`MODEL_COLUMN_LEGACY_KEY_MESSAGES`** rather than removing the key from the allowlist immediately.

| Key | Notes |
| --- | --- |
| `config` | Column-level config block; `tags` and `meta` may nest here instead of (or alongside) the top-level equivalents |
| `constraints` | [Column constraints](https://docs.getdbt.com/reference/resource-properties/constraints) (dbt 1.5+) |
| `data_tests` | Column-level tests |
| `data_type` | Data type hint |
| `description` | |
| `granularity` | [Time spine granularity](https://docs.getdbt.com/docs/build/metricflow-time-spine) — time dimension for metrics on this column |
| `meta` | Column-level metadata (top-level on column entry; use `*-allowed-meta-keys` to constrain key names inside `meta`) |
| `name` | Required; identifies the column |
| `quote` | Whether to quote the column identifier in generated SQL |
| `tags` | Column-level tags (top-level on column entry) |
| `tests` | Legacy alias for `data_tests` — **not** in `MODEL_COLUMN_ALLOWED_KEYS` |

#### Default allowlist (`MODEL_COLUMN_ALLOWED_KEYS`)

**`MODEL_COLUMN_ALLOWED_KEYS`** in **`src/dbt_yaml_guardrails/hook_families/allowed_keys/resource_keys.py`** matches the table above **except** `tests`. Legacy keys are handled via **`MODEL_COLUMN_LEGACY_KEY_MESSAGES`**.

#### Legacy / deprecated (column keys)

| Key | Notes | Suggested violation detail |
| --- | --- | --- |
| `tests` | Legacy alias for `data_tests`. | Rename to `data_tests` (legacy alias `tests` is deprecated). |

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

### Column keys (`seed-allowed-keys --check-columns`)

[Seed column properties](https://docs.getdbt.com/reference/seed-properties#columns) — keys on each item in a seed's `columns:` list. Seeds do not have a time-spine `granularity` dimension; otherwise column keys mirror models. `meta` and `tags` may appear directly on the column entry or under a column-level `config:` block; `config` child keys on column entries are not validated. **`tests`** is legacy.

> **Stability note:** Targets **dbt Fusion and the latest dbt Core versions**. Update this table (and **`SEED_COLUMN_ALLOWED_KEYS`** / **`SEED_COLUMN_LEGACY_KEY_MESSAGES`**) as the dbt column-property surface evolves.

| Key | Notes |
| --- | --- |
| `config` | Column-level config block; `tags` and `meta` may nest here |
| `constraints` | Column constraints (dbt 1.5+) |
| `data_tests` | Column-level tests |
| `data_type` | |
| `description` | |
| `meta` | Column-level metadata (top-level on column entry) |
| `name` | Required |
| `quote` | |
| `tags` | Column-level tags (top-level on column entry) |
| `tests` | Legacy alias for `data_tests` — **not** in `SEED_COLUMN_ALLOWED_KEYS` |

#### Default allowlist (`SEED_COLUMN_ALLOWED_KEYS`)

**`SEED_COLUMN_ALLOWED_KEYS`** matches the table above **except** `tests`. Legacy keys: **`SEED_COLUMN_LEGACY_KEY_MESSAGES`**.

#### Legacy / deprecated (column keys)

| Key | Notes | Suggested violation detail |
| --- | --- | --- |
| `tests` | Legacy alias for `data_tests`. | Rename to `data_tests` (legacy alias `tests` is deprecated). |

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

### Column keys (`snapshot-allowed-keys --check-columns`)

[Snapshot column properties](https://docs.getdbt.com/reference/snapshot-properties#columns) — keys on each item in a snapshot's `columns:` list. Same surface as seeds (no `granularity`). `meta` and `tags` may appear directly on the column entry or under a column-level `config:` block; `config` child keys on column entries are not validated.

> **Stability note:** Targets **dbt Fusion and the latest dbt Core versions**. Update this table (and **`SNAPSHOT_COLUMN_ALLOWED_KEYS`** / **`SNAPSHOT_COLUMN_LEGACY_KEY_MESSAGES`**) as the dbt column-property surface evolves.

| Key | Notes |
| --- | --- |
| `config` | Column-level config block; `tags` and `meta` may nest here |
| `constraints` | Column constraints (dbt 1.5+) |
| `data_tests` | Column-level tests |
| `data_type` | |
| `description` | |
| `meta` | Column-level metadata (top-level on column entry) |
| `name` | Required |
| `quote` | |
| `tags` | Column-level tags (top-level on column entry) |
| `tests` | Legacy alias for `data_tests` — **not** in `SNAPSHOT_COLUMN_ALLOWED_KEYS` |

#### Default allowlist (`SNAPSHOT_COLUMN_ALLOWED_KEYS`)

**`SNAPSHOT_COLUMN_ALLOWED_KEYS`** matches the table above **except** `tests`. Legacy keys: **`SNAPSHOT_COLUMN_LEGACY_KEY_MESSAGES`**.

#### Legacy / deprecated (column keys)

| Key | Notes | Suggested violation detail |
| --- | --- | --- |
| `tests` | Legacy alias for `data_tests`. | Rename to `data_tests` (legacy alias `tests` is deprecated). |

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

## Catalogs

dbt Core **1.10+** [parses `catalogs.yml`](https://docs.getdbt.com/docs/dbt-versions/core-upgrade/upgrading-to-v1.10) and related property YAML. Top-level list keys on each `catalogs:` item follow the dbt/adapter [write catalog](https://github.com/dbt-labs/dbt-adapters/blob/main/docs/guides/write_catalog.md) pattern (and examples in the [v1.10 upgrade](https://docs.getdbt.com/docs/dbt-versions/core-upgrade/upgrading-to-v1.10) note). This hook validates only **catalog-row** top-level keys, not the nested **`write_integrations:`** list items (those are integration configs, not catalog entries).

| Key | Notes |
| --- | --- |
| `active_write_integration` | Optional; which named write integration to use (defaults to the only one, if applicable) |
| `name` | |
| `write_integrations` | List of write integration definitions |

### Default allowlist (`catalog-allowed-keys`)

**`CATALOG_ALLOWED_KEYS`** is exactly the table above. There is no legacy top-level key map for catalogs yet; **`CATALOG_LEGACY_KEY_MESSAGES`** is empty. **`--forbidden`** can still ban keys in the set.

## dbt project file (`dbt_project.yml`)

[dbt_project.yml](https://docs.getdbt.com/reference/dbt_project.yml) — the **required** project configuration file. dbt Core **1.10+** adds [stricter validation](https://github.com/dbt-labs/dbt-core) of this file (for example JSON Schema–based checks). The table below is the **documented** top-level key set for **`dbt-project-allowed-keys`** (see **`hook-families/allowed-keys.md`** §8); it is **not** a byte-for-byte copy of dbt’s internal schema—when dbt adds or renames keys, update this section and **`DBT_PROJECT_ALLOWED_KEYS`** together.

| Key | Notes |
| --- | --- |
| `name` | Project name (snake_case) |
| `config-version` | Should be **`2`** per dbt |
| `version` | [Project version](https://docs.getdbt.com/reference/project-configs/version) (package / semver semantics)—**not** resource YAML `version: 2` |
| `profile` | Profile name for `profiles.yml` |
| `model-paths` | |
| `seed-paths` | |
| `test-paths` | |
| `analysis-paths` | |
| `macro-paths` | |
| `snapshot-paths` | |
| `docs-paths` | |
| `asset-paths` | |
| `function-paths` | |
| `packages-install-path` | |
| `clean-targets` | |
| `query-comment` | |
| `require-dbt-version` | |
| `flags` | [Project flags](https://docs.getdbt.com/reference/global-configs/project-flags) |
| `dbt-cloud` | dbt Cloud / CLI integration (e.g. `project-id`) |
| `analyses` | Project-level analysis configs (dbt **v1.12+** may require a flag; see dbt docs) |
| `exposures` | |
| `quoting` | Includes adapter-specific subkeys (e.g. **`snowflake_ignore_case`** is **Fusion-only** on `quoting`) |
| `metrics` | |
| `models` | Hierarchical model configs—**values** are not validated by **`dbt-project-allowed-keys`** |
| `seeds` | |
| `semantic-models` | |
| `saved-queries` | |
| `snapshots` | |
| `sources` | |
| `data_tests` | |
| `vars` | |
| `on-run-start` | |
| `on-run-end` | |
| `dispatch` | |
| `restrict-access` | |
| `functions` | |

### Default allowlist (`dbt-project-allowed-keys`)

**`DBT_PROJECT_ALLOWED_KEYS`** in **`src/dbt_yaml_guardrails/hook_families/allowed_keys/resource_keys.py`** **SHOULD** match the table above. **`DBT_PROJECT_LEGACY_KEY_MESSAGES`** **MAY** map deprecated top-level keys (e.g. keys dbt still parses but recommends renaming) to actionable messages. **`--forbidden`** can still ban keys in the set.

### Legacy / deprecated (top-level keys)

Add rows here as dbt deprecates or renames project-file keys; until then this subsection may be empty.

## Analyses, unit tests

This repository does not ship `analysis-allowed-keys` or `unit-test-allowed-keys`. For [analysis](https://docs.getdbt.com/reference/analysis-properties) and [unit test](https://docs.getdbt.com/reference/unit-test-properties) property YAML, use the dbt reference for authorable top-level keys; do not assume the wide “node field” lists from older revisions of this spec (manifest overlap).

## Manifest-only fields (not in default allowlists)

Fields such as `original_file_path`, `package_name`, `patch_path`, `relation_name`, `resource_type`, and `unrendered_config` appear on **nodes in `manifest.json`**. They are **not** part of the default `*_ALLOWED_KEYS` sets—users do not author them in property YAML.

When dbt’s published **resource property** or **project file** surface grows, update **`src/dbt_yaml_guardrails/hook_families/allowed_keys/resource_keys.py`** and the **user-authorable** tables in this document together.
