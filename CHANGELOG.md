# Changelog

All notable changes to this project are documented here. Versions match **git tags** and **`version`** in **`pyproject.toml`**. This project is distributed as a **pre-commit** Git repository, not via PyPI.

**Style (from 0.4.3 onward):** Each release summarizes **user-visible behavior**—new hooks, fixes, and breaking or notable spec changes. Unless a path is the point of the change, avoid inventorying file paths, module names, and test file lists; the **git diff** and **specs** are the source of truth for where code lives. Earlier entries may still read like internal release notes; new entries follow this rule.

## [Unreleased]

## [0.7.1](https://github.com/scrambldchannel/dbt-yaml-guardrails/releases) — 2026-04-26

### Added

- **`source-allowed-keys` and `--fix-legacy-yaml`:** v1 rewrites **`tests` → `data_tests`** on **table** rows under **`sources: → … → tables:`** and, when both nested checks are enabled, on each **column** dict under a table’s **`columns:`** list. Nested rewrites run **only** when the same flags that control validation are on: **`--check-source-tables`** for tables, and **`--check-source-table-columns`** for those columns (so turning off a nested check also skips the fix there). See **`fix-legacy-yaml.md`** and **`allowed-keys.md`**.

- **Release metadata:** `version` in `pyproject.toml` is **0.7.1**; copy-paste `rev:` examples should use **v0.7.1**.

## [0.7.0](https://github.com/scrambldchannel/dbt-yaml-guardrails/releases) — 2026-04-26

### Changed

- **Contributors and CI:** dev-only packages (pytest, pytest-cov, vulture) are declared in **`[dependency-groups].dev`** (PEP 735) as the single source of truth. Documentation and the GitHub workflow use **`uv sync`**, which includes that group by default. No change to hook behavior; consumers who only pin a pre-commit **`rev:`** are unaffected.

- **Release metadata:** `version` in `pyproject.toml` is **0.7.0**; copy-paste `rev:` examples should use **v0.7.0**.

## [0.6.0](https://github.com/scrambldchannel/dbt-yaml-guardrails/releases) — 2026-04-26

### Added

- **`source-allowed-keys`:** validates each **`sources: → … → tables:`** row and, by default, each table’s **`columns:`** list using the **`SOURCE_TABLE_*`** and **`SOURCE_TABLE_COLUMN_*`** allowlists. New flags **`--check-source-tables`** and **`--check-source-table-columns`** (default **`true`** each). If **`--check-source-tables`** is **`false`**, **`--check-source-table-columns`** must be **`false`** (otherwise exit **2**). When **`--check-config`** and **`--check-source-tables`** are on, each table’s **`config:`** is checked with the same key set as **`source-allowed-config-keys`**. First implementation: **validation-only** for nested table/column vs **`--fix-legacy-yaml`** rewrites. See **`specs/hook-families/allowed-keys.md`**.
- **`--fix-legacy-yaml`** (`true` / `false`, default `false`) on the six **`*-allowed-keys`** property-YAML CLIs (**`model`**, **`macro`**, **`seed`**, **`snapshot`**, **`exposure`**, **`source`**) and on **`*-allowed-column-keys`**: when enabled, applies rewrites in place, then runs validation: **`tests` → `data_tests`**, and top-level **`meta` / `tags` → `config`** on resource entries (no merge if **`config.meta` / `config.tags`** already exist). **`catalog-allowed-keys`** and **`dbt-project-allowed-keys`** do **not** take this flag. See [`specs/hook-families/allowed-keys.md`](specs/hook-families/allowed-keys.md) and [`specs/hook-families/fix-legacy-yaml.md`](specs/hook-families/fix-legacy-yaml.md).

### Removed

- **Standalone** **`fix-legacy-yaml`** console entry point and pre-commit **hook** **`id: fix-legacy-yaml`**. Use **`--fix-legacy-yaml` `true`** on a suitable **`*-allowed-keys`** or **`*-allowed-column-keys`** hook instead.

### Changed

- **Release metadata:** `version` in `pyproject.toml` is **0.6.0**; copy-paste `rev:` examples should use **v0.6.0**.

## [0.5.1](https://github.com/scrambldchannel/dbt-yaml-guardrails/releases) — 2026-04-25

### Changed

- **Release metadata:** `version` in `pyproject.toml` is **0.5.1**; copy-paste `rev:` examples should use **v0.5.1**.
- **`--check-nested` renamed to `--check-config`** on all `*-allowed-keys` hooks. The flag behaves identically — it controls whether direct keys under `config:` are validated — but the new name makes its purpose clearer.
- **`--check-columns` removed from `macro-`, `exposure-`, and `source-allowed-keys`**. Those hooks never had a `columns:` list to check, so the flag was silently ignored. It's now absent rather than a no-op. The flag remains fully functional on `model-`, `seed-`, and `snapshot-allowed-keys`.

## [0.5.0](https://github.com/scrambldchannel/dbt-yaml-guardrails/releases) — 2026-04-25

### Added

- **`*-allowed-column-keys`** (`model`, `seed`, `snapshot`): new hook family for enforcing which keys appear on column entries. Supports `--required` (e.g. mandate `description` on every column) and `--forbidden`. `name` in `--required` exits `2`. If `columns:` is absent the entry is skipped silently.
- **`--check-columns`** on `*-allowed-keys` (`model`, `seed`, `snapshot`): column key validation is now on by default, using the same allowlists as `*-allowed-column-keys`. Pass `--check-columns false` to disable. `macro`, `exposure`, and `source` accept the flag but it has no effect.
- **Column `config:` key** added to the allowlist for model, seed, and snapshot column entries, reflecting the dbt docs showing `config: { tags, meta }` is valid at the column level.

### Changed

- **Release metadata:** `version` in `pyproject.toml` is **0.5.0**; copy-paste `rev:` examples should use **v0.5.0**.
- **Sandbox hooks** moved out of the main `.pre-commit-config.yaml` into a dedicated `tests/hook_sandbox/.pre-commit-sandbox.yaml`. The `Makefile` target is now `make sandbox-hooks` (was `make sandbox`), which runs `pre-commit run --config … --files …` so no `stages: [manual]` or `files:` patterns are needed in the sandbox config.

## [0.4.4](https://github.com/scrambldchannel/dbt-yaml-guardrails/releases) — 2026-04-25

### Added

- **`--check-columns` on `model-`, `seed-`, and `snapshot-allowed-keys`**: by default each hook now also validates **direct keys on every column entry** (each item in `columns:`) against a new per-resource allowlist (`MODEL_COLUMN_ALLOWED_KEYS`, `SEED_COLUMN_ALLOWED_KEYS`, `SNAPSHOT_COLUMN_ALLOWED_KEYS`). Allowlists are documented in `specs/resource-keys.md` § Column keys. Column violations print as `{path}: {resource} '{name}': column '{col}': <detail>`, making them visually distinct from top-level and `config:` violations. Pass `--check-columns false` to restore pre-0.4.4 top-level-only behavior.
- **Legacy `tests` column key**: a column entry using `tests` instead of `data_tests` gets an actionable message (`Rename to \`data_tests\`…`) consistent with the top-level legacy key handling.
- **Shape errors** for malformed `columns:` values (`null` / non-list), non-mapping column entries, and column entries missing `name` exit `1` with a precise message (e.g. `model 'x': column at index 0 is missing 'name'`).
- **`--check-columns` accepted (no effect) on `macro-`, `exposure-`, and `source-allowed-keys`**: the flag is parsed and silently ignored so pre-commit configs that pass it globally do not error on hooks where `columns:` is out of scope.

### Changed

- **Release metadata:** `version` in `pyproject.toml` is **0.4.4**; copy-paste `rev:` examples should use **v0.4.4**.

## [0.4.3](https://github.com/scrambldchannel/dbt-yaml-guardrails/releases) — 2026-04-24

### Added

- **`catalog-allowed-keys`**: New hook to enforce the allowlisted top-level keys on each `catalogs:` entry (for dbt 1.10+ catalog / Iceberg write integration YAML). Includes YAML helpers to read catalog entries and a manual sandbox hook for local runs.
- **`dbt-project-allowed-keys`**: New hook to enforce the allowlisted top-level keys in `dbt_project.yml`, with a project-file loader that does not apply the “resource YAML `version: 2`” document rule to the project’s `version` key. The pre-commit hook is scoped to `dbt_project.yml` by default. Specs and docs were updated to describe the project file, hook behavior, and scope.

### Changed

- **Release and pins:** `pyproject.toml` is **0.4.3**; copy-paste **`rev:`** examples in the README, HOOKS, and related docs use **v0.4.3** for consumers pinning this release.

## [0.4.2](https://github.com/scrambldchannel/dbt-yaml-guardrails/releases) — 2026-04-23

### Fixed

- **`*-allowed-keys` default allowlists** (**`src/dbt_yaml_guardrails/hook_families/allowed_keys/resource_keys.py`**) now list only **top-level keys users can author in dbt property YAML** (per the dbt **resource properties** reference for each resource), **not** manifest-only fields (e.g. `original_file_path`, `package_name`, `relation_name`, `resource_type`, `unrendered_config`). Models use the [model properties](https://docs.getdbt.com/reference/model-properties) surface (including latest YAML fields such as `semantic_model`, `metrics`, `agg_time_dimension`, `primary_entity`); seeds, snapshots, macros, exposures, and sources match their respective dbt property docs. **`specs/resource-keys.md`**, **`specs/hook-families/allowed-keys.md`**, and **`specs/README.md`** describe the policy; the **Analyses** / **Unit tests** wide tables were replaced with a short note (no matching shipped hooks yet).

### Changed

- **Release metadata:** **`version`** in **`pyproject.toml`** is **0.4.2**; pre-commit **`rev:`** examples in **`README.md`**, **`HOOKS.md`**, **`specs/hook-families/meta-accepted-values.md`**, and **`specs/project-spec.md`** use **`v0.4.2`**.

## [0.4.1](https://github.com/scrambldchannel/dbt-yaml-guardrails/releases) — 2026-04-22

### Added

- **`source-allowed-meta-keys`**, **`source-meta-accepted-values`**, **`source-tags-accepted-values`**: same behavior as the other resource CLIs in those families, for **`sources:`** entries. **`[project.scripts]`**, **`.pre-commit-hooks.yaml`**, manual sandbox hooks, **`HOOKS.md`**, and family specs updated; tests and fixtures under **`tests/hook_families/`** and **`tests/fixtures/yaml/**`** per family.
- **`source-allowed-config-keys`**: top-level keys under each source’s **`config:`** mapping; default **`SOURCE_CONFIG_ALLOWED_KEYS`** in **`resource_config_keys.py`** (see **`specs/resource-config-keys.md`** § **Sources — default keys under `config`**). **`[project.scripts]`**, **`.pre-commit-hooks.yaml`**, sandbox **`dbtg-sandbox-source-allowed-config-keys`**, **`HOOKS.md`**, and **`specs/hook-families/allowed-config-keys.md`** updated. Tests: **`tests/hook_families/allowed_config_keys/test_source_allowed_config_keys.py`**, fixtures **`tests/fixtures/yaml/allowed_config_keys/sources/**`.
- **`source-allowed-keys`**: top-level keys on each **`sources:`** entry; default allowlist **`SOURCE_ALLOWED_KEYS`** in **`resource_keys.py`** (see **`specs/resource-keys.md`** § **Sources** / **Default allowlist (source-allowed-keys)**). **`[project.scripts]`**, **`.pre-commit-hooks.yaml`**, sandbox hook **`dbtg-sandbox-source-allowed-keys`**, **`HOOKS.md`**, and **`specs/hook-families/allowed-keys.md`** §6 updated. Tests: **`tests/hook_families/allowed_keys/test_source_allowed_keys.py`**, fixtures **`tests/fixtures/yaml/allowed_keys/sources/**`.
- **`yaml_handling`**: **`extract_source_entries`** and **`iter_source_entries`** for top-level **`sources:`** (keyed by each source’s **`name`**; nested **`tables:`** preserved on the entry). **`_extract_named_list_by_name`** accepts optional **`duplicate_name_kind`** so duplicate-**`name`** errors read **`Duplicate source name`** (not **`sourc`**). Spec: **`specs/yaml-handling.md`**; tests: **`tests/test_yaml_handling.py`**, fixtures **`tests/fixtures/yaml/allowed_keys/sources/**`.

### Changed

- **Release metadata:** **`version`** in **`pyproject.toml`** is **0.4.1**; pre-commit **`rev:`** examples in **`README.md`**, **`HOOKS.md`**, **`specs/hook-families/meta-accepted-values.md`**, and **`specs/project-spec.md`** use **`v0.4.1`**.

## [0.4.0](https://github.com/scrambldchannel/dbt-yaml-guardrails/releases) — 2026-04-22

> **Note:** This tag was an **administrative mistake**: the version was released before the intended work was on **`main`**, so **0.4.0** does **not** include the code that was meant to ship with it. Use **0.4.1** (section above) or later for the release that contains that work.

### Changed

- **Release metadata:** `**pyproject.toml**` `**version**` is **0.4.0**; pre-commit `**rev:**` examples in **`README.md`**, **`HOOKS.md`**, and **`specs/hook-families/meta-accepted-values.md`** use **`v0.4.0`**. No CLI or spec behavior change beyond the version pin—tag **v0.4.0** for consumers who track releases by git ref.

## [0.3.0](https://github.com/scrambldchannel/dbt-yaml-guardrails/releases) — 2026-04-21

### Added

- `**macro-meta-accepted-values**`: same behavior as the other `***-meta-accepted-values**` CLIs, for entries under `**macros:**` (`**--key**`, `**--values**`, optional `**--optional**`). Implementation: `**src/dbt_yaml_guardrails/hook_families/meta_accepted_values/macro_meta_accepted_values.py**`; `**[project.scripts]**`, `**.pre-commit-hooks.yaml**`, and docs/specs updated. Tests: `**tests/hook_families/meta_accepted_values/test_macro_meta_accepted_values.py**` and `**tests/fixtures/yaml/meta_accepted_values/macros/**`.
- `***-tags-accepted-values`** hooks (`**model**`, `**seed**`, `**snapshot**`, `**exposure**`, `**macro**`): validate `**config.tags**` (string or list of strings) against `**--values**` when `**tags**` is declared; missing `**config**` or `**tags**` passes (see `**specs/hook-families/tags-accepted-values.md**`). Implementation: `**src/dbt_yaml_guardrails/hook_families/tags_accepted_values/**`; `**[project.scripts]**`, `**.pre-commit-hooks.yaml**`, `**HOOKS.md**` example block, and `**specs/**` index updated.

### Changed

- **Tests**: `**tests/hook_families/tags_accepted_values/`** and `**tests/fixtures/yaml/tags_accepted_values/**` cover the tags family; `**tests/hook_families/meta_accepted_values/**` includes `**macro**` where applicable.

## [0.2.1](https://github.com/scrambldchannel/dbt-yaml-guardrails/releases) — 2026-04-21

### Changed

- `***-meta-accepted-values**`: the value at `**--key**` may be a **YAML list of strings** (flow or block list); **each** element must appear in `**--values`** after trim. Single-string leaves unchanged.
- **Spec**: `**specs/hook-families/meta-accepted-values.md`** — `**--values**` applies to **leaf** paths only (extend `**--key`** to reach a string field, e.g. `**owner.name**`); docs and hook descriptions updated accordingly.

## [0.2.0](https://github.com/scrambldchannel/dbt-yaml-guardrails/releases) — 2026-04-20

### Added

- `***-allowed-config-keys**` hooks (`**model**`, `**macro**`, `**seed**`, `**snapshot**`, `**exposure**`): validate **top-level keys under each entry’s `config:`** mapping against Fusion-oriented allowlists in `**specs/resource-config-keys.md**`, with `**--required**` / `**--forbidden**` (see `**specs/hook-families/allowed-config-keys.md**`). Implementation: `**src/dbt_yaml_guardrails/hook_families/allowed_config_keys/**` and `**resource_config_keys.py**`.
- **Specs & docs**: `**specs/resource-config-keys.md`** (config-key allowlists; split from top-level `**resource-keys.md**`), plus updates to `**HOOKS.md**`, `**specs/hooks.md**`, `**specs/README.md**`, and related hook-family specs so `**rev:**` and shipped hooks stay aligned.

### Changed

- **Tests**: `**tests/hook_families/allowed_config_keys/`** and `**tests/fixtures/yaml/allowed_config_keys/**` cover the new CLIs.

## [0.1.2](https://github.com/scrambldchannel/dbt-yaml-guardrails/releases) — 2026-04-19

### Added

- `***-meta-accepted-values**` hooks (`**model**`, `**seed**`, `**snapshot**`, `**exposure**`): validate a **string** leaf at a **dot path** under `**config.meta`** against a comma-separated `**--values**` allowlist, with optional `**--optional**` when the path may be absent (see `**specs/hook-families/meta-accepted-values.md**`).

### Changed

- **Packaging & docs**: `**[project.scripts]`** and `**.pre-commit-hooks.yaml**` entries for the new hooks; root `**README**`, `**specs/hooks.md**`, `**specs/README.md**`, and `**meta-accepted-values.md**` updated so the hook family and pre-commit `**rev:**` examples stay aligned.
- **Tests**: `**tests/hook_families/meta_accepted_values/`** and `**tests/fixtures/yaml/meta_accepted_values/**` cover the new CLIs (mirrors the `**models/**` scenarios for `**seeds/**`, `**snapshots/**`, `**exposures/**`).

## [0.1.1](https://github.com/scrambldchannel/dbt-yaml-guardrails/releases) — 2026-04-19

**First public release.** Use `**v0.1.1`** (or this commit) as the first tag intended for general pre-commit `**rev:**` pins.

**0.1.0** was a **pre-release** (internal / early tagging only); there is no separate feature delta from 0.1.0—the shipped behavior is described under the 0.1.0 section below.

## [0.1.0](https://github.com/scrambldchannel/dbt-yaml-guardrails/releases) — 2026-04-19 (pre-release)

> Not promoted as a public release; superseded by **0.1.1** for `**rev:`** pinning.

### Added

- `***-allowed-keys**` hooks for `**models**`, `**macros**`, `**seeds**`, `**snapshots**`, and `**exposures**`: validate top-level keys on each resource entry against Fusion-oriented allowlists in `**specs/resource-keys.md**` (with `**--required**` / `**--forbidden**`).
- `***-allowed-meta-keys**` hooks for `**models**`, `**seeds**`, `**snapshots**`, `**exposures**`, and `**macros**`: validate keys under `**config.meta**` with optional `**--allowed**`, plus `**--required**` / `**--forbidden**`.
- Shared YAML loading and parsing (`**yaml_handling**`) per `**specs/yaml-handling.md**`.
- MIT license; `**pyproject.toml**` metadata (authors, URLs, keywords, classifiers) for tooling and documentation.
