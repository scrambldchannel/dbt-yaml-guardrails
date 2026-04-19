# Specs index

The **dbt-yaml-guardrails** codebase is released under the **MIT License** (see the repository root **`LICENSE`**). Distribution is **pre-commit**-first (Git `repo:`), not PyPI—see **`project-spec.md`** § **Tech Stack & Standards**. User-facing changes by version: **[`CHANGELOG.md`](../CHANGELOG.md)** (repository root). Contribution workflow: **[`CONTRIBUTING.md`](../CONTRIBUTING.md)**.

Read in this order when onboarding or implementing behavior:

1. **[`project-spec.md`](project-spec.md)** — Project constitution: goal, tech stack, workflow rules, **root `README.md` update rules** (hook families listed separately), and **source/test layout** (mirror **`hook-families/`**).
2. **[`scope.md`](scope.md)** — What is in and out of scope, and the Fusion-first product angle.
3. **[`yaml-handling.md`](yaml-handling.md)** — Shared contract for parsing dbt property YAML, document shape, and CLI error/exit behavior for all hooks.
4. **[`resource-keys.md`](resource-keys.md)** — Default allowed keys per resource type (Fusion-oriented); **`src/dbt_yaml_guardrails/hook_families/allowed_keys/resource_keys.py`** is the implementation source (e.g. **`MODEL_ALLOWED_KEYS`**, **`MACRO_ALLOWED_KEYS`**); extend both as new resource types are supported.
5. **[`hooks.md`](hooks.md)** — Umbrella: pre-commit packaging, **`.pre-commit-hooks.yaml`**, and an index of **hook families** under **`hook-families/`**.
6. **[`hook-families/allowed-keys.md`](hook-families/allowed-keys.md)** — **`*-allowed-keys`** hooks: pattern, **exit codes**, and each shipped CLI.
7. **[`hook-families/allowed-meta-keys.md`](hook-families/allowed-meta-keys.md)** — **`*-allowed-meta-keys`** family (**`model`**, **`seed`**, **`snapshot`**, **`exposure`**, **`macro`** shipped; **`config.meta`** implied; optional **`--allowed`**, plus **`--required`** / **`--forbidden`**).
8. **[`hook-families/meta-accepted-values.md`](hook-families/meta-accepted-values.md)** — **`*-meta-accepted-values`** (specified; not shipped): string leaf at a dot path under **`meta`** (**`--key`**, **`--values`**, **`--optional`**); non-string scalars **later**. **Implementation priority:** ship this **before** nested dot paths in **`allowed-meta-keys.md`** (see both specs).
9. **[`testing-strategy.md`](testing-strategy.md)** — Where tests and YAML fixtures live, what to assert, and CI expectations.

For a single hook implementation, read **`yaml-handling.md`** first, then **`resource-keys.md`** for defaults (when applicable), then the relevant **hook family** spec (e.g. **`hook-families/allowed-keys.md`**). When adding or changing behavior, align tests with **`testing-strategy.md`**.
