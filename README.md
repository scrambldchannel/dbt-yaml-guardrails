# dbt-yaml-guardrails

Pre-commit hooks that enforce allowed keys on dbt property YAML (Fusion-oriented). Further detail: `specs/`.

## Motivation

These hooks **do not run dbt**—they only parse YAML and check key names. That keeps them **fast** and **easy to wire into pre-commit** while still matching dbt property-file shapes. Use them to keep schema/metadata files consistent without paying for a full `dbt parse` in CI on every commit.

## Hooks


| ID                         | Validates                                                                 |
| -------------------------- | ------------------------------------------------------------------------- |
| `model-allowed-keys`       | Top-level keys on each `models:` entry                                    |
| `macro-allowed-keys`       | Top-level keys on each `macros:` entry                                    |
| `seed-allowed-keys`        | Top-level keys on each `seeds:` entry                                     |
| `snapshot-allowed-keys`    | Top-level keys on each `snapshots:` entry                                 |
| `exposure-allowed-keys`      | Top-level keys on each `exposures:` entry                                 |
| `model-allowed-meta-keys`    | Keys under `config.meta` on each `models:` entry ([`allowed-meta-keys`](specs/hook-families/allowed-meta-keys.md)) |
| `seed-allowed-meta-keys`     | Keys under `config.meta` on each `seeds:` entry                                   |
| `snapshot-allowed-meta-keys` | Keys under `config.meta` on each `snapshots:` entry                             |
| `exposure-allowed-meta-keys` | Keys under `config.meta` on each `exposures:` entry                             |
| `macro-allowed-meta-keys`    | Keys under `config.meta` on each `macros:` entry                                |

The **`*-allowed-meta-keys`** hooks have **no** fixed allowlist in-repo: use optional **`--allowed`**, plus **`--required`** / **`--forbidden`**, as documented in [`specs/hook-families/allowed-meta-keys.md`](specs/hook-families/allowed-meta-keys.md).

The **`*-allowed-keys`** hooks use a **fixed allowlist** from [`specs/resource-keys.md`](specs/resource-keys.md) for that resource type. On top of that:

- **--required** — comma-separated keys that **must** appear on every entry (e.g. enforce `description` everywhere). Do not list `name`; it is implied for real resources and the hook rejects `name` in `--required` with exit code 2.
- **--forbidden** — comma-separated keys that **must not** appear on an entry, even when they would otherwise be allowed—use this for stricter team rules (e.g. forbid `config` on models so configuration lives only in `dbt_project.yml`).

Pass these as `args` in your pre-commit config (see below).

## pre-commit

pre-commit installs this repo as a Python environment and runs the hook entry points; you do not install the package separately.

```yaml
repos:
  - repo: https://github.com/OWNER/dbt-yaml-guardrails
    rev: main
    hooks:
      - id: model-allowed-keys
        args: ["--required", "description", "--forbidden", "version"]
      - id: macro-allowed-keys
      - id: seed-allowed-keys
      - id: snapshot-allowed-keys
      - id: exposure-allowed-keys
      - id: model-allowed-meta-keys
        args: ["--allowed", "owner"]
      - id: seed-allowed-meta-keys
      - id: snapshot-allowed-meta-keys
      - id: exposure-allowed-meta-keys
      - id: macro-allowed-meta-keys
```

Replace `OWNER` / `rev` with your fork and a tag or SHA as needed.

## License

This project is licensed under the [MIT License](LICENSE).
