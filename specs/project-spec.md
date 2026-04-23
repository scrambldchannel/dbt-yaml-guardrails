# Project Constitution: dbt-yaml-guardrails

## 1. Goal

Build a set of pre-commit hooks that apply configurable standards to dbt yaml that define properties for dbt resource types (e.g. models, macros, sources etc) with a focus on a dbt Fusion mindset.

## 2. Tech Stack & Standards
- **Language:** Python 3.10+
- **Tooling:** uv, pytest, github
- **Libraries:** ruamel.yaml, typer
- **License:** MIT — see **`LICENSE`**, **`pyproject.toml`** (`authors`, `[project.urls]` for the GitHub repo and Issues)
- **Distribution:** The **primary** way to use these hooks is **[pre-commit](https://pre-commit.com/)** with this repository as the **`repo:`** source (see **`.pre-commit-hooks.yaml`**, **`hooks.md`**). **PyPI publication is not** a project goal; **`keywords`**, **`classifiers`**, and other **`[project]`** metadata exist for documentation, IDE tooling, and consistency—not for publishing a package to the index.
- **Release notes:** Maintain **`CHANGELOG.md`** at the repository root when cutting a version; align the **`version`** field in **`pyproject.toml`** and **git tags** (e.g. **`v0.4.2`**). When you ship, update the **`rev:`** in the **pre-commit example** in **[`HOOKS.md`](../HOOKS.md)** (and keep the root **`README.md`** accurate if it references a **`rev:`**) so it matches the **latest release tag** (same as **`v<version>`** from **`pyproject.toml`**), so copy-paste installs stay pinned to what you just released. The **date** on each **`## [x.y.z] — <date>`** line **should** match the **calendar date** of the **commit to `main`** that ships that version (the version-bump commit), so the changelog order stays chronological and reflects when the release actually landed.
- **Automated GitHub releases:** **`.github/workflows/release.yml`** runs on pushes to **`main`** that touch **`pyproject.toml`**. It reads **`project.version`**, and if **`v<version>`** is not already a tag, it creates that tag on the pushed commit and opens a **GitHub Release** (auto-generated notes). Bump **`version`** and update **`CHANGELOG.md`** in the **same commit** you intend to ship so the release matches your notes.

### Docstrings

Where a docstring is worth having (public APIs, non-obvious behavior, shared cores), use **Google style** sections (`Args:`, `Returns:`, `Raises:`, …). Skip docstrings that only restate the name of the function.

### README.md and HOOKS.md (repository root)

The root **`README.md`** is the project entry (goal, links). The **hook inventory**—families, tables, CLI flag summaries, and the **pre-commit** example—lives in **[`HOOKS.md`](../HOOKS.md)**.

When adding or renaming hooks, update **`HOOKS.md`** so it stays accurate for consumers. **Hook families MUST be listed separately** (e.g. one table or section for **`*-allowed-keys`** and another for **`*-allowed-meta-keys`**)—do not merge unrelated families into a single undifferentiated list. Order within a family can follow **`specs/hook-families/`** and **[`pyproject.toml`](../pyproject.toml)** **`[project.scripts]`**. The hook inventory **SHOULD** align with **[`.pre-commit-hooks.yaml`](../.pre-commit-hooks.yaml)** and **`hooks.md`** § **Hook families**; the pre-commit config example should include at least one hook per family or note where families are omitted for brevity. The example’s **`rev:`** **SHOULD** match the **current latest release tag** (see **Release notes** above); avoid leaving **`main`** in the committed example unless documenting a deliberate “bleeding edge” workflow.

### Source and test layout (mirror hook families)

Specs group hooks by **family** under **`specs/hook-families/`** (e.g. **`allowed-keys.md`**, **`allowed-meta-keys.md`**). The Python package and tests **SHOULD** follow the same grouping so growth stays navigable:

+ **`src/dbt_yaml_guardrails/`** — Put code for each family under a subpackage (or clearly named subfolder) that corresponds to that family (e.g. **`hook_families/allowed_keys/`** for the **`*-allowed-keys`** family, **`hook_families/allowed_meta_keys/`** for the **`*-allowed-meta-keys`** family (keys under **`config.meta`**)). Keep **cross-family** modules (YAML loading, shared validation cores, shared types) at the package root or under a small **`_internal`** / **`common`** name if needed.
+ **`tests/`** — Mirror the same structure: family-scoped tests under **`tests/hook_families/<family>/`** (or equivalent), with **`tests/fixtures/yaml/`** optionally split into subfolders per family if file volume warrants it.

This is a **SHOULD**, not a hard gate: older flat modules may remain until refactored; **new** hooks and families **SHOULD** adopt the layout above. See also **`hooks.md`** § **Code layout (implementation)**.

## 3. Rules & Guidelines for Cursor
- Read `README.md`, **`HOOKS.md`** (when changing hooks), **`CHANGELOG.md`** (when changing user-visible behavior or versioning), `specs/project-spec.md`, and **`specs/README.md`** (for spec reading order and links) before starting any task. Contributors: **[`CONTRIBUTING.md`](../CONTRIBUTING.md)** (dev setup, tests, spec-driven expectations).
- Use atomic commits via `git` after each functional component completion.

## 4. Workflow
1. Stop and allow human review before proceeding to the next task.

## 5. Deferred / optional implementation notes

+ **`*-allowed-keys` Typer boilerplate:** validation is shared (**`hook_families/allowed_keys/allowed_keys_core.py`**); per-hook entry modules may still repeat Typer **`main`** / **`cli_main`**. A factory to reduce that duplication is **optional**—see **`hook-families/allowed-keys.md`** § **Typer CLI entry modules (optional refactor)**.
+ **CI / GitHub feedback (future):** surfacing hook violations in pull requests (e.g. [workflow **annotations** (`::error` / `::notice` with `file` and `line`)](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/workflow-commands-for-github-actions), a **summary or inline review comment** from a wrapper Action, or tools like [reviewdog](https://github.com/reviewdog/reviewdog)) is **not** required for the core hook or CLI work; treat it as an optional product layer once the hook API and message shape are stable enough to map violations to locations reliably.
