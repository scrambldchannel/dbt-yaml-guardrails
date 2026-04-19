# Project Constitution: dbt-yaml-guardrails

## 1. Goal

Build a set of pre-commit hooks that apply configurable standards to dbt yaml that define properties for dbt resource types (e.g. models, macros, sources etc) with a focus on a dbt Fusion mindset.

## 2. Tech Stack & Standards
- **Language:** Python 3.10+
- **Tooling:** uv, pytest, github
- **Libraries** ruamel.yaml, typer

### Source and test layout (mirror hook families)

Specs group hooks by **family** under **`specs/hook-families/`** (e.g. **`allowed-keys.md`**, **`config-meta-keys.md`**). The Python package and tests **SHOULD** follow the same grouping so growth stays navigable:

+ **`src/dbt_yaml_guardrails/`** — Put code for each family under a subpackage (or clearly named subfolder) that corresponds to that family (e.g. **`hook_families/allowed_keys/`** for the **`*-allowed-keys`** family, **`hook_families/config_meta_keys/`** for **`config` → `meta`** hooks). Keep **cross-family** modules (YAML loading, shared validation cores, shared types) at the package root or under a small **`_internal`** / **`common`** name if needed.
+ **`tests/`** — Mirror the same structure: family-scoped tests under **`tests/hook_families/<family>/`** (or equivalent), with **`tests/fixtures/yaml/`** optionally split into subfolders per family if file volume warrants it.

This is a **SHOULD**, not a hard gate: older flat modules may remain until refactored; **new** hooks and families **SHOULD** adopt the layout above. See also **`hooks.md`** § **Code layout (implementation)**.

## 3. Rules & Guidelines for Cursor
- Read `README.md`, `specs/project-spec.md`, and **`specs/README.md`** (for spec reading order and links) before starting any task.
- Use atomic commits via `git` after each functional component completion.

## 4. Workflow
1. Stop and allow human review before proceeding to the next task.

## 5. Deferred / optional implementation notes

+ **`*-allowed-keys` Typer boilerplate:** validation is shared (**`hook_families/allowed_keys/allowed_keys_core.py`**); per-hook entry modules may still repeat Typer **`main`** / **`cli_main`**. A factory to reduce that duplication is **optional**—see **`hook-families/allowed-keys.md`** § **Typer CLI entry modules (optional refactor)**.
