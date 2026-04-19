# Resource key allowlists

Fusion-oriented **fixed allowed keys** **per resource type** for `*-allowed-keys` hooks (see **`hooks.md`**). **`--forbidden`** can additionally ban keys from the default set for stricter projects.

**Related:** [`yaml-handling.md`](yaml-handling.md) (which YAML nodes hooks validate), [`hooks.md`](hooks.md) (CLI flags, exit codes, pre-commit selection).

Allowlists describe **keys on the resource object** the hook targets (e.g. each dict under `models:`), not wrapper keys like `models` itself.

## Models

**Source of truth (implementation):** `MODEL_ALLOWED_KEYS` in **`src/dbt_yaml_guardrails/resource_keys.py`**. The table below **must** mirror that constant; change the constant and this table together.

Default keys allowed on **each model entry** (under `models:`):

| Key | Notes |
| --- | --- |
| `name` | Always present for real models in dbt; do not list in `--required`. |
| `description` | |
| `columns` | |
| `data_tests` | As in Fusion / modern schema YAML naming. |
| `versions` | YAML-oriented; manifest may use `version`. |
| `latest_version` | |
| `version` | On manifest nodes. |
| `constraints` | |
| `docs` | |
| `config` | |

### Legacy / deprecated keys (reference only — not allowlisted)

Top-level keys that **used to appear** in schema YAML or still parse with warnings, but should be **migrated** rather than treated as first-class alongside the Fusion-oriented set above:

| Key | Notes |
| --- | --- |
| `tests` | Legacy alias for **`data_tests`**. [dbt model properties](https://docs.getdbt.com/reference/model-properties) lists it explicitly; use **`data_tests`**. |
| `meta` | Prefer **`config.meta`** on the model (and project defaults) so metadata follows the same inheritance as other config. Top-level / ad-hoc attributes on nodes are being tightened in dbt Core (see v1.10+ deprecations around custom top-level properties). |
| `tags` | Same pattern as **`meta`**: prefer **`config.tags`** (or `config` + inherited tags) rather than a bare top-level **`tags`** key on the model when standardizing new YAML. |

Other backwards-compatibility keys (e.g. top-level **`access`** only for compatibility) are documented in [model properties](https://docs.getdbt.com/reference/model-properties); they are also outside this hook’s default allowlist until explicitly added.

## Sources (each entry under `sources:`)

Fusion-oriented keys on **each source** object (table rows live under `tables`; see **Source tables**):

| Key | Notes |
| --- | --- |
| `name` | Required. |
| `description` | |
| `database` | |
| `schema` | |
| `loader` | |
| `config` | Includes `meta`, `tags`, freshness, `loaded_at_field`, etc. (per [source configs](https://docs.getdbt.com/reference/source-configs)). |
| `quoting` | |
| `tables` | Nested list; see **Source tables** below. |

### Legacy / deprecated keys (reference only — not allowlisted)

| Key | Notes |
| --- | --- |
| `tests` | Legacy alias for **`data_tests`** where dbt still accepts it; use **`data_tests`** (see [source properties](https://docs.getdbt.com/reference/source-properties)). |
| `meta` | Prefer **`config.meta`** on the source (see [source configs](https://docs.getdbt.com/reference/source-configs)). |
| `tags` | Prefer **`config.tags`**. |
| `overrides` | Deprecated in dbt v1.10+ in favor of **`config`** / [source configs](https://docs.getdbt.com/reference/source-configs); may still appear in older files. |

## Source tables (each entry under `sources: [].tables:`)

| Key | Notes |
| --- | --- |
| `name` | Required. |
| `description` | |
| `identifier` | |
| `data_tests` | |
| `config` | Per-table freshness, `meta`, `tags`, etc. |
| `quoting` | |
| `external` | External table metadata. |
| `columns` | |

### Legacy / deprecated keys (reference only — not allowlisted)

| Key | Notes |
| --- | --- |
| `tests` | Legacy alias for **`data_tests`**; use **`data_tests`** on tables and columns (see [source properties](https://docs.getdbt.com/reference/source-properties)). |
| `meta` | Prefer **`config.meta`** on the table (and column **`config`** where applicable). |
| `tags` | Prefer **`config.tags`**. |

## Seeds (each entry under `seeds:`)

| Key | Notes |
| --- | --- |
| `name` | Required. |
| `description` | |
| `config` | Seed configs, `docs`, etc. |
| `data_tests` | |
| `columns` | |

### Legacy / deprecated keys (reference only — not allowlisted)

| Key | Notes |
| --- | --- |
| `tests` | Legacy alias for **`data_tests`**; use **`data_tests`** ([seed properties](https://docs.getdbt.com/reference/seed-properties)). |
| `meta` | Prefer **`config.meta`**. |
| `tags` | Prefer **`config.tags`**. |

## Snapshots (each entry under `snapshots:`)

| Key | Notes |
| --- | --- |
| `name` | Required. |
| `description` | |
| `config` | Snapshot configs, `meta`, `docs`, etc. |
| `data_tests` | |
| `columns` | |

### Legacy / deprecated keys (reference only — not allowlisted)

| Key | Notes |
| --- | --- |
| `tests` | Legacy alias for **`data_tests`**; use **`data_tests`** ([snapshot properties](https://docs.getdbt.com/reference/snapshot-properties)). |
| `meta` | Prefer **`config.meta`**. |
| `tags` | Prefer **`config.tags`**. |

## Macros (each entry under `macros:`)

**Source of truth (implementation):** `MACRO_ALLOWED_KEYS` in **`src/dbt_yaml_guardrails/resource_keys.py`**. The table below **must** mirror that constant; change the constant and this table together.

| Key | Notes |
| --- | --- |
| `name` | Required. |
| `description` | |
| `config` | Often `docs`, `meta`. |
| `arguments` | List of argument defs (`name`, `type`, `description`, …). |

### Legacy / deprecated keys (reference only — not allowlisted)

| Key | Notes |
| --- | --- |
| `meta` | Prefer **`config.meta`** (macro [`docs`](https://docs.getdbt.com/reference/macro-properties) / resource config). |
| `tags` | Prefer **`config.tags`**. |

Macro property YAML does not use a **`tests`** / **`data_tests`** block at the macro node the way models do; do not confuse with model/column tests.

## Analyses (each entry under `analyses:`)

| Key | Notes |
| --- | --- |
| `name` | Required. |
| `description` | |
| `config` | `enabled`, `docs`, `tags`, etc. |
| `columns` | |

### Legacy / deprecated keys (reference only — not allowlisted)

| Key | Notes |
| --- | --- |
| `tests` | Legacy alias for **`data_tests`** where accepted; use **`data_tests`** ([analysis properties](https://docs.getdbt.com/reference/analysis-properties)). |
| `meta` | Prefer **`config.meta`**. |
| `tags` | Prefer **`config.tags`**. |

## Exposures (each entry under `exposures:`)

| Key | Notes |
| --- | --- |
| `name` | Required. |
| `description` | |
| `type` | e.g. `dashboard`, `notebook`, `analysis`, `ml`, `application`. |
| `url` | |
| `maturity` | |
| `enabled` | |
| `config` | `tags`, `meta`, `enabled`, etc. |
| `owner` | Object (`name`, `email`). |
| `depends_on` | List of refs / sources / metrics. |
| `label` | Display label. |

### Legacy / deprecated keys (reference only — not allowlisted)

| Key | Notes |
| --- | --- |
| `meta` | Prefer **`config.meta`** ([exposure properties](https://docs.getdbt.com/reference/exposure-properties); v1.10+ moved many knobs under **`config`**). |
| `tags` | Prefer **`config.tags`** unless following a documented top-level exception in dbt for your version. |

## Unit tests (each entry under `unit_tests:`)

| Key | Notes |
| --- | --- |
| `name` | Required. |
| `model` | Target model. |
| `given` | Inputs / fixtures. |
| `expect` | Expected output. |
| `config` | Optional (`meta`, `tags`, `enabled`, …). |
| `overrides` | Macro / vars / env for the test run. |
| `versions` | Versioned-model test selection. |

### Legacy / deprecated keys (reference only — not allowlisted)

Unit test property YAML is relatively new and still gains fields across dbt versions. Prefer the keys in the table above and **[unit test properties](https://docs.getdbt.com/reference/resource-properties/unit-tests)**; avoid ad-hoc top-level keys that are not documented. **`meta`** / **`tags`** belong under **`config`** when you need them.

Exact shapes follow [dbt property docs](https://docs.getdbt.com/reference/define-properties); extend these tables when Fusion or dbt adds new top-level keys.
