# Testing strategy

**Related specs:** [`README.md`](README.md) (index), [`project-spec.md`](project-spec.md) (pytest / Python baseline), [`scope.md`](scope.md) (what the tool does not test), [`yaml-handling.md`](yaml-handling.md) (parsing rules, skip vs error, exit codes, stderr), [`hooks.md`](hooks.md) (per-hook CLIs and defaults).

## Runner

+ Use **pytest** (`uv run pytest`, aligned with [`project-spec.md`](project-spec.md)).

## Layout

+ Tests live under **`tests/`**.
+ Shared YAML snippets live under **`tests/fixtures/yaml/`** — include **good** and **bad** examples **per hook**, plus **basic edge cases** for shared parsing behavior (invalid YAML, encoding/BOM, empty file, `version:`, multi-document streams, etc.) as required by [`yaml-handling.md`](yaml-handling.md).

## Assertions

+ **Exit code** is the default contract: tests should assert **0** on success and **non-zero** when violations or parse errors are expected, per [`yaml-handling.md`](yaml-handling.md) § Errors.
+ **Coverage** and **pytest markers** are out of scope for now.

## CI

+ Add a **GitHub Actions** workflow under **`.github/workflows/`** that runs the **full pytest suite** on **all Python versions the project supports** (same range as **`requires-python`** / [`project-spec.md`](project-spec.md); use a version matrix).
