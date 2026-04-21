# Hooks

All hooks should follow the conventions for hooks defined for [pre-commit](https://pre-commit.com/#creating-new-hooks).

## Packaging (required for consumers)

When this repository is used as a pre-commit **`repo:`** (local path, git URL, etc.), pre-commit **requires** a **`.pre-commit-hooks.yaml`** file at the **repository root** listing each hook’s `id`, `entry`, `language`, and selection (`types` / `files` / `types_or`, …). Without that file, pre-commit fails with *`.pre-commit-hooks.yaml` is not a file*. See [Creating new hooks](https://pre-commit.com/#creating-new-hooks).

Keep **`.pre-commit-hooks.yaml`** in sync with each shipped hook: every **`entry`** must match a console script from **`pyproject.toml`** (`[project.scripts]`), and file selection should align with **`yaml-handling.md`** § Files and the hook’s family spec.

## Shared foundations

Shared behavior (parser, document shape, when to skip a file, stderr/exit semantics, message ordering) is defined in **`yaml-handling.md`**. Default **top-level allowed-key sets** per resource type for the **`*-allowed-keys`** family are in **`resource-keys.md`**. Default **keys under `config`** for the **`*-allowed-config-keys`** family are in **`resource-config-keys.md`** (all five resource hooks shipped)—see **`hook-families/allowed-config-keys.md`**.

**Per-hook** CLI names, arguments, numeric **exit codes**, defaults, and pre-commit `id`/`entry` details live in **hook family** specs under **`hook-families/`** (see below), not only in this file.

## Hook families

Each family groups hooks that share the same validation target and CLI shape. Add a new file under **`hook-families/`** when introducing a new family.

| Family | Spec | What it validates (summary) |
| --- | --- | --- |
| Top-level keys on each resource entry | **`hook-families/allowed-keys.md`** | Keys on each dict under `models:`, `macros:`, `seeds:`, … |
| Top-level keys under each entry’s `config` mapping | **`hook-families/allowed-config-keys.md`** | **`*-allowed-config-keys`**: **`model`**, **`macro`**, **`seed`**, **`snapshot`**, **`exposure`** shipped. Same CLI as **`*-allowed-keys`** (`--required` / `--forbidden`); default allowlists in **`resource-config-keys.md`** (Fusion-oriented cross-adapter keys **plus** documented adapter-specific **union** per resource) |
| Keys under `config.meta` | **`hook-families/allowed-meta-keys.md`** | **`*-allowed-meta-keys`** (**`model`**, **`seed`**, **`snapshot`**, **`exposure`**, **`macro`** shipped); **`config`** implied; optional **`--allowed`**, plus **`--required`** / **`--forbidden`**; no default allowlist in-repo (see that spec) |
| String or string list at a path under `config.meta` | **`hook-families/meta-accepted-values.md`** | **`*-meta-accepted-values`**: **`model`**, **`seed`**, **`snapshot`**, **`exposure`** shipped; **`macro`** planned; **`--key`** dot path, **`--values`** allowlist, optional **`--optional`**; non-string scalars **future** |
| **`config.tags`** value shape (string or list of strings) | **`hook-families/tags-accepted-values.md`** | **`*-tags-accepted-values`**: **spec only** (not shipped yet); **`--values`** allowlist only; **no** mandatory-tag mode; no path flag—always **`config.tags`** |

The repository root **`HOOKS.md`** **SHOULD** list shipped hooks **by family** in separate tables or sections (not one flat list that mixes families), and include the canonical **`repos:`** / **`rev:`** / **`hooks:`** copy-paste block; **`rev:`** tracks **`v`** + **`pyproject.toml`** **`project.version`**. See **`project-spec.md`** § **README.md and HOOKS.md (repository root)**.

Implementations **SHOULD** keep the **`*-allowed-keys`** family aligned with **`resource-keys.md`** when top-level allowlists change, and the **`*-allowed-config-keys`** family aligned with **`resource-config-keys.md`** as hooks ship (see **`hook-families/allowed-config-keys.md`**). The **`*-allowed-meta-keys`** family uses **user-supplied** allowlists only (keys under **`config.meta`**; **`config`** implied in the hook name); there is no fixed allowlist table in **`resource-keys.md`** or **`resource-config-keys.md`** for **`meta`** key names unless we add optional convention docs later.

## Code layout (implementation)

Python **source** and **tests** **SHOULD** be organized by **hook family** in parallel with **`hook-families/*.md`** (subpackage per family, tests mirrored under **`tests/`**). Cross-family shared code stays at the package root or a small shared module. Details and naming guidance: **`project-spec.md`** § **Source and test layout (mirror hook families)**; test layout notes in **`testing-strategy.md`** § **Layout**.
