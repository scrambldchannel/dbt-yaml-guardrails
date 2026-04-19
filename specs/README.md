# Specs index

Read in this order when onboarding or implementing behavior:

1. **[`project-spec.md`](project-spec.md)** — Project constitution: goal, tech stack, and workflow rules for contributors.
2. **[`scope.md`](scope.md)** — What is in and out of scope, and the Fusion-first product angle.
3. **[`yaml-handling.md`](yaml-handling.md)** — Shared contract for parsing dbt property YAML, document shape, and CLI error/exit behavior for all hooks.
4. **[`resource-keys.md`](resource-keys.md)** — Default allowed keys per resource type (Fusion-oriented); **`src/dbt_yaml_guardrails/resource_keys.py`** is the implementation source (e.g. **`MODEL_ALLOWED_KEYS`**, **`MACRO_ALLOWED_KEYS`**); extend both as new resource types are supported.
5. **[`hooks.md`](hooks.md)** — Umbrella: pre-commit packaging, **`.pre-commit-hooks.yaml`**, and an index of **hook families** under **`hook-families/`**.
6. **[`hook-families/allowed-keys.md`](hook-families/allowed-keys.md)** — **`*-allowed-keys`** hooks: pattern, **exit codes**, and each shipped CLI.
7. **[`hook-families/config-meta-keys.md`](hook-families/config-meta-keys.md)** — Planned family for **`config.meta`** key allowlists (stub).
8. **[`testing-strategy.md`](testing-strategy.md)** — Where tests and YAML fixtures live, what to assert, and CI expectations.

For a single hook implementation, read **`yaml-handling.md`** first, then **`resource-keys.md`** for defaults (when applicable), then the relevant **hook family** spec (e.g. **`hook-families/allowed-keys.md`**). When adding or changing behavior, align tests with **`testing-strategy.md`**.
