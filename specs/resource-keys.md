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

## Other resource types

Add sections here (e.g. **Sources**, **Macros**) as hooks and defaults are defined. Nested shapes (`sources` → `tables`) may use subsections or separate tables per node type.
