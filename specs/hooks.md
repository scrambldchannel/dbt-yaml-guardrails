# Hooks

All hooks should follow the conventions for hooks defined for [pre-commit](https://pre-commit.com/#creating-new-hooks).

Shared behavior (parser, document shape, when to skip a file, stderr/exit codes, message ordering) is defined in **`yaml-handling.md`**. This file defines **per-hook** CLIs, arguments, and defaults.

## 1. model-allowed-keys

Validates the **top-level keys on each model entry** (each dict under the `models:` list). Document-level rules and multi-resource files are described in **`yaml-handling.md`** (see **§ dbt shape** and **§ Parsing**).

The CLI entry point and hook id should be `model-allowed-keys`.

**Arguments:**

+ `--required` — a comma-separated list of key names that must be present. The default is no keys. **`name`** is always present for real models in dbt; do not list it in `--required`.
+ `--allowed` — a comma-separated list of key names that are allowed. The default is the supported Fusion-oriented set for models in the table below (callers may override by passing `--allowed` explicitly).
+ `--strict` — if set, `--allowed` may not include keys outside the default Fusion-oriented set in the table below.

Default **`allowed`** keys for models:

| Key | Notes |
| --- | --- |
| `name` | Always present for real models in dbt; do not list in `--required`. |
| `description` | |
| `columns` | |
| `data_tests` | As in Fusion / modern schema YAML naming. |
| `versions` | YAML-oriented; manifest may use `version`. |
| `latest_version` | |
| `version` | On manifest nodes. |
| `constraints` | |
| `docs` | |
| `config` | |
