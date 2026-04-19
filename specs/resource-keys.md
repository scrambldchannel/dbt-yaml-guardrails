# Resource key allowlists

Canonical **fixed allowed keys** (Fusion-oriented / dbt property YAML) **per resource type**, for hooks such as **`model-allowed-keys`** in **`hooks.md`**. That hook uses this table as the only allowlist; **`--forbidden`** can additionally ban keys from this set for stricter projects.

**Related:** [`yaml-handling.md`](yaml-handling.md) (which YAML nodes hooks validate), [`hooks.md`](hooks.md) (CLI flags and behavior).

Allowlists describe **keys on the resource object** the hook targets (e.g. each dict under `models:`), not wrapper keys like `models` itself.

## Models

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
| `overrides` | Deprecated in dbt v1.10+; prefer `config`. |
| `tables` | Nested list; see **Source tables** below. |

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

## Seeds (each entry under `seeds:`)

| Key | Notes |
| --- | --- |
| `name` | Required. |
| `description` | |
| `config` | Seed configs, `docs`, etc. |
| `data_tests` | |
| `columns` | |

## Snapshots (each entry under `snapshots:`)

| Key | Notes |
| --- | --- |
| `name` | Required. |
| `description` | |
| `config` | Snapshot configs, `meta`, `docs`, etc. |
| `data_tests` | |
| `columns` | |

## Macros (each entry under `macros:`)

| Key | Notes |
| --- | --- |
| `name` | Required. |
| `description` | |
| `config` | Often `docs`, `meta`. |
| `arguments` | List of argument defs (`name`, `type`, `description`, …). |

## Analyses (each entry under `analyses:`)

| Key | Notes |
| --- | --- |
| `name` | Required. |
| `description` | |
| `config` | `enabled`, `docs`, `tags`, etc. |
| `columns` | |

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

Exact shapes follow [dbt property docs](https://docs.getdbt.com/reference/define-properties); extend these tables when Fusion or dbt adds new top-level keys.
