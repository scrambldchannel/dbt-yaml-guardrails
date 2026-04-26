# Contributing

**Be kind** — assume good intent, keep feedback specific and respectful.

## Spec-driven development

Behavior lives in **`specs/`**. Start from **[`specs/README.md`](specs/README.md)** (reading order) and **[`specs/project-spec.md`](specs/project-spec.md)** (constitution). Change or extend specs **before** or **with** code so reviews stay grounded in written intent.

## Dev environment & tests

Requires **Python 3.10+** and **[uv](https://docs.astral.sh/uv/)**.

Install dependencies and run the suite:

```bash
uv sync
uv run pytest
```

**How dev tools are declared:** the repo follows **PEP 735** — development-only packages live in **`[dependency-groups].dev`** in **`pyproject.toml`** (pytest, pytest-cov, vulture), not in **`[project.optional-dependencies]`**. Extras in **`[project.optional-dependencies]`** are for *optional runtime features* users install with **`pip install package[extra]`** and are listed in published package metadata; this project is **not** published to PyPI, and we do not use extras. With **uv**, the **`dev`** group is **included by default** on plain **`uv sync`**, so local setup and **CI** (see [`.github/workflows/ci.yml`](.github/workflows/ci.yml)) stay aligned. Add a dev dep with **`uv add --dev <name>`** (it updates `[dependency-groups].dev`).

**Other installers:** a plain **`pip install -e .`** does not apply PEP 735 **dependency-groups**; use **uv** for this repo. We would only document **`pip install -e .[some_extra]`** if **`[project.optional-dependencies]`** gains a *runtime* extra in the future.

**Makefile** (repo root) wraps common commands:

| Target | What it does |
|--------|----------------|
| **`make test`** | **`uv run pytest`**
| **`make vulture`** | Dead-code scan with config from **`pyproject.toml`**
| **`make coverage`** | Full pytest + Coverage.py (see **`[tool.coverage.*]`**)
| **`make check`** | **`test`** then **`vulture`** (handy before a push)
| **`make release-check`** | **`test`**, then **`vulture`**, then **`coverage`** (pre-ship bundle)
| **`make sandbox-hooks`** | Manual pre-commit on the ringfenced sandbox (see below)

**Before a release** (or when you want the full maintainer pass), also follow **[`project-spec.md`](specs/project-spec.md)** § **Test coverage** and **Dead code (Vulture)**—same commands as **`make release-check`**, with notes there on **`CHANGELOG`**, version bumps, and **`rev:`** pins.

Details on layout, fixtures, and optional sandbox runs: **[`specs/testing-strategy.md`](specs/testing-strategy.md)**.

### Ad hoc hook runs (optional)

For quick, hands-on checks of stderr and exit codes without writing a new pytest case, use the **ringfenced** file **[`tests/hook_sandbox/sandbox.yml`](tests/hook_sandbox/sandbox.yml)** and the **`dbtg-sandbox-*`** hooks in **[`tests/hook_sandbox/.pre-commit-sandbox.yaml`](tests/hook_sandbox/.pre-commit-sandbox.yaml)**. They use **`uv run …`**, are scoped to that YAML only, and use **`stages: [manual]`** so they do not run on a normal commit. Run one hook, for example:

```bash
pre-commit run dbtg-sandbox-model-allowed-keys --hook-stage manual --files tests/hook_sandbox/sandbox.yml
```

Full write-up: **[`specs/testing-strategy.md`](specs/testing-strategy.md)** § **Local pre-commit (manual hook smoke)**.

## Changelog

When a PR ships a new version, update **[`CHANGELOG.md`](CHANGELOG.md)** and align **`version`** with **`project-spec.md`** (see that doc’s **Release notes** / **Changelog tone**—write for users, not a file list).

## Issues and pull requests

GitHub **[issue templates](.github/ISSUE_TEMPLATE/)** and **[`pull_request_template.md`](.github/pull_request_template.md)** mirror this doc: **spec-first** changes, clear repros for bugs, and **`uv run pytest`** before review when you touch behavior.
