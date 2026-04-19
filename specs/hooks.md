# Hooks

All hooks should follow the conventions as laid out for hooks defined for pre-commit - https://pre-commit.com/#creating-new-hooks

## 1. model-allowed-keys

This hook should check the top-level keys defined for each model in any YAML file it runs on.

Schema YAML nests model definitions under a top-level `models` key; the hook validates only the keys on each model object, not the wrapper key `models`.

The CLI entry point and hook id should be `model-allowed-keys`.

It should take the following optional arguments:

+ `--required` — a comma-separated list of key names that must be present. The default is no keys. **`name`** is always present for real models in dbt; do not list it in `--required`.
+ `--allowed` — a comma-separated list of key names that are allowed. The default is the supported Fusion-oriented set for models in the table below (callers may override by passing `--allowed` explicitly).

+ `--strict` - a boolean indicating whether the allowed keys argument can contain keys not in the supported Fusion-oriented set for models in the table below.

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
