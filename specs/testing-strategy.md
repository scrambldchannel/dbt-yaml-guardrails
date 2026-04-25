# Testing strategy

**Related specs:** [`README.md`](README.md) (index), [`project-spec.md`](project-spec.md) (pytest / Python baseline), [`scope.md`](scope.md) (what the tool does not test), [`yaml-handling.md`](yaml-handling.md) (parsing rules, skip vs error, stderr, non-zero semantics), [`hooks.md`](hooks.md) (umbrella; packaging), [`hook-families/allowed-keys.md`](hook-families/allowed-keys.md) (per-hook CLIs for **`*-allowed-keys`**, **numeric exit codes**, defaults), [`hook-families/allowed-config-keys.md`](hook-families/allowed-config-keys.md) (**`*-allowed-config-keys`**; keys under **`config`**), [`hook-families/allowed-meta-keys.md`](hook-families/allowed-meta-keys.md) (**`*-allowed-meta-keys`**; **`config.meta`** key policy), [`resource-keys.md`](resource-keys.md) (top-level allowlists; **`MODEL_ALLOWED_KEYS`** in **`src/dbt_yaml_guardrails/hook_families/allowed_keys/resource_keys.py`**), [`resource-config-keys.md`](resource-config-keys.md) (defaults under **`config`** for **`*-allowed-config-keys`**; **`resource_config_keys.py`**).

## Runner

+ Use **pytest** (`uv run pytest`, aligned with [`project-spec.md`](project-spec.md)).

## Layout

+ Tests live under **`tests/`**.
+ **Family-specific** tests live under **`tests/hook_families/<family>/`** (e.g. **`tests/hook_families/allowed_keys/`** for **`*-allowed-keys`**), mirroring **`specs/hook-families/`** and **`src/dbt_yaml_guardrails/hook_families/`** (see [`project-spec.md`](project-spec.md) § **Source and test layout (mirror hook families)** and [`hooks.md`](hooks.md) § **Code layout (implementation)**). Shared parsing tests stay at **`tests/`** root (e.g. **`test_yaml_handling.py`**).
+ **YAML fixtures** **SHOULD** follow the same **hook-family** layout as **`src/`** (e.g. **`tests/fixtures/yaml/allowed_keys/`** for **`*-allowed-keys`**, **`tests/fixtures/yaml/allowed_meta_keys/`** for **`*-allowed-meta-keys`**, **`tests/fixtures/yaml/tags_accepted_values/`** for **`*-tags-accepted-values`**). **Within each family folder**, **SHOULD** place individual **`.yml`** files in a **subfolder per resource type** (e.g. **`models/`**, **`macros/`**, **`seeds/`**), matching the hooks and CLI entry points in that family. Include **good** and **bad** examples per hook; **basic edge cases** for shared parsing (invalid YAML, encoding/BOM, empty file, `version:`, multi-document streams, etc.) may live under a **`shared/`** (or similarly named) directory under that family, or under **`tests/fixtures/yaml/shared/`**, as required by [`yaml-handling.md`](yaml-handling.md) and documented by the tests that consume them.
+ **`*-allowed-meta-keys`** CLI tests **SHOULD** use **one pytest module per shipped hook** (e.g. **`test_model_allowed_meta_keys.py`**, **`test_seed_allowed_meta_keys.py`**, … under **`tests/hook_families/allowed_meta_keys/`**), parallel to **`*-allowed-keys`**. The CLIs share **`allowed_meta_keys_core.py`**, but **separate modules** keep failures and navigation readable; avoid a single heavily parametrized file that multiplexes every resource type unless there is a strong reason.

## Assertions

+ **Exit code** is the default contract: tests should assert **`0`** on success and **`1`** (or other documented non-zero codes from the hook’s family spec, e.g. [`hook-families/allowed-keys.md`](hook-families/allowed-keys.md)) when violations, parse errors, or invalid CLI usage are expected, per [`yaml-handling.md`](yaml-handling.md) § Errors
+ When testing **legacy** keys (see [`resource-keys.md`](resource-keys.md) § Legacy / deprecated for **`*-allowed-keys`** and [`resource-config-keys.md`](resource-config-keys.md) for **`*-allowed-config-keys`**, and the relevant [`hook-families/allowed-keys.md`](hook-families/allowed-keys.md) / [`hook-families/allowed-config-keys.md`](hook-families/allowed-config-keys.md) § Pattern), assert stderr includes the **Suggested violation detail** (or equivalent wording) once hooks implement that behavior.
+ **Coverage** and **pytest markers** are out of scope for now.

## Local pre-commit (manual hook smoke)

+ **Pytest** is the source of truth for **regressions and CI**; this section is an **optional, complementary** way to run **this repository’s** hook CLIs on **ad hoc** YAML while developing or debugging behavior (stderr, exit codes, and parser interaction) without adding a new pytest case every time.
+ **Ringfenced file:** maintain **one** (or a small, named set of) **YAML file(s) under a dedicated path**—conventionally **`tests/hook_sandbox/sandbox.yml`**—that is **only** for local manual runs. It is **not** a substitute for **fixtures** under **`tests/fixtures/yaml/`**; keep automated tests data-driven and stable there.
+ **Dedicated sandbox config:** sandbox hooks live in **`tests/hook_sandbox/.pre-commit-sandbox.yaml`** (a separate pre-commit config, kept out of the main **`.pre-commit-config.yaml`**). Hook entries in this file:
  + use **`entry: uv run <script-name>`** so the same **`[project.scripts]`** CLIs as consumers run;
  + do **not** need **`files:`** patterns or **`stages:`**—the target file is passed explicitly when the config is invoked;
  + pass **minimal, documented `args:`** per hook family, aligned with **[`HOOKS.md`](../HOOKS.md)** examples (e.g. **`--values`**, **`--key`**, **`--required` / `--forbidden`** as needed).
+ **Workflow:** edit **`sandbox.yml`**, then run the chosen hook (or the full manual block) and read stderr. Reset or branch the file when you are done experimenting. Prefer harmless placeholder content; do not put secrets or real PII in the sandbox file if it is committed.
+ **Coverage:** the sandbox should include **at least** the **`version:`** + resource sections needed to exercise the hooks you care about (e.g. **`models:`** + **`seeds:`** + **`snapshots:`** + **`exposures:`** + **`macros:`** in one file when the parser loads a single document with multiple top-level keys, per **[`yaml-handling.md`](yaml-handling.md)**). Hooks whose resource section is **absent** are expected to **skip** that file, same as in production.
+ **CI:** **do not** require manual pre-commit on **`tests/hook_sandbox/`** for merge gates unless the team explicitly adds a dedicated workflow step; keep **`uv run pytest`** the automated gate in **[`ci.yml`](../.github/workflows/ci.yml)**. For running the same pre-commit config you use locally inside **GitHub Actions** (clone + `pre-commit run`), see the **GitHub Actions** section in the root **[`README.md`](../README.md)**.
+ **This repository:** sandbox hooks are defined in **`tests/hook_sandbox/.pre-commit-sandbox.yaml`** (ids prefixed **`dbtg-sandbox-`**) with args aligned with **[`HOOKS.md`](../HOOKS.md)**. If **`make sandbox-hooks`** reports **(no files to check)**, the sandbox file may be untracked—run **`git add tests/hook_sandbox/sandbox.yml`** first.
+ **Makefile:** the repository includes a **`Makefile`** at the root with two targets:
  + **`make test`** → **`uv run pytest`** (automated regression suite)
  + **`make sandbox-hooks`** → runs all sandbox hooks via the dedicated config:
  ```makefile
  SANDBOX_FILE  = tests/hook_sandbox/sandbox.yml
  SANDBOX_CFG   = tests/hook_sandbox/.pre-commit-sandbox.yaml

  sandbox-hooks:
  	pre-commit run --config $(SANDBOX_CFG) --files $(SANDBOX_FILE)
  ```
  Keep the Makefile minimal—it is a convenience wrapper, not a build system. When new sandbox hooks are added to **`.pre-commit-sandbox.yaml`**, they are picked up automatically by **`make sandbox-hooks`**.

## CI

+ **GitHub Actions:** **`.github/workflows/ci.yml`** runs **`uv run pytest`** on a **Python version matrix** aligned with **`requires-python`** in **`pyproject.toml`** (currently **3.10**–**3.14**).
