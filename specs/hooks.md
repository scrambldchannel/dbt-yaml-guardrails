# Hooks

All hooks should follow the conventions for hooks defined for [pre-commit](https://pre-commit.com/#creating-new-hooks).

## Packaging (required for consumers)

When this repository is used as a pre-commit **`repo:`** (local path, git URL, etc.), pre-commit **requires** a **`.pre-commit-hooks.yaml`** file at the **repository root** listing each hook’s `id`, `entry`, `language`, and selection (`types` / `files` / `types_or`, …). Without that file, pre-commit fails with *`.pre-commit-hooks.yaml` is not a file*. See [Creating new hooks](https://pre-commit.com/#creating-new-hooks).

Keep **`.pre-commit-hooks.yaml`** in sync with each shipped hook: every **`entry`** must match a console script from **`pyproject.toml`** (`[project.scripts]`), and file selection should align with **`yaml-handling.md`** § Files and the hook’s family spec.

## Shared foundations

Shared behavior (parser, document shape, when to skip a file, stderr/exit semantics, message ordering) is defined in **`yaml-handling.md`**. Default **top-level allowed-key sets** per resource type for the **`*-allowed-keys`** family are in **`resource-keys.md`**. The **same** **`resource-config-keys.md`** allowlists govern **keys under `config:`** on property YAML when **`--check-config`** is **true** (the default) on **`*-allowed-keys`**, and govern the **`*-allowed-config-keys`** family ( **`model`**, **`macro`**, **`seed`**, **`source`**, **`snapshot`**, **`exposure`** )—see **`hook-families/allowed-keys.md`** and **`hook-families/allowed-config-keys.md`**. If both families run on the same file, each hook emits its own violations (**no** cross-hook deduplication).

**Per-hook** CLI names, arguments, numeric **exit codes**, defaults, and pre-commit `id`/`entry` details live in **hook family** specs under **`hook-families/`** (see below), not only in this file.

## Hook families

Each family groups hooks that share the same validation target and CLI shape. Add a new file under **`hook-families/`** when introducing a new family.

| Family | Spec | What it validates (summary) |
| --- | --- | --- |
| Top-level keys (property entries or `dbt_project.yml` root) | **`hook-families/allowed-keys.md`** | Keys on each resource entry and, by default (**`--check-config`**, see that spec), **direct keys under `config:`** for §§1–6 hooks; top-level keys in **`dbt_project.yml`** (**`dbt-project-allowed-keys`**, §8; nested project blocks **v1 out of scope**) |
| Top-level keys under each entry’s `config` mapping | **`hook-families/allowed-config-keys.md`** | **`*-allowed-config-keys`**: **`model`**, **`macro`**, **`seed`**, **`source`**, **`snapshot`**, **`exposure`** shipped. Same CLI as **`*-allowed-keys`** (`--required` / `--forbidden`); default allowlists in **`resource-config-keys.md`** (Fusion-oriented; adapter **union** where the spec documents it) |
| Direct keys on each column entry (`columns:` list) | **`hook-families/allowed-column-keys.md`** | **`*-allowed-column-keys`**: **`model`**, **`seed`**, **`snapshot`** shipped. Same CLI shape as **`*-allowed-config-keys`** (`--required` / `--forbidden`; `name` in `--required` exits `2`); default allowlists in **`resource-keys.md`** § **Column keys** (`*_COLUMN_ALLOWED_KEYS` in `resource_keys.py`). Overlap with **`*-allowed-keys --check-columns`** (default on): both may flag the same column key; implementations MUST NOT deduplicate. |
| Mechanical rewrites of deprecated property-YAML (legacy keys) | **`hook-families/fix-legacy-yaml.md`** | **Normative** rewrite rules (v1: **`tests` → `data_tests`**; future: top-level **`tags` / `meta`**, …). Delivered only via opt-in **`--fix-legacy-yaml`** (default **`false`**) on the six property **`*-allowed-keys`** CLIs and **`*-allowed-column-keys`** (see those specs; **not** on **`catalog-allowed-keys`** or **`dbt-project-allowed-keys`**). Complements validators; not a separate validation family or standalone hook. |
| Keys under `config.meta` | **`hook-families/allowed-meta-keys.md`** | **`*-allowed-meta-keys`** (**`model`**, **`seed`**, **`snapshot`**, **`exposure`**, **`source`**, **`macro`** shipped); **`config`** implied; optional **`--allowed`**, plus **`--required`** / **`--forbidden`**; no default allowlist in-repo (see that spec) |
| String or string list at a path under `config.meta` | **`hook-families/meta-accepted-values.md`** | **`*-meta-accepted-values`**: **`model`**, **`seed`**, **`snapshot`**, **`exposure`**, **`source`**, **`macro`** shipped; **`--key`** dot path, **`--values`** allowlist, optional **`--optional`**; non-string scalars **future** |
| **`config.tags`** value shape (string or list of strings) | **`hook-families/tags-accepted-values.md`** | **`*-tags-accepted-values`**: **`model`**, **`seed`**, **`snapshot`**, **`exposure`**, **`source`**, **`macro`** shipped; **`--values`** allowlist only; no path flag—always **`config.tags`** |

**General policy — no no-op hooks:** A hook is only shipped for a resource type where the validation target exists at the expected YAML path. For example, `*-allowed-column-keys` is only shipped for `model`, `seed`, and `snapshot` (which have `columns:` at the resource entry level); there is no `macro-allowed-column-keys` or `exposure-allowed-column-keys`. Where a flag on an existing hook accepts a value that has no effect on a particular resource (e.g. `--check-columns` on `*-allowed-keys` for `macro` or `exposure`), the flag is accepted for CLI consistency — but a dedicated hook for that resource is not added unless the validation target is real. New families **SHOULD** follow this pattern.

The repository root **`HOOKS.md`** **SHOULD** list shipped hooks **by family** in separate tables or sections (not one flat list that mixes families), and include the canonical **`repos:`** / **`rev:`** / **`hooks:`** copy-paste block; **`rev:`** tracks **`v`** + **`pyproject.toml`** **`project.version`**. See **`project-spec.md`** § **README.md and HOOKS.md (repository root)**.

Implementations **SHOULD** keep the **`*-allowed-keys`** family aligned with **`resource-keys.md`** when top-level allowlists change, and the **`*-allowed-config-keys`** family aligned with **`resource-config-keys.md`** as hooks ship (see **`hook-families/allowed-config-keys.md`**). The **`*-allowed-meta-keys`** family uses **user-supplied** allowlists only (keys under **`config.meta`**; **`config`** implied in the hook name); there is no fixed allowlist table in **`resource-keys.md`** or **`resource-config-keys.md`** for **`meta`** key names unless we add optional convention docs later.

## Code layout (implementation)

Python **source** and **tests** **SHOULD** be organized by **hook family** in parallel with **`hook-families/*.md`** (subpackage per family, tests mirrored under **`tests/`**). Cross-family shared code stays at the package root or a small shared module. Details and naming guidance: **`project-spec.md`** § **Source and test layout (mirror hook families)**; test layout notes in **`testing-strategy.md`** § **Layout**.
