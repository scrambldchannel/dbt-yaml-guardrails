# Testing strategy

**Related specs:** [`README.md`](README.md) (index), [`project-spec.md`](project-spec.md) (pytest / Python baseline), [`scope.md`](scope.md) (what the tool does not test), [`yaml-handling.md`](yaml-handling.md) (parsing rules, skip vs error, stderr, non-zero semantics), [`hooks.md`](hooks.md) (per-hook CLIs, **numeric exit codes**, defaults), [`resource-keys.md`](resource-keys.md) (documented allowlists; **`MODEL_ALLOWED_KEYS`** in **`resource_keys.py`** is the implementation source for models).

## Runner

+ Use **pytest** (`uv run pytest`, aligned with [`project-spec.md`](project-spec.md)).

## Layout

+ Tests live under **`tests/`**.
+ Shared YAML snippets live under **`tests/fixtures/yaml/`** — include **good** and **bad** examples **per hook**, plus **basic edge cases** for shared parsing behavior (invalid YAML, encoding/BOM, empty file, `version:`, multi-document streams, etc.) as required by [`yaml-handling.md`](yaml-handling.md).

## Assertions

+ **Exit code** is the default contract: tests should assert **`0`** on success and **`1`** (or other documented non-zero codes from [`hooks.md`](hooks.md)) when violations, parse errors, or invalid CLI usage are expected, per [`yaml-handling.md`](yaml-handling.md) § Errors and [`hooks.md`](hooks.md) **Exit codes**
+ **Coverage** and **pytest markers** are out of scope for now.

## CI

+ **GitHub Actions:** **`.github/workflows/ci.yml`** runs **`uv run pytest`** on a **Python version matrix** aligned with **`requires-python`** in **`pyproject.toml`** (currently **3.10**–**3.14**).
