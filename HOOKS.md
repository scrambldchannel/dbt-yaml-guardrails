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

## `*-allowed-config-keys`

Top-level keys under each entry’s **`config:`** mapping in property YAML.

| ID | Validates |
| --- | --- |
| `model-allowed-config-keys` | Keys under `config` on each `models:` entry |
| `macro-allowed-config-keys` | Keys under `config` on each `macros:` entry |
| `seed-allowed-config-keys` | Keys under `config` on each `seeds:` entry |
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
| `macro-meta-accepted-values` | One path on each `macros:` entry |

## `*-tags-accepted-values`

**`config.tags`** on each resource entry must use only strings from **`--values`** (string or list of strings; missing **`config`** or **`tags`** passes). See [`specs/hook-families/tags-accepted-values.md`](specs/hook-families/tags-accepted-values.md).

| ID | Validates |
| --- | --- |
| `model-tags-accepted-values` | `config.tags` on each `models:` entry |
| `seed-tags-accepted-values` | `config.tags` on each `seeds:` entry |
| `snapshot-tags-accepted-values` | `config.tags` on each `snapshots:` entry |
| `exposure-tags-accepted-values` | `config.tags` on each `exposures:` entry |
| `macro-tags-accepted-values` | `config.tags` on each `macros:` entry |

## pre-commit

The hooks are **not** published to PyPI—point pre-commit at **this Git repository** (see [`.pre-commit-hooks.yaml`](.pre-commit-hooks.yaml)).

pre-commit installs the repo as a Python environment and runs the hook entry points; you do not `pip install` the package yourself for normal use. Release notes: [`CHANGELOG.md`](CHANGELOG.md).

```yaml
repos:
  - repo: https://github.com/scrambldchannel/dbt-yaml-guardrails
    rev: v0.4.0
    hooks:

      # allowed top level keys
      - id: model-allowed-keys
        args: ["--required", "description", "--forbidden", "version"]
      - id: macro-allowed-keys
      - id: seed-allowed-keys
      - id: snapshot-allowed-keys
      - id: exposure-allowed-keys

      # allowed config keys (under config:)
      - id: model-allowed-config-keys
      - id: macro-allowed-config-keys
      - id: seed-allowed-config-keys
      - id: snapshot-allowed-config-keys
      - id: exposure-allowed-config-keys

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
      - id: macro-tags-accepted-values
        args: ["--values", "nightly,finance,raw"]
```

The **`rev:`** above tracks the **latest release**; bump it when you release (see **`specs/project-spec.md`** § **Release notes**). For reproducible installs you can also pin a [specific tag](https://github.com/scrambldchannel/dbt-yaml-guardrails/tags) or commit SHA. Use **`main`** only if you intentionally want the tip of the default branch.
