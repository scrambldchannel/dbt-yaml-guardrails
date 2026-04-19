# Hooks

All hooks should follow the conventions for hooks defined for [pre-commit](https://pre-commit.com/#creating-new-hooks).

## Packaging (required for consumers)

When this repository is used as a pre-commit **`repo:`** (local path, git URL, etc.), pre-commit **requires** a **`.pre-commit-hooks.yaml`** file at the **repository root** listing each hook’s `id`, `entry`, `language`, and selection (`types` / `files` / `types_or`, …). Without that file, pre-commit fails with *`.pre-commit-hooks.yaml` is not a file*. See [Creating new hooks](https://pre-commit.com/#creating-new-hooks).

Keep **`.pre-commit-hooks.yaml`** in sync with the sections below: every shipped hook gets an entry there, with **`entry`** matching the console script from **`pyproject.toml`** (`[project.scripts]`), and file selection aligned with **`yaml-handling.md`** § Files and each hook’s notes.

Shared behavior (parser, document shape, when to skip a file, stderr/exit codes, message ordering) is defined in **`yaml-handling.md`**. Default **allowed-key sets** per resource type are in **`resource-keys.md`**. This file defines **per-hook** CLIs, arguments, and how those defaults apply.

## 1. model-allowed-keys

Validates the **top-level keys on each model entry** (each dict under the `models:` list). Document-level rules and multi-resource files are described in **`yaml-handling.md`** (see **§ dbt shape** and **§ Parsing**).

The CLI entry point and hook id should be `model-allowed-keys`.

**Arguments:**

+ `--required` — a comma-separated list of key names that must be present. The default is no keys. **`name`** is always present for real models in dbt; do not list it in `--required`.
+ `--allowed` — a comma-separated list of key names that are allowed. The default is the Fusion-oriented set in **`resource-keys.md`** § **Models** (callers may override by passing `--allowed` explicitly).
+ `--strict` — when true (the default), `--allowed` may not include keys outside the default set in **`resource-keys.md`** § **Models**. Pass **`--strict false`** (or `0` / `no` / `off`) to allow additional keys in `--allowed` (e.g. team-specific properties).
