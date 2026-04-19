# Specs index

Read in this order when onboarding or implementing behavior:

1. **[`project-spec.md`](project-spec.md)** — Project constitution: goal, tech stack, and workflow rules for contributors.
2. **[`scope.md`](scope.md)** — What is in and out of scope, and the Fusion-first product angle.
3. **[`yaml-handling.md`](yaml-handling.md)** — Shared contract for parsing dbt property YAML, document shape, and CLI error/exit behavior for all hooks.
4. **[`hooks.md`](hooks.md)** — Catalog of hooks: CLI names, arguments, defaults, and (as they are defined) pre-commit integration details per hook.
5. **[`testing-strategy.md`](testing-strategy.md)** — Where tests and YAML fixtures live, what to assert, and CI expectations.

For a single hook implementation, read **`yaml-handling.md`** first, then the relevant section in **`hooks.md`**. When adding or changing behavior, align tests with **`testing-strategy.md`**.
