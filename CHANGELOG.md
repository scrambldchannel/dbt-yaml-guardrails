# Changelog

All notable changes to this project are documented here. Versions match **git tags** (and **`version`** in **`pyproject.toml`**). This project is distributed as a **pre-commit** Git repository, not via PyPI.

## [0.1.0] — 2026-04-19

### Added

- **`*-allowed-keys`** hooks for **`models`**, **`macros`**, **`seeds`**, **`snapshots`**, and **`exposures`**: validate top-level keys on each resource entry against Fusion-oriented allowlists in **`specs/resource-keys.md`** (with **`--required`** / **`--forbidden`**).
- **`*-allowed-meta-keys`** hooks for **`models`**, **`seeds`**, **`snapshots`**, **`exposures`**, and **`macros`**: validate keys under **`config.meta`** with optional **`--allowed`**, plus **`--required`** / **`--forbidden`**.
- Shared YAML loading and parsing (**`yaml_handling`**) per **`specs/yaml-handling.md`**.
- MIT license; **`pyproject.toml`** metadata (authors, URLs, keywords, classifiers) for tooling and documentation.

[0.1.0]: https://github.com/scrambldchannel/dbt-yaml-guardrails/releases
