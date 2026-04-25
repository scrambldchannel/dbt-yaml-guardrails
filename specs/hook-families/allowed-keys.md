# Hook family: `*-allowed-keys`

Keys on each resource entry in **dbt property YAML** (e.g. `schema.yml` under model paths) **or** top-level keys on the **project root mapping** in **`dbt_project.yml`**, depending on the hook. **By default**, property-YAML hooks also validate **direct keys under `config:`** (see **§ Nested keys (`config`) and `--check-nested`**). Umbrella packaging and the list of families live in **[`../hooks.md`](../hooks.md)**.

**Exit codes** for `*-allowed-keys` CLIs **SHOULD** be:

+ **`0`** — every processed file passed (including skipped files with no target section or empty file).
+ **`1`** — at least one key violation, or a YAML/parse/shape error for a file (see **`yaml-handling.md`** § Errors).
+ **`2`** — invalid CLI usage. For hooks that validate **list entries** with a per-row **`name`** (e.g. each dict under `models:`), do not list **`name`** in **`--required`**. This applies to **`model-allowed-keys`**, **`macro-allowed-keys`**, **`seed-allowed-keys`**, **`source-allowed-keys`**, **`snapshot-allowed-keys`**, **`exposure-allowed-keys`**, **`catalog-allowed-keys`**, and similar. **`dbt-project-allowed-keys`** (see **§8**) does **not** use that rule—teams may set **`--required name`** to enforce a project `name:`. For flags that are invalid or contradictory, the hook’s section defines exit **`2`**, if any.

## Pattern: `*-allowed-keys` (shared design)

Most hooks validate **top-level keys on each entry** in a dbt property YAML document: one **target node type** per hook (e.g. each dict under `models:`, each source under `sources:`, each row under `sources: … tables:`, …). **`dbt-project-allowed-keys`** instead validates **one** top-level mapping per file (**`dbt_project.yml`**) as a single “project” resource (see **§8**). Document-level rules, multi-resource files, and parsing are in **`yaml-handling.md`** (especially **§ dbt project file**, **§ dbt shape**, and **§ Parsing**).

**CLI contract** (same for every hook in this family):

+ `--required` — comma-separated keys that must be present on each **validated resource entry** (top-level of the model/seed/… dict). Default: none. Do not require keys that dbt always supplies for real resources if that would be redundant (e.g. **`name`** on models); each hook’s section calls out exceptions. **`--required`** does **not** apply to keys **under** **`config:`**; **`--required` / `--forbidden` for `config` keys** stay on **`*-allowed-config-keys`** **until further notice** (no current plan to move them onto **`*-allowed-keys`**).
+ **Allowed keys are fixed** for that hook’s target: only the **user-authorable** top-level keys in **`resource-keys.md`** for the matching **§** (dbt **resource properties** for property YAML, or the **dbt project file** table for **`dbt_project.yml`**; not manifest-only fields; see that doc’s intro).
+ `--forbidden` — optional comma-separated keys that **must not** appear on the **top-level** resource entry, even when otherwise allowlisted. Does **not** apply to keys under **`config:`**; use **`*-allowed-config-keys`** **`--forbidden`** for that (**until further notice**, same as **`--required`** above).
+ **`--check-nested`** — **one** boolean option; default **`true`**. Accept explicit **`true`** or **`false`** (e.g. **`--check-nested false`** to restore historical top-level-only behavior). When **`true`**, hooks listed in **§ Nested keys (`config`) and `--check-nested`** also validate **direct children of `config:`** using the same default allowlists as **`*-allowed-config-keys`** (see **`resource-config-keys.md`** and **`hook-families/allowed-config-keys.md`**). When **`false`**, behavior matches the **historical** **`*-allowed-keys`** scope: **top-level keys on the resource entry only** (no `config` child-key checks). Do **not** split this into a separate inverted flag name (e.g. no standalone **`--no-check-nested`**); a single **`--check-nested`** with a boolean value keeps pre-commit **`args:`** and shell usage predictable.
+ **`--check-columns`** — **one** boolean option; default **`true`**. Accept explicit **`true`** or **`false`**. When **`true`**, hooks listed in **§ Nested keys (`columns:`) and `--check-columns`** also validate **direct keys on each entry in `columns:`** using the default allowlists from **`resource-keys.md`** § **Column keys** (implemented as **`*_COLUMN_ALLOWED_KEYS`** in **`resource_keys.py`**). When **`false`**, no column-level key checks are performed. Do **not** split this into a separate inverted flag name; a single **`--check-columns`** with a boolean value is consistent with **`--check-nested`**.

**Legacy keys:** If a top-level key on an entry appears in **`resource-keys.md`** § **Legacy / deprecated** for that hook’s resource type, implementations **SHOULD** emit a violation whose message is **actionable**: it **SHOULD** include the **Suggested violation detail** from that row (rename target, e.g. use **`data_tests`** instead of **`tests`**, or where to nest under **`config`**, e.g. **`config.meta`**). Keys that are neither allowlisted nor listed as legacy continue to use generic **disallowed key** wording (see **`yaml-handling.md`** § Errors).

**Hook identity:** each hook has its own **`id`** and **`entry`** (console script name). Name hooks so **`id`** and **`entry`** clearly identify the target (e.g. `model-allowed-keys`, `source-allowed-keys`, `catalog-allowed-keys`, `dbt-project-allowed-keys`, `seed-allowed-keys`, …). Nested or secondary lists (e.g. table rows under `sources: … → tables:`) get a distinct hook when we validate them, with a distinct **`resource-keys.md`** section and a distinct **`id`** / **`entry`** (e.g. `source-table-allowed-keys`).

**Implementation reuse:** all `*-allowed-keys` hooks **SHOULD** delegate to **one shared validation core** (load YAML per **`yaml-handling.md`**, **extract the mapping to check** (named list section vs. whole-document root; see **§8** for **`dbt_project.yml`**) and apply required / allowlist / forbidden rules, emit violations). Per-hook code **SHOULD** be limited to wiring (Typer/command entry, argument forwarding) plus **resource-specific** pieces: which top-level section and list path to walk (including nesting), and the **default allowlist** (frozen sets in **`src/dbt_yaml_guardrails/hook_families/allowed_keys/resource_keys.py`**, documented in **`resource-keys.md`**). Avoid copying the full check loop for each new resource type.

### Typer CLI entry modules (optional refactor)

Each console script may remain its own small module with duplicated **`main`** / **`cli_main`** / **`typer.run`** wiring. Introducing a **shared factory** (or helper) to register new `*-allowed-keys` hooks with less boilerplate is **optional**—do it only if the number of hooks makes the duplication hard to maintain. Not a spec requirement.

**Pre-commit:** each hook is a separate stanza in **`.pre-commit-hooks.yaml`**; they may share **`language: python`** and the same package install. **`files`** / **`types`** patterns may differ per hook if we need narrower file matching. **`dbt-project-allowed-keys`** **SHOULD** use a **`files:`** filter such as **`^dbt_project\.yml$`** (or equivalent) so only the project file is checked—see **§8**.

### Nested keys (`config`) and `--check-nested` (v1)

**Goal:** The default **`*-allowed-keys`** run should also catch **unknown keys under `config:`** on each resource, using the **same** Fusion- and dbt **1.10+**-oriented default allowlists as **`*-allowed-config-keys`** (**`*_CONFIG_ALLOWED_KEYS`**, **`resource-config-keys.md`**), without adding a second family of per-hook flags for “what is allowed under `config`” in v1. Invalid **`config:`** keys are **flagged**; **`--required` / `--forbidden` for `config` keys** are **not** added to **`*-allowed-keys`** (**until further notice** they stay on **`*-allowed-config-keys`** only—see **`hook-families/allowed-config-keys.md`**).

**In scope (v1):** **Direct keys** of the **`config:`** mapping only (same rule as **`*-allowed-config-keys`** v1: one segment per key; no dot paths into deeper nesting). Applies to the shipped property-YAML hooks **§§1–6** ( **`model`**, **`macro`**, **`seed`**, **`snapshot`**, **`exposure`**, **`source`** ) when the entry has a **`config`** key that is a mapping. If **`config`** is missing, there is nothing nested to check; if **`config`** is **`null`** or not a mapping, that is a **shape error** (exit **`1`**) as in **`*-allowed-config-keys`**. **Out of v1 scope for nested checking:** **§7 `catalog-allowed-keys`** (no **`config:`** on the catalog entry in the current spec), **§8 `dbt-project-allowed-keys`**, and **any** deeper nestings beyond **`config:`** (e.g. **`columns`**, project-file hierarchical **`models:`** blocks). **Planned next** for nested allowlist work after **`config:`** is **`columns`** (per-column keys on resource entries); other paths follow after that.

**`meta` under `config`:** The key **`meta`** is **in scope** only as a **sibling** under **`config:`** (it must appear in the **`_CONFIG_ALLOWED_KEYS`** set if the user sets **`meta`**, as today). **`*-allowed-keys`** with **`--check-nested` true** does **not** validate **keys inside `config.meta`** (no recursion into the **`meta`** mapping). **`config.meta`** key names and values stay with **`*-allowed-meta-keys`**, **`*-meta-accepted-values`**, and related families. Allowlists for **`config:`** child keys are the **default sets in `resource-config-keys.md`** (dbt **1.10+** / **Fusion**-aligned, including **`meta` as a permitted key** where documented).

**Relationship to `*-allowed-config-keys`:** The standalone family remains **shipped** and **documented**; it **may** be **deprecated** in favor of **`*-allowed-keys` + `--check-nested` default true** in a **future** release, but that is not required for v1. **Each hook runs independently** as configured in pre-commit: if both **`*-allowed-keys`** (with **`--check-nested` true**) and **`*-allowed-config-keys`** validate the same file and entry, the same bad **`config:`** key **may** produce **two** stderr lines (one per hook). Implementations **MUST NOT** deduplicate or suppress violations across hooks.

**stderr for nested `config` keys:** Violations from this nested pass **SHOULD** use a **prefixed** tail after the resource label—include the literal segment **`config:`** before the detail—so they read differently from top-level key violations on the same hook (see **`yaml-handling.md`** § **Errors**).

**Implementation reuse:** **SHOULD** call the same validation logic and legacy maps as **`*-allowed-config-keys`** for the **`config:`** key pass, so the two code paths do not diverge on allowlist contents.

### Nested keys (`columns:`) and `--check-columns`

**Goal:** The default **`*-allowed-keys`** run should also catch **unknown keys on each column entry** (each item in `columns:`), using dbt/Fusion-oriented default allowlists from **`resource-keys.md`** § **Column keys** for that resource type, without adding a separate hook family for column key validation.

**In scope:** Direct keys of each item in the **`columns:`** list for the three property-YAML hooks that have `columns:` at the resource entry level: **`model-allowed-keys`** (§1), **`seed-allowed-keys`** (§3), and **`snapshot-allowed-keys`** (§4). If **`columns:`** is absent or an empty list, skip silently (nothing to check). Shape errors that exit **`1`**:

- `columns:` present but **`null`** or not a list — message: `{resource_kind} '{resource_name}': columns must be a list`
- a column entry that is **`null`** or not a mapping — message: `{resource_kind} '{resource_name}': column at index {i} must be a mapping`
- a column entry missing **`name`** — message: `{resource_kind} '{resource_name}': column at index {i} is missing 'name'`

Indices are **0-based** and refer to the position in the `columns:` list.

**Out of scope:** **`macro-allowed-keys`** and **`exposure-allowed-keys`** (those entry shapes have no `columns:` list); **`source-allowed-keys`** (source columns are nested under `tables: → [table] → columns:` — a deeper path addressed when `source-table-allowed-keys` is specced; see §9); **`catalog-allowed-keys`** and **`dbt-project-allowed-keys`**. Deeper nesting inside a column entry — including keys **inside** a column-level `config:` block and keys inside column-level `meta` or per-constraint mappings — is out of scope and stays with dedicated families. The column-level `config:` key itself **is** allowlisted (dbt supports `config: { tags: …, meta: … }` directly on column entries); only its child keys are not validated here.

**`name` on column entries:** Always required on each column dict; do **not** list it in **`--required`** (consistent with resource-level `name` rules). A column entry missing `name` is a **shape error** (exit **`1`**), not a key violation.

**`--required` / `--forbidden` on column keys:** not in scope for this version. Only the default allowlist is checked; per-column `--required`/`--forbidden` (e.g. enforce `description` on every column) are a **future extension**.

**Legacy column keys:** If a key on a column entry appears in **`resource-keys.md`** § **Column keys — Legacy / deprecated** for that resource, implementations **SHOULD** emit an actionable message (the **Suggested violation detail** from that row), consistent with top-level and `config:` legacy key handling. The primary legacy key across all three resources is **`tests`** → rename to `data_tests`.

**stderr for column key violations:** Use **`column '<name>': <detail>`** as the infix after the resource label — e.g. `path/to/schema.yml: model 'my_model': column 'id': disallowed key 'bad_key'` — so column violations are visually distinct from both top-level key violations and `config:` violations on the same hook run.

**Stability / versioning:** The column key allowlists target **dbt Fusion and the latest dbt Core versions** (currently 1.10+). The allowed sets are expected to grow as dbt formalises new column-level properties. When dbt deprecates or renames a column key, add a row to the **Legacy / deprecated** table in **`resource-keys.md`** § **Column keys** for that resource and a matching entry in the relevant **`*_COLUMN_LEGACY_KEY_MESSAGES`** map, rather than removing the key from the allowlist immediately. Consumers should pin a `rev:` and review changelog entries when upgrading, as allowlist additions are non-breaking but legacy-key additions change violation messages.

**Implementation:** SHOULD add a column-validation helper in **`allowed_keys_core.py`** (parallel to `_nested_config_violations`) and extend **`collect_violation_rows_for_property_paths`** with `check_columns`, `column_allowed`, `column_legacy_key_messages`, and `resource_label` params, following the same pattern as the `check_nested` extension. Column allowlists live in **`resource_keys.py`** as **`MODEL_COLUMN_ALLOWED_KEYS`**, **`SEED_COLUMN_ALLOWED_KEYS`**, **`SNAPSHOT_COLUMN_ALLOWED_KEYS`** (and matching `*_COLUMN_LEGACY_KEY_MESSAGES`), documented in **`resource-keys.md`** § **Column keys** for each resource.

## 1. `model-allowed-keys`

Validates the **top-level keys on each model entry** (each dict under the `models:` list).

The CLI entry point and hook **`id`** should be **`model-allowed-keys`**.

**Pre-commit (shipped):** **`language: python`**, **`entry: model-allowed-keys`**, **`types: [yaml]`** — see **`.pre-commit-hooks.yaml`** at the repo root (must match **`[project.scripts]`** in **`pyproject.toml`**).

**Arguments:** see **§ Pattern: `*-allowed-keys`**, **§ Nested keys (`config`) and `--check-nested`**, and **§ Nested keys (`columns:`) and `--check-columns`**. For **`--required`**: **`name`** is always present for real models in dbt; do not list it in **`--required`**. **Allowed keys:** **`resource-keys.md`** § **Models**, implemented as **`MODEL_ALLOWED_KEYS`**. **`--forbidden`:** e.g. disallow **`config`** on the top-level model entry where policy requires config-only in `dbt_project.yml`. **Nested `config` keys (when `--check-nested` is on):** **`resource-config-keys.md`** § **Models — default keys under `config`**, as **`MODEL_CONFIG_ALLOWED_KEYS`**, matching **`model-allowed-config-keys`**. **Column keys (when `--check-columns` is on):** **`resource-keys.md`** § **Models — Column keys**, as **`MODEL_COLUMN_ALLOWED_KEYS`** / **`MODEL_COLUMN_LEGACY_KEY_MESSAGES`**.

## 2. `macro-allowed-keys`

Validates the **top-level keys on each macro entry** (each dict under the `macros:` list).

The CLI entry point and hook **`id`** should be **`macro-allowed-keys`**.

**Pre-commit (shipped):** **`language: python`**, **`entry: macro-allowed-keys`**, **`types: [yaml]`** — see **`.pre-commit-hooks.yaml`** (must match **`[project.scripts]`** in **`pyproject.toml`**).

**Arguments:** see **§ Pattern: `*-allowed-keys`** and **§ Nested keys (`config`) and `--check-nested`**. For **`--required`**: **`name`** is always present for real macros in dbt; do not list it in **`--required`**. **Allowed keys:** **`resource-keys.md`** § **Macros**, implemented as **`MACRO_ALLOWED_KEYS`**. **Nested `config` keys (when `--check-nested` is on):** **`resource-config-keys.md`** § **Macros — default keys under `config`** / **`MACRO_CONFIG_ALLOWED_KEYS`**, matching **`macro-allowed-config-keys`**. **`--check-columns`:** **no effect** (macro entries have no `columns:` list).

## 3. `seed-allowed-keys`

Validates the **top-level keys on each seed entry** (each dict under the `seeds:` list).

The CLI entry point and hook **`id`** should be **`seed-allowed-keys`**.

**Pre-commit (shipped):** **`language: python`**, **`entry: seed-allowed-keys`**, **`types: [yaml]`** — see **`.pre-commit-hooks.yaml`** (must match **`[project.scripts]`** in **`pyproject.toml`**).

**Arguments:** see **§ Pattern: `*-allowed-keys`**, **§ Nested keys (`config`) and `--check-nested`**, and **§ Nested keys (`columns:`) and `--check-columns`**. For **`--required`**: **`name`** is always present for real seeds in dbt; do not list it in **`--required`**. **Allowed keys:** **`resource-keys.md`** § **Seeds**, implemented as **`SEED_ALLOWED_KEYS`**. **Nested `config` keys (when `--check-nested` is on):** **`resource-config-keys.md`** § **Seeds — default keys under `config`** / **`SEED_CONFIG_ALLOWED_KEYS`**, matching **`seed-allowed-config-keys`**. **Column keys (when `--check-columns` is on):** **`resource-keys.md`** § **Seeds — Column keys**, as **`SEED_COLUMN_ALLOWED_KEYS`** / **`SEED_COLUMN_LEGACY_KEY_MESSAGES`**.

## 4. `snapshot-allowed-keys`

Validates the **top-level keys on each snapshot entry** (each dict under the `snapshots:` list).

The CLI entry point and hook **`id`** should be **`snapshot-allowed-keys`**.

**Pre-commit (shipped):** **`language: python`**, **`entry: snapshot-allowed-keys`**, **`types: [yaml]`** — see **`.pre-commit-hooks.yaml`** (must match **`[project.scripts]`** in **`pyproject.toml`**).

**Arguments:** see **§ Pattern: `*-allowed-keys`**, **§ Nested keys (`config`) and `--check-nested`**, and **§ Nested keys (`columns:`) and `--check-columns`**. For **`--required`**: **`name`** is always present for real snapshots in dbt; do not list it in **`--required`**. **Allowed keys:** **`resource-keys.md`** § **Snapshots**, implemented as **`SNAPSHOT_ALLOWED_KEYS`**. **Nested `config` keys (when `--check-nested` is on):** **`resource-config-keys.md`** § **Snapshots — default keys under `config`** / **`SNAPSHOT_CONFIG_ALLOWED_KEYS`**, matching **`snapshot-allowed-config-keys`**. **Column keys (when `--check-columns` is on):** **`resource-keys.md`** § **Snapshots — Column keys**, as **`SNAPSHOT_COLUMN_ALLOWED_KEYS`** / **`SNAPSHOT_COLUMN_LEGACY_KEY_MESSAGES`**.

## 5. `exposure-allowed-keys`

Validates the **top-level keys on each exposure entry** (each dict under the `exposures:` list).

The CLI entry point and hook **`id`** should be **`exposure-allowed-keys`**.

**Pre-commit (shipped):** **`language: python`**, **`entry: exposure-allowed-keys`**, **`types: [yaml]`** — see **`.pre-commit-hooks.yaml`** (must match **`[project.scripts]`** in **`pyproject.toml`**).

**Arguments:** see **§ Pattern: `*-allowed-keys`** and **§ Nested keys (`config`) and `--check-nested`**. For **`--required`**: **`name`** is always present for real exposures in dbt; do not list it in **`--required`**. **Allowed keys:** **`resource-keys.md`** § **Exposures**, implemented as **`EXPOSURE_ALLOWED_KEYS`**. **Nested `config` keys (when `--check-nested` is on):** **`resource-config-keys.md`** § **Exposures — default keys under `config`** / **`EXPOSURE_CONFIG_ALLOWED_KEYS`**, matching **`exposure-allowed-config-keys`**. **`--check-columns`:** **no effect** (exposure entries have no `columns:` list).

## 6. `source-allowed-keys`

Validates the **top-level keys on each source entry** (each dict under the `sources:` list).

The CLI entry point and hook **`id`** should be **`source-allowed-keys`**.

**Pre-commit (shipped):** **`language: python`**, **`entry: source-allowed-keys`**, **`types: [yaml]`** — see **`.pre-commit-hooks.yaml`** (must match **`[project.scripts]`** in **`pyproject.toml`**).

**Arguments:** see **§ Pattern: `*-allowed-keys`** and **§ Nested keys (`config`) and `--check-nested`**. For **`--required`**: **`name`** is always present for real sources in dbt; do not list it in **`--required`**. **Allowed keys:** **`resource-keys.md`** § **Sources**, implemented as **`SOURCE_ALLOWED_KEYS`**. **Nested `config` keys (when `--check-nested` is on):** **`resource-config-keys.md`** § **Sources — default keys under `config`** / **`SOURCE_CONFIG_ALLOWED_KEYS`**, matching **`source-allowed-config-keys`**. **`--check-columns`:** **no effect** in v1; source entry columns are nested under `tables: → [table] → columns:` — a deeper path addressed when `source-table-allowed-keys` is specced (see §9).

## 7. `catalog-allowed-keys`

Validates the **top-level keys on each catalog entry** (each dict under the `catalogs:` list). dbt Core **1.10+** parses [catalogs property YAML](https://docs.getdbt.com/docs/dbt-versions/core-upgrade/upgrading-to-v1.10) (often a root-level **`catalogs.yml`** file).

The CLI entry point and hook **`id`** should be **`catalog-allowed-keys`**.

**Pre-commit (shipped):** **`language: python`**, **`entry: catalog-allowed-keys`**, **`types: [yaml]`** — see **`.pre-commit-hooks.yaml`** (must match **`[project.scripts]`** in **`pyproject.toml`**).

**Arguments:** see **§ Pattern: `*-allowed-keys`**. For **`--required`**: **`name`** is always present for each catalog in dbt; do not list it in **`--required`**. **Allowed keys:** **`resource-keys.md`** § **Catalogs**, implemented as **`CATALOG_ALLOWED_KEYS`**. Nested keys under each **`write_integrations`** item are not validated by this hook. **`--check-nested`:** **no effect** in v1 (there is no **`config:`** on catalog entries under the current **`CATALOG_ALLOWED_KEYS`** spec; see **§ Nested keys (`config`) and `--check-nested`**). **`--check-columns`:** **no effect** (catalog entries have no `columns:` list).

## 8. `dbt-project-allowed-keys`

Validates the **top-level keys** on the **root mapping** of a **`dbt_project.yml` file**—a single “resource” (the dbt project), not a list of named resources.

**Rationale:** dbt Core **1.10+** tightens the authoring surface with [JSON Schema validation of `dbt_project.yml`](https://github.com/dbt-labs/dbt-core) and related deprecations. This hook **does not** re-implement dbt’s schema; it enforces a **documented, team-visible allowlist** of top-level **keys** aligned with the public [`dbt_project.yml` reference](https://docs.getdbt.com/reference/dbt_project.yml), so pre-commit can fail fast on typos, deprecated custom keys, or policy-forbidden top-level options **without** running dbt.

**Distinction from other `*-allowed-keys` hooks:** property YAML (under model paths) uses optional top-level `version: 2` and resource sections. **`dbt_project.yml`** uses **`config-version`**, **`name`**, **`profile`**, path keys, and resource **config** blocks (`models:`, `seeds:`, …). The **`version`** key at the top of **`dbt_project.yml`** is the [project `version` config](https://docs.getdbt.com/reference/project-configs/version) (e.g. semver for packages), **not** the “resource YAML v2” document marker. YAML is loaded with **`load_dbt_project_yaml`** (see **`yaml-handling.md` § dbt project file**), which does **not** apply the property-YAML `version: 2` document rule.

The CLI entry point and hook **`id`** should be **`dbt-project-allowed-keys`**.

**Pre-commit (shipped):** **`language: python`**, **`entry: dbt-project-allowed-keys`**, **`files: ^dbt_project\.yml$`**, and **`types: [yaml]`** — see **`.pre-commit-hooks.yaml`** (must match **`[project.scripts]`** in **`pyproject.toml`**). Relying on **`types: [yaml]`** without **`files:`** is not recommended for monorepos that run hooks on all `*.yml`.

**Arguments:** see **§ Pattern: `*-allowed-keys`**. **`--required`**: it is valid to require **`name`**, **`config-version`**, **`profile`**, or other top-level keys your policy demands (no exit code **`2`** for including **`name`** in **`--required`**). **Allowed keys:** **`resource-keys.md`** § **dbt project file (`dbt_project.yml`)**, implemented as **`DBT_PROJECT_ALLOWED_KEYS`**. **Legacy or deprecated** top-level project keys dbt still accepts (if any) **SHOULD** be listed in **`resource-keys.md`** for this section and mapped in **`DBT_PROJECT_LEGACY_KEY_MESSAGES`**, the same as other allowlist hooks. **`--forbidden`:** e.g. forbid **`vars`** in the project file if variables must live only in **`profiles.yml`**. **`--check-nested`:** **not applicable** in v1 (this hook validates only the **top level** of **`dbt_project.yml`**; hierarchical **`models:`** / **`seeds:`** / … blocks are a **future** extension—see **§ Nested keys (`config`) and `--check-nested`**). **`--check-columns`:** **not applicable** (`dbt_project.yml` has no `columns:` list at the root level).

**Violation format:** stderr uses **`path: project: <detail>`** (see **`format_violation_line`** in **`allowed_keys_core.py`** when the resource label is **`project`** and there is no per-row name).

**Nested keys:** this hook only validates **the top level** of **`dbt_project.yml`**. It does not traverse **`models: → …` nested folder configs**; path-level and resource-type config under those keys is out of scope for this hook (use **`model-allowed-config-keys`** and related families where applicable **when** those hooks support project-file paths in a future spec, or use separate policy).

## 9. Other resource types (later version)

Hooks for **source tables**, **analyses**, **unit tests**, and any other targets described in **`resource-keys.md`** but not listed in **§§ 1–8** above are **planned for a later version**. They **`SHOULD`** follow **§ Pattern: `*-allowed-keys`** when implemented, with **`resource-keys.md`** as the allowlist source for each target:

| Target (conceptual) | `resource-keys.md` section | Notes |
| --- | --- | --- |
| Each source table | § **Source tables** (when specified) | Nested list under `sources: … → tables:`; distinct hook from source-level keys |
| Each analysis | § **Analyses** | Under `analyses:` |
| Each unit test | § **Unit tests** | Under `unit_tests:` |
| **`columns:`** entries (per-column keys) on **models, seeds, snapshots** | § **Models — Column keys** / § **Seeds — Column keys** / § **Snapshots — Column keys** | Specced — see **§ Nested keys (`columns:`) and `--check-columns`**; implementation pending. Source entry columns are deeper (`tables: → columns:`) and remain out of scope until `source-table-allowed-keys` is added. |

Concrete **`id`**, **`entry`**, and **`[project.scripts]`** names **`SHOULD`** stay predictable (e.g. `source-table-allowed-keys`, …).
