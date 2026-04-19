# Hooks

All hooks should follow the conventions for hooks defined for [pre-commit](https://pre-commit.com/#creating-new-hooks).

## Packaging (required for consumers)

When this repository is used as a pre-commit **`repo:`** (local path, git URL, etc.), pre-commit **requires** a **`.pre-commit-hooks.yaml`** file at the **repository root** listing each hook’s `id`, `entry`, `language`, and selection (`types` / `files` / `types_or`, …). Without that file, pre-commit fails with *`.pre-commit-hooks.yaml` is not a file*. See [Creating new hooks](https://pre-commit.com/#creating-new-hooks).

Keep **`.pre-commit-hooks.yaml`** in sync with the sections below: every shipped hook gets an entry there, with **`entry`** matching a console script from **`pyproject.toml`** (`[project.scripts]`), and file selection aligned with **`yaml-handling.md`** § Files and each hook’s notes.

Shared behavior (parser, document shape, when to skip a file, stderr/exit codes, message ordering) is defined in **`yaml-handling.md`**. Default **allowed-key sets** per resource type are in **`resource-keys.md`**. This file defines **per-hook** CLIs, arguments, and how those defaults apply.

**Exit codes** for `*-allowed-keys` CLIs **SHOULD** be:

+ **`0`** — every processed file passed (including skipped files with no target section or empty file).
+ **`1`** — at least one key violation, or a YAML/parse/shape error for a file (see **`yaml-handling.md`** § Errors).
+ **`2`** — invalid CLI usage (e.g. redundant **`name`** in **`--required`** for any **`*-allowed-keys`** hook that validates named resources: **`model-allowed-keys`**, **`macro-allowed-keys`**, **`seed-allowed-keys`**, **`snapshot-allowed-keys`**, **`exposure-allowed-keys`**, …).

## Pattern: `*-allowed-keys` (shared design)

Several hooks validate **top-level keys on each entry** in a dbt property YAML document: one **target node type** per hook (e.g. each dict under `models:`, each source under `sources:`, each row under `sources: … tables:`, …). Document-level rules, multi-resource files, and parsing are in **`yaml-handling.md`** (especially **§ dbt shape** and **§ Parsing**).

**CLI contract** (same for every hook in this family):

+ `--required` — comma-separated keys that must be present on each validated entry. Default: none. Do not require keys that dbt always supplies for real resources if that would be redundant (e.g. **`name`** on models); each hook’s section calls out exceptions.
+ **Allowed keys are fixed** for that hook’s target node: only the Fusion-oriented set in **`resource-keys.md`** for the matching **§**.
+ `--forbidden` — optional comma-separated keys that **must not** appear on an entry, even when otherwise allowlisted (stricter team policy).

**Legacy keys:** If a top-level key on an entry appears in **`resource-keys.md`** § **Legacy / deprecated** for that hook’s resource type, implementations **SHOULD** emit a violation whose message is **actionable**: it **SHOULD** include the **Suggested violation detail** from that row (rename target, e.g. use **`data_tests`** instead of **`tests`**, or where to nest under **`config`**, e.g. **`config.meta`**). Keys that are neither allowlisted nor listed as legacy continue to use generic **disallowed key** wording (see **`yaml-handling.md`** § Errors).

**Hook identity:** each hook has its own **`id`** and **`entry`** (console script name). Name hooks so **`id`** and **`entry`** clearly identify the target (e.g. `model-allowed-keys`, and later `source-allowed-keys`, `seed-allowed-keys`, …). Nested or secondary lists (e.g. tables under a source) get a distinct hook when we validate them, with a distinct **`resource-keys.md`** section and a distinct **`id`** / **`entry`** (e.g. `source-table-allowed-keys`).

**Implementation reuse:** all `*-allowed-keys` hooks **SHOULD** delegate to **one shared validation core** (load YAML per **`yaml-handling.md`**, extract entries for the hook’s target section, apply required / allowlist / forbidden rules, emit violations). Per-hook code **SHOULD** be limited to wiring (Typer/command entry, argument forwarding) plus **resource-specific** pieces: which top-level section and list path to walk (including nesting), and the **default allowlist** (frozen sets in **`src/dbt_yaml_guardrails/resource_keys.py`**, documented in **`resource-keys.md`**). Avoid copying the full check loop for each new resource type.

**Pre-commit:** each hook is a separate stanza in **`.pre-commit-hooks.yaml`**; they may share **`language: python`** and the same package install. **`files`** / **`types`** patterns may differ per hook if we need narrower file matching later; until then, align with **`yaml-handling.md`**.

## 1. `model-allowed-keys`

Validates the **top-level keys on each model entry** (each dict under the `models:` list).

The CLI entry point and hook **`id`** should be **`model-allowed-keys`**.

**Pre-commit (shipped):** **`language: python`**, **`entry: model-allowed-keys`**, **`types: [yaml]`** — see **`.pre-commit-hooks.yaml`** at the repo root (must match **`[project.scripts]`** in **`pyproject.toml`**).

**Arguments:** see **§ Pattern: `*-allowed-keys`**. For **`--required`**: **`name`** is always present for real models in dbt; do not list it in **`--required`**. **Allowed keys:** **`resource-keys.md`** § **Models**, implemented as **`MODEL_ALLOWED_KEYS`** in **`src/dbt_yaml_guardrails/resource_keys.py`**. **`--forbidden`:** e.g. disallow **`config`** where policy requires config-only in `dbt_project.yml`.

## 2. `macro-allowed-keys`

Validates the **top-level keys on each macro entry** (each dict under the `macros:` list).

The CLI entry point and hook **`id`** should be **`macro-allowed-keys`**.

**Pre-commit (shipped):** **`language: python`**, **`entry: macro-allowed-keys`**, **`types: [yaml]`** — see **`.pre-commit-hooks.yaml`** (must match **`[project.scripts]`** in **`pyproject.toml`**).

**Arguments:** see **§ Pattern: `*-allowed-keys`**. For **`--required`**: **`name`** is always present for real macros in dbt; do not list it in **`--required`**. **Allowed keys:** **`resource-keys.md`** § **Macros**, implemented as **`MACRO_ALLOWED_KEYS`** in **`src/dbt_yaml_guardrails/resource_keys.py`**.

## 3. `seed-allowed-keys`

Validates the **top-level keys on each seed entry** (each dict under the `seeds:` list).

The CLI entry point and hook **`id`** should be **`seed-allowed-keys`**.

**Pre-commit (shipped):** **`language: python`**, **`entry: seed-allowed-keys`**, **`types: [yaml]`** — see **`.pre-commit-hooks.yaml`** (must match **`[project.scripts]`** in **`pyproject.toml`**).

**Arguments:** see **§ Pattern: `*-allowed-keys`**. For **`--required`**: **`name`** is always present for real seeds in dbt; do not list it in **`--required`**. **Allowed keys:** **`resource-keys.md`** § **Seeds**, implemented as **`SEED_ALLOWED_KEYS`** in **`src/dbt_yaml_guardrails/resource_keys.py`**.

## 4. `snapshot-allowed-keys`

Validates the **top-level keys on each snapshot entry** (each dict under the `snapshots:` list).

The CLI entry point and hook **`id`** should be **`snapshot-allowed-keys`**.

**Pre-commit (shipped):** **`language: python`**, **`entry: snapshot-allowed-keys`**, **`types: [yaml]`** — see **`.pre-commit-hooks.yaml`** (must match **`[project.scripts]`** in **`pyproject.toml`**).

**Arguments:** see **§ Pattern: `*-allowed-keys`**. For **`--required`**: **`name`** is always present for real snapshots in dbt; do not list it in **`--required`**. **Allowed keys:** **`resource-keys.md`** § **Snapshots**, implemented as **`SNAPSHOT_ALLOWED_KEYS`** in **`src/dbt_yaml_guardrails/resource_keys.py`**.

## 5. `exposure-allowed-keys`

Validates the **top-level keys on each exposure entry** (each dict under the `exposures:` list).

The CLI entry point and hook **`id`** should be **`exposure-allowed-keys`**.

**Pre-commit (shipped):** **`language: python`**, **`entry: exposure-allowed-keys`**, **`types: [yaml]`** — see **`.pre-commit-hooks.yaml`** (must match **`[project.scripts]`** in **`pyproject.toml`**).

**Arguments:** see **§ Pattern: `*-allowed-keys`**. For **`--required`**: **`name`** is always present for real exposures in dbt; do not list it in **`--required`**. **Allowed keys:** **`resource-keys.md`** § **Exposures**, implemented as **`EXPOSURE_ALLOWED_KEYS`** in **`src/dbt_yaml_guardrails/resource_keys.py`**.

## 6. Other resource types (later version)

Hooks for **sources**, **source tables**, **analyses**, **unit tests**, and any other targets described in **`resource-keys.md`** but not listed in **§§ 1–5** above are **planned for a later version**. They **`SHOULD`** follow **§ Pattern: `*-allowed-keys`** when implemented, with **`resource-keys.md`** as the allowlist source for each target:

| Target (conceptual) | `resource-keys.md` section | Notes |
| --- | --- | --- |
| Each source | § **Sources** | Top-level list under `sources:` |
| Each source table | § **Source tables** | Nested list under `sources: … tables:`; distinct hook from source-level keys |
| Each analysis | § **Analyses** | Under `analyses:` |
| Each unit test | § **Unit tests** | Under `unit_tests:` |

Concrete **`id`**, **`entry`**, and **`[project.scripts]`** names **`SHOULD`** stay predictable (e.g. `source-allowed-keys`, `source-table-allowed-keys`, …).
