# Contributing

**Be kind** — assume good intent, keep feedback specific and respectful.

## Spec-driven development

Behavior lives in **`specs/`**. Start from **[`specs/README.md`](specs/README.md)** (reading order) and **[`specs/project-spec.md`](specs/project-spec.md)** (constitution). Change or extend specs **before** or **with** code so reviews stay grounded in written intent.

## Dev environment & tests

Requires **Python 3.10+** and **[uv](https://docs.astral.sh/uv/)**.

```bash
uv sync --extra dev
uv run pytest
```

Details: **[`specs/testing-strategy.md`](specs/testing-strategy.md)**.

### Ad hoc hook runs (optional)

For quick, hands-on checks of stderr and exit codes without writing a new pytest case, use the **ringfenced** file **[`tests/hook_sandbox/sandbox.yml`](tests/hook_sandbox/sandbox.yml)** and the **`dbtg-sandbox-*`** hooks in **[`.pre-commit-config.yaml`](.pre-commit-config.yaml)**. They use **`uv run …`**, are scoped to that YAML only, and use **`stages: [manual]`** so they do not run on a normal commit. Run one hook, for example:

```bash
pre-commit run dbtg-sandbox-model-allowed-keys --hook-stage manual --files tests/hook_sandbox/sandbox.yml
```

Full write-up: **[`specs/testing-strategy.md`](specs/testing-strategy.md)** § **Local pre-commit (manual hook smoke)**.

## Changelog

When a PR ships a new version, update **[`CHANGELOG.md`](CHANGELOG.md)** and align **`version`** with **`project-spec.md`** (see that doc’s **Release notes** / **Changelog tone**—write for users, not a file list).

## Issues and pull requests

GitHub **[issue templates](.github/ISSUE_TEMPLATE/)** and **[`pull_request_template.md`](.github/pull_request_template.md)** mirror this doc: **spec-first** changes, clear repros for bugs, and **`uv run pytest`** before review when you touch behavior.
