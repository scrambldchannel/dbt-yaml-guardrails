# Project Constitution: dbt-yaml-guardrails

## 1. Goal

Build a set of pre-commit hooks that apply configurable standards to dbt yaml that define properties for dbt resource types (e.g. models, macros, sources etc) with a focus on a dbt Fusion mindset.

## 2. Tech Stack & Standards
- **Language:** Python 3.10+
- **Tooling:** uv, pytest, github
- **Development dependencies (lockstep with `pyproject.toml`):** **pytest**, **pytest-cov**, and **vulture** are listed under **`[dependency-groups].dev`** (PEP 735) — they are for **contributors and CI** only, not part of published wheel install requirements. The **`dev`** group is the single source of truth; do **not** duplicate the same tools under **`[project.optional-dependencies]`** unless we intentionally add a *user-facing* **extra** (optional runtime feature) in the future. **uv** includes the **`dev`** group by default on **`uv sync`**. Add dev tools with **`uv add --dev <package>`**; see **`CONTRIBUTING.md`**.
- **Libraries:** ruamel.yaml, typer
- **License:** MIT — see **`LICENSE`**, **`pyproject.toml`** (`authors`, `[project.urls]` for the GitHub repo and Issues)
- **Distribution:** The **primary** way to use these hooks is **[pre-commit](https://pre-commit.com/)** with this repository as the **`repo:`** source (see **`.pre-commit-hooks.yaml`**, **`hooks.md`**). **PyPI publication is not** a project goal; **`keywords`**, **`classifiers`**, and other **`[project]`** metadata exist for documentation, IDE tooling, and consistency—not for publishing a package to the index.
- **Release notes:** Maintain **`CHANGELOG.md`** at the repository root when cutting a version; align the **`version`** field in **`pyproject.toml`** and **git tags** (e.g. **`v0.7.0`**). When you ship, update the **`rev:`** in the **pre-commit example** in **[`HOOKS.md`](../HOOKS.md)** (and keep the root **`README.md`** accurate if it references a **`rev:`**) so it matches the **latest release tag** (same as **`v<version>`** from **`pyproject.toml`**), so copy-paste installs stay pinned to what you just released. The **date** on each **`## [x.y.z] — <date>`** line **should** match the **calendar date** of the **commit to `main`** that ships that version (the version-bump commit), so the changelog order stays chronological and reflects when the release actually landed.
- **Changelog tone:** For releases **0.4.3 and later**, write **`CHANGELOG.md`** for **readers of the product**, not an audit of every file touched. Use short bullets that describe **what users get** (new hooks, behavior fixes, notable spec or breaking changes). Do **not** list implementation paths, Python modules, or test file paths **unless** that path is itself the user-facing fact (e.g. a single new doc is the deliverable). **`specs/`** and the git history remain where implementors look for detail. The **Style** note at the top of **`CHANGELOG.md`** restates this.
- **Test coverage (pytest) before release:** In addition to **`uv run pytest`** (or **`make test`**, same suite) for correctness, run **`make coverage`** from the repository root. That target runs the test suite with **[Coverage.py](https://coverage.readthedocs.io/)** via **`pytest-cov`**, with **`--cov-config pyproject.toml`**, so **`[tool.coverage.run]`** / **`[tool.coverage.report]`** (what to measure, how to print gaps) are the source of truth—not ad-hoc `pytest`/`coverage` flags. A terminal summary and an **`htmlcov/`** report (for spot-checking) are written; that directory and **`.coverage`** are git-ignored. This **SHOULD** be part of the pre-ship pass before the version-bump commit merges to **`main`**. (Coverage answers “what is exercised by tests?”, which is complementary to Vulture’s “what is unused?”; neither replaces the other.)
- **Dead code (Vulture) before release:** As part of the same pre-ship check as tests and **`CHANGELOG`**, run **`make vulture`** from the repository root (see root **`Makefile`**). That target runs Vulture with **`--config pyproject.toml`**, so settings under **`[tool.vulture]`** (e.g. **`paths`**, **`min_confidence`**, and any optional options such as **`ignore_names`**) apply consistently. **Do not** hand-type a different Vulture command line for releases—the **Makefile** and config are the source of truth. The run **SHOULD** exit **0** before the version-bump commit is merged to **`main`**.
- **Automated GitHub releases:** **`.github/workflows/release.yml`** runs on pushes to **`main`** that touch **`pyproject.toml`**. It reads **`project.version`**, and if **`v<version>`** is not already a tag, it creates that tag on the pushed commit and opens a **GitHub Release** (auto-generated notes). Bump **`version`** and update **`CHANGELOG.md`** in the **same commit** you intend to ship so the release matches your notes.
- **Release process: confirm version; never auto-push:** Before any version bump or **CHANGELOG** entry for a release, **confirm** the exact **version string** and **SemVer intent** (patch **0.6.1** vs minor **0.7.0** vs major) with the **maintainer**—do not assume from informal wording. **Do not** run **`git push`** to **`origin`** (or any remote) while preparing a release: finish with a **local** commit (or stop before commit if the maintainer prefers). **Pushing** to **`origin`** is **always** at the **developer’s sole discretion** and triggers CI / the tag workflow only when *they* run it; list the exact **`git push …`** command in chat if helpful, but **do not** execute it unless the maintainer has asked you to in that session.

### Docstrings

Where a docstring is worth having (public APIs, non-obvious behavior, shared cores), use **Google style** sections (`Args:`, `Returns:`, `Raises:`, …). Skip docstrings that only restate the name of the function.

### README.md and HOOKS.md (repository root)

The root **`README.md`** is the project entry (goal, links). The **hook inventory**—families, tables, CLI flag summaries, and the **pre-commit** example—lives in **[`HOOKS.md`](../HOOKS.md)**.

When adding or renaming hooks, update **`HOOKS.md`** so it stays accurate for consumers. **Hook families MUST be listed separately** (e.g. one table or section for **`*-allowed-keys`** and another for **`*-allowed-meta-keys`**)—do not merge unrelated families into a single undifferentiated list. Order within a family can follow **`specs/hook-families/`** and **[`pyproject.toml`](../pyproject.toml)** **`[project.scripts]`**.

**Complete hook inventory (required):** **`HOOKS.md` MUST document every shipped hook**—every pre-commit **`id`** in **[`.pre-commit-hooks.yaml`](../.pre-commit-hooks.yaml)** (in lockstep with **`[project.scripts]`** in **`pyproject.toml`**) **MUST** appear in the per-family **ID** / **Validates** tables (or an equivalent explicit listing in that file). No shipped hook may be missing from the documented inventory. The **`repos:`** / **`hooks:`** copy-paste example at the end of **`HOOKS.md` SHOULD** list **all** those **`id`s** as separate **`- id:`** stanzas; if the example is shortened for readability, a short **note in that section** must state that the **tables** (and **`.pre-commit-hooks.yaml`**) are the full list. The example’s **`rev:`** **SHOULD** match the **current latest release tag** (see **Release notes** above); avoid leaving **`main`** in the committed example unless documenting a deliberate “bleeding edge” workflow.

### Source and test layout (mirror hook families)

Specs group hooks by **family** under **`specs/hook-families/`** (e.g. **`allowed-keys.md`**, **`allowed-meta-keys.md`**). The Python package and tests **SHOULD** follow the same grouping so growth stays navigable:

+ **`src/dbt_yaml_guardrails/`** — Put code for each family under a subpackage (or clearly named subfolder) that corresponds to that family (e.g. **`hook_families/allowed_keys/`** for the **`*-allowed-keys`** family, **`hook_families/allowed_meta_keys/`** for the **`*-allowed-meta-keys`** family (keys under **`config.meta`**)). Keep **cross-family** modules (YAML loading, shared validation cores, shared types) at the package root or under a small **`_internal`** / **`common`** name if needed.
+ **`tests/`** — Mirror the same structure: family-scoped tests under **`tests/hook_families/<family>/`** (or equivalent), with **`tests/fixtures/yaml/`** optionally split into subfolders per family if file volume warrants it.

This is a **SHOULD**, not a hard gate: older flat modules may remain until refactored; **new** hooks and families **SHOULD** adopt the layout above. See also **`hooks.md`** § **Code layout (implementation)**.

## 3. Rules & Guidelines for Cursor
- Read `README.md`, **`HOOKS.md`** (when changing hooks), **`CHANGELOG.md`** (when changing user-visible behavior or versioning), `specs/project-spec.md`, and **`specs/README.md`** (for spec reading order and links) before starting any task. Contributors: **[`CONTRIBUTING.md`](../CONTRIBUTING.md)** (dev setup, tests, spec-driven expectations).
- Use atomic commits via `git` after each functional component completion.
- **Releases:** follow **§2 Release process: confirm version; never auto-push**—confirm the target version and patch/minor/major with the maintainer before changing **`pyproject.toml`** / **CHANGELOG**; **never** **`git push`** to **`origin`** unless the maintainer has explicitly asked you to run that command.

## 4. Workflow
1. Stop and allow human review before proceeding to the next task.

## 5. Deferred / optional implementation notes

+ **`*-allowed-keys` Typer boilerplate:** validation is shared (**`hook_families/allowed_keys/allowed_keys_core.py`**); per-hook entry modules may still repeat Typer **`main`** / **`cli_main`**. A factory to reduce that duplication is **optional**—see **`hook-families/allowed-keys.md`** § **Typer CLI entry modules (optional refactor)**.
