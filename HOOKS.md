# Hooks

Shipped pre-commit hooks for this repository. Families match [`specs/hooks.md`](specs/hooks.md); per-family behavior and exit codes live under [`specs/hook-families/`](specs/hook-families/).

Hooks are grouped by **family**. Each family has its own CLI shape.

## `*-allowed-keys`

Top-level keys on each resource entry in property YAML.

| ID | Validates |
| --- | --- |
| `model-allowed-keys` | Top-level keys on each `models:` entry |
| `macro-allowed-keys` | Top-level keys on each `macros:` entry |
| `seed-allowed-keys` | Top-level keys on each `seeds:` entry |
| `snapshot-allowed-keys` | Top-level keys on each `snapshots:` entry |
| `exposure-allowed-keys` | Top-level keys on each `exposures:` entry |

These hooks use a **fixed allowlist** from [`specs/resource-keys.md`](specs/resource-keys.md) for that resource type. On top of that:

- **`--required`** — comma-separated keys that **must** appear on every entry (e.g. enforce `description` everywhere). Do not list `name`; it is implied for real resources and the hook rejects `name` in `--required` with exit code 2.
- **`--forbidden`** — comma-separated keys that **must not** appear on an entry, even when they would otherwise be allowed—use this for stricter team rules (e.g. forbid `config` on models so configuration lives only in `dbt_project.yml`).

## `*-allowed-config-keys` (specified, not shipped)

Default keys under each entry’s **`config:`** mapping are specified in [`specs/resource-config-keys.md`](specs/resource-config-keys.md). Behavior and CLI mirror **`*-allowed-keys`**; see [`specs/hook-families/allowed-config-keys.md`](specs/hook-families/allowed-config-keys.md).

## `*-allowed-meta-keys`

Keys under **`config.meta`** on each resource entry (see [`specs/hook-families/allowed-meta-keys.md`](specs/hook-families/allowed-meta-keys.md)).

| ID | Validates |
| --- | --- |
| `model-allowed-meta-keys` | Keys under `config.meta` on each `models:` entry |
| `seed-allowed-meta-keys` | Keys under `config.meta` on each `seeds:` entry |
| `snapshot-allowed-meta-keys` | Keys under `config.meta` on each `snapshots:` entry |
| `exposure-allowed-meta-keys` | Keys under `config.meta` on each `exposures:` entry |
| `macro-allowed-meta-keys` | Keys under `config.meta` on each `macros:` entry |

There is **no** built-in allowlist in **`resource-keys.md`** or **`resource-config-keys.md`** for **`meta`** key names—your policy is entirely from CLI flags (comma-separated keys, same parsing as the **`*-allowed-keys`** family). All flags apply to **keys on `config.meta`** for each resource entry.

- **`--required`** — Keys that **must** be present on **`meta`**. If `config` or `meta` is missing, **`meta`** is treated as empty, so required keys are reported missing.
- **`--forbidden`** — Keys that **must not** appear on **`meta`**. Still enforced when **`--allowed`** is set (**forbidden** wins over the allowlist).
- **`--allowed`** (optional) — If **omitted**, only **`--required`** and **`--forbidden`** apply; any other key on **`meta`** is **not** reported (no unknown-key rule). If **present**, allowlist mode: a key that appears on **`meta`** must be in **effective allow** = **`--allowed`** ∪ **`--required`** (you do not need to repeat required keys in **`--allowed`**). Keys not in effective allow are violations.

If **`--allowed`**, **`--required`**, and **`--forbidden`** are all empty/absent, the hook does nothing (exit **`0`**).

Full detail: [`specs/hook-families/allowed-meta-keys.md`](specs/hook-families/allowed-meta-keys.md).

Pass hook flags as `args` in your pre-commit config (see below).

## `*-meta-accepted-values`

String **leaf** at a **dot path** under **`config.meta`** must be one of the values in **`--values`** (see [`specs/hook-families/meta-accepted-values.md`](specs/hook-families/meta-accepted-values.md)). **v1:** string leaves only.

| ID | Validates |
| --- | --- |
| `model-meta-accepted-values` | One path on each `models:` entry (`--key`, `--values`, optional `--optional`) |
| `seed-meta-accepted-values` | One path on each `seeds:` entry |
| `snapshot-meta-accepted-values` | One path on each `snapshots:` entry |
| `exposure-meta-accepted-values` | One path on each `exposures:` entry |

## pre-commit

The hooks are **not** published to PyPI—point pre-commit at **this Git repository** (see [`.pre-commit-hooks.yaml`](.pre-commit-hooks.yaml)).

pre-commit installs the repo as a Python environment and runs the hook entry points; you do not `pip install` the package yourself for normal use. Release notes: [`CHANGELOG.md`](CHANGELOG.md).

```yaml
repos:
  - repo: https://github.com/scrambldchannel/dbt-yaml-guardrails
    rev: v0.1.2
    hooks:

      # allowed top level keys
      - id: model-allowed-keys
        args: ["--required", "description", "--forbidden", "version"]
      - id: macro-allowed-keys
      - id: seed-allowed-keys
      - id: snapshot-allowed-keys
      - id: exposure-allowed-keys

      # allowed meta keys
      - id: model-allowed-meta-keys
        args: ["--allowed", "owner"]
      - id: seed-allowed-meta-keys
      - id: snapshot-allowed-meta-keys
      - id: exposure-allowed-meta-keys
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
```

The **`rev:`** above tracks the **latest release**; bump it when you release (see **`specs/project-spec.md`** § **Release notes**). For reproducible installs you can also pin a [specific tag](https://github.com/scrambldchannel/dbt-yaml-guardrails/tags) or commit SHA. Use **`main`** only if you intentionally want the tip of the default branch.
