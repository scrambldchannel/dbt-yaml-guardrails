# Specs index

The **dbt-yaml-guardrails** codebase is released under the **MIT License** (see the repository root **`LICENSE`**). Distribution is **pre-commit**-first (Git `repo:`), not PyPI—see **`project-spec.md`** § **Tech Stack & Standards**. User-facing changes by version: **[`CHANGELOG.md`](../CHANGELOG.md)** (repository root). Contribution workflow: **[`CONTRIBUTING.md`](../CONTRIBUTING.md)**.

Read in this order when onboarding or implementing behavior:

1. **[`project-spec.md`](project-spec.md)** — Project constitution: goal, tech stack, workflow rules, **root `README.md` / `HOOKS.md`** (hook catalog in **`HOOKS.md`**; families listed separately), and **source/test layout** (mirror **`hook-families/`**).
2. **[`scope.md`](scope.md)** — What is in and out of scope, and the Fusion-first product angle.
3. **[`yaml-handling.md`](yaml-handling.md)** — Shared contract for parsing dbt property YAML, document shape, and CLI error/exit behavior for all hooks.
4. **[`resource-keys.md`](resource-keys.md)** — Default allowlists for **`*-allowed-keys`**: top-level keys in **property YAML** (per dbt resource properties) and, for **`dbt-project-allowed-keys`**, the **`dbt_project.yml`** root (§ **dbt project file**); not manifest-only fields. **`src/dbt_yaml_guardrails/hook_families/allowed_keys/resource_keys.py`** is the implementation source; keep it in sync with dbt’s published surface.
5. **[`resource-config-keys.md`](resource-config-keys.md)** — Default keys **under each entry’s `config:`** for **`*-allowed-config-keys`** (see **`hook-families/allowed-config-keys.md`**); **`resource_config_keys.py`** implements frozen allowlists for all shipped resources.
6. **[`hooks.md`](hooks.md)** — Umbrella: pre-commit packaging, **`.pre-commit-hooks.yaml`**, and an index of **hook families** under **`hook-families/`**.
7. **[`hook-families/allowed-keys.md`](hook-families/allowed-keys.md)** — **`*-allowed-keys`** hooks: pattern, **exit codes**, and each shipped CLI (**`model`**, **`macro`**, **`seed`**, **`source`**, **`snapshot`**, **`exposure`**, **`catalog`**, **`dbt-project`**, …).
8. **[`hook-families/allowed-config-keys.md`](hook-families/allowed-config-keys.md)** — **`*-allowed-config-keys`**: keys under each resource’s **`config`** mapping; same CLI pattern as **`*-allowed-keys`**; default allowlists in **`resource-config-keys.md`**; **`model`**, **`macro`**, **`seed`**, **`source`**, **`snapshot`**, **`exposure`** shipped.
9. **[`hook-families/dbt-yaml-legacy.md`](hook-families/dbt-yaml-legacy.md)** — **Mechanical legacy rewrites** (`dbt-yaml-legacy` hook, check / `--write`). v1: **`tests` → `data_tests` only;** future: top-level **`meta` / `tags`** into **`config`**. Complements the validator families; does not replace them.
10. **[`hook-families/allowed-meta-keys.md`](hook-families/allowed-meta-keys.md)** — **`*-allowed-meta-keys`** family (**`model`**, **`seed`**, **`snapshot`**, **`exposure`**, **`source`**, **`macro`** shipped; **`config.meta`** implied; optional **`--allowed`**, plus **`--required`** / **`--forbidden`**).
11. **[`hook-families/meta-accepted-values.md`](hook-families/meta-accepted-values.md)** — **`*-meta-accepted-values`**: string or string list at a dot path under **`meta`** (**`--key`**, **`--values`**, **`--optional`**); **`model`**, **`seed`**, **`snapshot`**, **`exposure`**, **`source`**, **`macro`** shipped; non-string scalars **later** (see that spec).
12. **[`hook-families/tags-accepted-values.md`](hook-families/tags-accepted-values.md)** — **`*-tags-accepted-values`**: allowlist **`config.tags`** with **`--values`** only; **`model`**, **`seed`**, **`snapshot`**, **`exposure`**, **`source`**, **`macro`** shipped.
13. **[`testing-strategy.md`](testing-strategy.md)** — Where tests and YAML fixtures live, what to assert, and CI expectations.

For a single hook implementation, read **`yaml-handling.md`** first, then **`resource-keys.md`** and **`resource-config-keys.md`** for defaults (when applicable), then the relevant **hook family** spec (e.g. **`hook-families/allowed-keys.md`**). When adding or changing behavior, align tests with **`testing-strategy.md`**.
