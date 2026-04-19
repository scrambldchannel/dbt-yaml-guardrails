# Hooks

All hooks should follow the conventions for hooks defined for [pre-commit](https://pre-commit.com/#creating-new-hooks).

## Packaging (required for consumers)

When this repository is used as a pre-commit **`repo:`** (local path, git URL, etc.), pre-commit **requires** a **`.pre-commit-hooks.yaml`** file at the **repository root** listing each hook’s `id`, `entry`, `language`, and selection (`types` / `files` / `types_or`, …). Without that file, pre-commit fails with *`.pre-commit-hooks.yaml` is not a file*. See [Creating new hooks](https://pre-commit.com/#creating-new-hooks).

Keep **`.pre-commit-hooks.yaml`** in sync with each shipped hook: every **`entry`** must match a console script from **`pyproject.toml`** (`[project.scripts]`), and file selection should align with **`yaml-handling.md`** § Files and the hook’s family spec.

## Shared foundations

Shared behavior (parser, document shape, when to skip a file, stderr/exit semantics, message ordering) is defined in **`yaml-handling.md`**. Default **top-level allowed-key sets** per resource type for the **`*-allowed-keys`** family are in **`resource-keys.md`**.

**Per-hook** CLI names, arguments, numeric **exit codes**, defaults, and pre-commit `id`/`entry` details live in **hook family** specs under **`hook-families/`** (see below), not only in this file.

## Hook families

Each family groups hooks that share the same validation target and CLI shape. Add a new file under **`hook-families/`** when introducing a new family.

| Family | Spec | What it validates (summary) |
| --- | --- | --- |
| Top-level keys on each resource entry | **`hook-families/allowed-keys.md`** | Keys on each dict under `models:`, `macros:`, `seeds:`, … |
| Keys under `config.meta` | **`hook-families/config-meta-keys.md`** | Planned: optional **`--allowed`**, plus **`--required`** / **`--forbidden`**; no default allowlist in-repo (see that spec) |

Implementations **SHOULD** keep the **`*-allowed-keys`** family aligned with **`resource-keys.md`** when top-level allowlists change. The **`config` → `meta`** family uses **user-supplied** allowlists only; there is no fixed allowlist table in **`resource-keys.md`** unless we add optional convention docs later.

## Code layout (implementation)

Python **source** and **tests** **SHOULD** be organized by **hook family** in parallel with **`hook-families/*.md`** (subpackage per family, tests mirrored under **`tests/`**). Cross-family shared code stays at the package root or a small shared module. Details and naming guidance: **`project-spec.md`** § **Source and test layout (mirror hook families)**; test layout notes in **`testing-strategy.md`** § **Layout**.
