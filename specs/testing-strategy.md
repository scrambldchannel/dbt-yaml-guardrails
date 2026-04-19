# Testing strategy

**Related specs:** [`README.md`](README.md) (index), [`project-spec.md`](project-spec.md) (pytest / Python baseline), [`scope.md`](scope.md) (what the tool does not test), [`yaml-handling.md`](yaml-handling.md) (parsing rules, skip vs error, stderr, non-zero semantics), [`hooks.md`](hooks.md) (umbrella; packaging), [`hook-families/allowed-keys.md`](hook-families/allowed-keys.md) (per-hook CLIs for **`*-allowed-keys`**, **numeric exit codes**, defaults), [`hook-families/allowed-meta-keys.md`](hook-families/allowed-meta-keys.md) (**`*-allowed-meta-keys`**; **`config.meta`** key policy), [`resource-keys.md`](resource-keys.md) (documented allowlists; **`MODEL_ALLOWED_KEYS`** in **`src/dbt_yaml_guardrails/hook_families/allowed_keys/resource_keys.py`** is the implementation source for models).

## Runner

+ Use **pytest** (`uv run pytest`, aligned with [`project-spec.md`](project-spec.md)).

## Layout

+ Tests live under **`tests/`**.
+ **Family-specific** tests live under **`tests/hook_families/<family>/`** (e.g. **`tests/hook_families/allowed_keys/`** for **`*-allowed-keys`**), mirroring **`specs/hook-families/`** and **`src/dbt_yaml_guardrails/hook_families/`** (see [`project-spec.md`](project-spec.md) § **Source and test layout (mirror hook families)** and [`hooks.md`](hooks.md) § **Code layout (implementation)**). Shared parsing tests stay at **`tests/`** root (e.g. **`test_yaml_handling.py`**).
+ **YAML fixtures** **SHOULD** follow the same **hook-family** layout as **`src/`** (e.g. **`tests/fixtures/yaml/allowed_keys/`** for **`*-allowed-keys`**, and **`tests/fixtures/yaml/allowed_meta_keys/`** for **`*-allowed-meta-keys`** when implemented). **Within each family folder**, **SHOULD** place individual **`.yml`** files in a **subfolder per resource type** (e.g. **`models/`**, **`macros/`**, **`seeds/`**), matching the hooks and CLI entry points in that family. Include **good** and **bad** examples per hook; **basic edge cases** for shared parsing (invalid YAML, encoding/BOM, empty file, `version:`, multi-document streams, etc.) may live under a **`shared/`** (or similarly named) directory under that family, or under **`tests/fixtures/yaml/shared/`**, as required by [`yaml-handling.md`](yaml-handling.md) and documented by the tests that consume them.

## Assertions

+ **Exit code** is the default contract: tests should assert **`0`** on success and **`1`** (or other documented non-zero codes from the hook’s family spec, e.g. [`hook-families/allowed-keys.md`](hook-families/allowed-keys.md)) when violations, parse errors, or invalid CLI usage are expected, per [`yaml-handling.md`](yaml-handling.md) § Errors
+ When testing **legacy** keys (see [`resource-keys.md`](resource-keys.md) § Legacy / deprecated and [`hook-families/allowed-keys.md`](hook-families/allowed-keys.md) § Pattern), assert stderr includes the **Suggested violation detail** (or equivalent wording) once hooks implement that behavior.
+ **Coverage** and **pytest markers** are out of scope for now.

## CI

+ **GitHub Actions:** **`.github/workflows/ci.yml`** runs **`uv run pytest`** on a **Python version matrix** aligned with **`requires-python`** in **`pyproject.toml`** (currently **3.10**–**3.14**).
