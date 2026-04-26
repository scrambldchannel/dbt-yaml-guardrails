# Hooks

Shipped pre-commit hooks for this repository. Families match [`specs/hooks.md`](specs/hooks.md); per-family behavior and exit codes live under [`specs/hook-families/`](specs/hook-families/).

Hooks are grouped by **family**. Each family has its own CLI shape.

## `*-allowed-keys`

Top-level keys on each resource entry in property YAML, or the root mapping of `dbt_project.yml` for **`dbt-project-allowed-keys`**. For the six property-YAML hooks (`model` through `source`), **direct keys under each entry's `config:` mapping are also validated by default** using the same Fusion-oriented allowlists as `*-allowed-config-keys` (see `--check-config` below).

| ID | Validates |
| --- | --- |
| `model-allowed-keys` | Top-level keys on each `models:` entry; also `config:` child keys by default |
| `macro-allowed-keys` | Top-level keys on each `macros:` entry; also `config:` child keys by default |
| `seed-allowed-keys` | Top-level keys on each `seeds:` entry; also `config:` child keys by default |
| `source-allowed-keys` | Top-level keys on each `sources:` entry; also `config:` child keys by default |
| `snapshot-allowed-keys` | Top-level keys on each `snapshots:` entry; also `config:` child keys by default |
| `exposure-allowed-keys` | Top-level keys on each `exposures:` entry; also `config:` child keys by default |
| `catalog-allowed-keys` | Top-level keys on each `catalogs:` entry (dbt 1.10+) |
| `dbt-project-allowed-keys` | Top-level keys in the project root of `dbt_project.yml` |

These hooks use a **fixed allowlist** from [`specs/resource-keys.md`](specs/resource-keys.md) for that resource type. On top of that:

- **`--required`** — comma-separated keys that **must** appear on every entry (e.g. enforce `description` everywhere). For list-shaped resources, do not list `name` in `--required` (exit code 2). **`dbt-project-allowed-keys`** may use **`--required name`** (or **`config-version`**, **`profile`**, etc.) to enforce the project file. Does **not** apply to keys under `config:` — use `*-allowed-config-keys` for that.
- **`--forbidden`** — comma-separated keys that **must not** appear on an entry, even when they would otherwise be allowed—use this for stricter team rules (e.g. forbid `config` on models so configuration lives only in `dbt_project.yml`). Does **not** apply to keys under `config:`.
- **`--check-config`** — (`true` / `false`, default `true`) — when `true`, the six property-YAML hooks also validate **direct keys under each entry's `config:`** against the same default allowlists as `*-allowed-config-keys`. Pass `--check-config false` to restore the historical top-level-only behavior. Not applicable to `catalog-allowed-keys` or `dbt-project-allowed-keys`.
- **`--fix-legacy-yaml`** — (`true` / `false`, default `false`) — **only** on the six property-YAML `*-allowed-keys` hooks: **`model-`**, **`macro-`**, **`seed-`**, **`source-`**, **`snapshot-`**, **`exposure-allowed-keys`**. When `true`, runs mechanical rewrites in place (ruamel round-trip) **before** validation, for the whole file: **`tests` → `data_tests`**, and top-level **`meta` / `tags` → `config`** on each resource entry (see [`specs/hook-families/fix-legacy-yaml.md`](specs/hook-families/fix-legacy-yaml.md)). **`catalog-allowed-keys`** and **`dbt-project-allowed-keys`** do **not** define this option. See [`specs/hook-families/allowed-keys.md`](specs/hook-families/allowed-keys.md).

> **Heads-up — duplicate violations:** if you run both a `*-allowed-keys` hook (with the default `--check-config true`) **and** the matching `*-allowed-config-keys` hook on the same files, an unknown `config:` key will produce **two** stderr lines—one from each hook. To avoid this, either drop the `*-allowed-config-keys` hooks you no longer need, or pass `--check-config false` to the `*-allowed-keys` hooks and keep running `*-allowed-config-keys` separately (useful when you need `--required`/`--forbidden` on `config` keys, which `*-allowed-keys` does not support).

## `*-allowed-column-keys`

Direct keys on each **column entry** (each item in a resource's `columns:` list) in property YAML. The default allowlists are identical to those used by `*-allowed-keys --check-columns`, but this family adds **`--required`** and **`--forbidden`** support for column keys.

| ID | Validates |
| --- | --- |
| `model-allowed-column-keys` | Direct keys on each column entry under `models:` |
| `seed-allowed-column-keys` | Direct keys on each column entry under `seeds:` |
| `snapshot-allowed-column-keys` | Direct keys on each column entry under `snapshots:` |

Allowlists are in [`specs/resource-keys.md`](specs/resource-keys.md) § **Column keys** (`MODEL_COLUMN_ALLOWED_KEYS`, `SEED_COLUMN_ALLOWED_KEYS`, `SNAPSHOT_COLUMN_ALLOWED_KEYS` in `resource_keys.py`). See [`specs/hook-families/allowed-column-keys.md`](specs/hook-families/allowed-column-keys.md).

- **`--required`** — comma-separated column keys that **must** appear on every column entry (e.g. `--required description` to enforce documented columns). Do **not** list `name` (always required; exit code 2 if specified).
- **`--forbidden`** — comma-separated column keys that **must not** appear on any column entry, even when otherwise allowlisted.
- **`--fix-legacy-yaml`** — (`true` / `false`, default `false`) — when `true`, run the same **fix-legacy-yaml** rewrites on the file before column-key validation (see [`specs/hook-families/allowed-column-keys.md`](specs/hook-families/allowed-column-keys.md) and [`specs/hook-families/fix-legacy-yaml.md`](specs/hook-families/fix-legacy-yaml.md)).

If a resource entry has no `columns:` key, or `columns:` is an empty list, it is skipped silently — `--required` does not trigger violations for entries without a `columns:` block.

> **Heads-up — duplicate violations:** `*-allowed-keys` validates column keys by default (`--check-columns true`). Running both families on the same files will emit **two** stderr lines for the same disallowed column key. If you adopt `*-allowed-column-keys` for fine-grained control (e.g. `--required description`), consider passing `--check-columns false` to the corresponding `*-allowed-keys` hooks to suppress the duplicate output.

## `*-allowed-config-keys`

Top-level keys under each entry’s **`config:`** mapping in property YAML.

| ID | Validates |
| --- | --- |
| `model-allowed-config-keys` | Keys under `config` on each `models:` entry |
| `macro-allowed-config-keys` | Keys under `config` on each `macros:` entry |
| `seed-allowed-config-keys` | Keys under `config` on each `seeds:` entry |
| `source-allowed-config-keys` | Keys under `config` on each `sources:` entry |
| `snapshot-allowed-config-keys` | Keys under `config` on each `snapshots:` entry |
| `exposure-allowed-config-keys` | Keys under `config` on each `exposures:` entry |

Allowlists are in [`specs/resource-config-keys.md`](specs/resource-config-keys.md) (implementation: `*_CONFIG_ALLOWED_KEYS` in `resource_config_keys.py`). CLI mirrors **`*-allowed-keys`**: **`--required`**, **`--forbidden`**. See [`specs/hook-families/allowed-config-keys.md`](specs/hook-families/allowed-config-keys.md).

## `*-allowed-meta-keys`

Keys under **`config.meta`** on each resource entry (see [`specs/hook-families/allowed-meta-keys.md`](specs/hook-families/allowed-meta-keys.md)).

| ID | Validates |
| --- | --- |
| `model-allowed-meta-keys` | Keys under `config.meta` on each `models:` entry |
| `seed-allowed-meta-keys` | Keys under `config.meta` on each `seeds:` entry |
| `snapshot-allowed-meta-keys` | Keys under `config.meta` on each `snapshots:` entry |
| `exposure-allowed-meta-keys` | Keys under `config.meta` on each `exposures:` entry |
| `source-allowed-meta-keys` | Keys under `config.meta` on each `sources:` entry |
| `macro-allowed-meta-keys` | Keys under `config.meta` on each `macros:` entry |

There is **no** built-in allowlist in **`resource-keys.md`** or **`resource-config-keys.md`** for **`meta`** key names—your policy is entirely from CLI flags (comma-separated keys, same parsing as the **`*-allowed-keys`** family). All flags apply to **keys on `config.meta`** for each resource entry.

- **`--required`** — Keys that **must** be present on **`meta`**. If `config` or `meta` is missing, **`meta`** is treated as empty, so required keys are reported missing.
- **`--forbidden`** — Keys that **must not** appear on **`meta`**. Still enforced when **`--allowed`** is set (**forbidden** wins over the allowlist).
- **`--allowed`** (optional) — If **omitted**, only **`--required`** and **`--forbidden`** apply; any other key on **`meta`** is **not** reported (no unknown-key rule). If **present**, allowlist mode: a key that appears on **`meta`** must be in **effective allow** = **`--allowed`** ∪ **`--required`** (you do not need to repeat required keys in **`--allowed`**). Keys not in effective allow are violations.

If **`--allowed`**, **`--required`**, and **`--forbidden`** are all empty/absent, the hook does nothing (exit **`0`**).

Full detail: [`specs/hook-families/allowed-meta-keys.md`](specs/hook-families/allowed-meta-keys.md).

Pass hook flags as `args` in your pre-commit config (see below).

## `*-meta-accepted-values`

The value at a **dot path** under **`config.meta`** must be a **string** or **list of strings**; each string must be one of the values in **`--values`** (see [`specs/hook-families/meta-accepted-values.md`](specs/hook-families/meta-accepted-values.md)).

| ID | Validates |
| --- | --- |
| `model-meta-accepted-values` | One path on each `models:` entry (`--key`, `--values`, optional `--optional`) |
| `seed-meta-accepted-values` | One path on each `seeds:` entry |
| `snapshot-meta-accepted-values` | One path on each `snapshots:` entry |
| `exposure-meta-accepted-values` | One path on each `exposures:` entry |
| `source-meta-accepted-values` | One path on each `sources:` entry |
| `macro-meta-accepted-values` | One path on each `macros:` entry |

## `*-tags-accepted-values`

**`config.tags`** on each resource entry must use only strings from **`--values`** (string or list of strings; missing **`config`** or **`tags`** passes). See [`specs/hook-families/tags-accepted-values.md`](specs/hook-families/tags-accepted-values.md).

| ID | Validates |
| --- | --- |
| `model-tags-accepted-values` | `config.tags` on each `models:` entry |
| `seed-tags-accepted-values` | `config.tags` on each `seeds:` entry |
| `snapshot-tags-accepted-values` | `config.tags` on each `snapshots:` entry |
| `exposure-tags-accepted-values` | `config.tags` on each `exposures:` entry |
| `source-tags-accepted-values` | `config.tags` on each `sources:` entry |
| `macro-tags-accepted-values` | `config.tags` on each `macros:` entry |

## pre-commit

The hooks are **not** published to PyPI—point pre-commit at **this Git repository** (see [`.pre-commit-hooks.yaml`](.pre-commit-hooks.yaml)).

pre-commit installs the repo as a Python environment and runs the hook entry points; you do not `pip install` the package yourself for normal use. Release notes: [`CHANGELOG.md`](CHANGELOG.md).

```yaml
repos:
  - repo: https://github.com/scrambldchannel/dbt-yaml-guardrails
    rev: v0.5.1
    hooks:

      # allowed top-level keys (also checks config: child keys by default)
      - id: model-allowed-keys
        args: ["--required", "description", "--forbidden", "version"]
      - id: macro-allowed-keys
      - id: seed-allowed-keys
      - id: source-allowed-keys
      - id: snapshot-allowed-keys
      - id: exposure-allowed-keys
      - id: catalog-allowed-keys
      - id: dbt-project-allowed-keys

      # allowed config keys — only needed if you want --required/--forbidden on config
      # keys, or if you run the *-allowed-keys hooks with --check-config false.
      # Running both with the default --check-config true will emit duplicate violations
      # for the same unknown config: key.
      - id: model-allowed-config-keys
      - id: macro-allowed-config-keys
      - id: seed-allowed-config-keys
      - id: source-allowed-config-keys
      - id: snapshot-allowed-config-keys
      - id: exposure-allowed-config-keys

      # allowed column keys (model / seed / snapshot)
      - id: model-allowed-column-keys
      - id: seed-allowed-column-keys
      - id: snapshot-allowed-column-keys

      # allowed meta keys
      - id: model-allowed-meta-keys
        args: ["--allowed", "owner"]
      - id: seed-allowed-meta-keys
      - id: snapshot-allowed-meta-keys
      - id: exposure-allowed-meta-keys
      - id: source-allowed-meta-keys
      - id: macro-allowed-meta-keys

      # meta accepted values (enum-like string at one dot path)
      - id: model-meta-accepted-values
        args: ["--key", "domain", "--values", "sales,hr,finance"]
      - id: seed-meta-accepted-values
        args: ["--key", "domain", "--values", "sales,hr,finance"]
      - id: snapshot-meta-accepted-values
        args: ["--key", "domain", "--values", "sales,hr,finance"]
      - id: exposure-meta-accepted-values
        args: ["--key", "domain", "--values", "sales,hr,finance"]
      - id: source-meta-accepted-values
        args: ["--key", "domain", "--values", "sales,hr,finance"]
      - id: macro-meta-accepted-values
        args: ["--key", "domain", "--values", "sales,hr,finance"]

      # config.tags allowlist (when tags are declared in YAML)
      - id: model-tags-accepted-values
        args: ["--values", "nightly,finance,raw"]
      - id: seed-tags-accepted-values
        args: ["--values", "nightly,finance,raw"]
      - id: snapshot-tags-accepted-values
        args: ["--values", "nightly,finance,raw"]
      - id: exposure-tags-accepted-values
        args: ["--values", "nightly,finance,raw"]
      - id: source-tags-accepted-values
        args: ["--values", "nightly,finance,raw"]
      - id: macro-tags-accepted-values
        args: ["--values", "nightly,finance,raw"]

      # optional: e.g. model-allowed-keys with --fix-legacy-yaml true rewrites legacy keys then validates
      # - id: model-allowed-keys
      #   args: ["--fix-legacy-yaml", "true", "--required", "description"]
```

The **`rev:`** above tracks the **latest release**; bump it when you release (see **`specs/project-spec.md`** § **Release notes**). For reproducible installs you can also pin a [specific tag](https://github.com/scrambldchannel/dbt-yaml-guardrails/tags) or commit SHA. Use **`main`** only if you intentionally want the tip of the default branch.
