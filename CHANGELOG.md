# Changelog

All notable changes to this project are documented here. Versions match **git tags** (and **`version`** in **`pyproject.toml`**). This project is distributed as a **pre-commit** Git repository, not via PyPI.

## [0.1.2] — 2026-04-19

### Added

- **`*-meta-accepted-values`** hooks (**`model`**, **`seed`**, **`snapshot`**, **`exposure`**): validate a **string** leaf at a **dot path** under **`config.meta`** against a comma-separated **`--values`** allowlist, with optional **`--optional`** when the path may be absent (see **`specs/hook-families/meta-accepted-values.md`**).

### Changed

- **Packaging & docs**: **`[project.scripts]`** and **`.pre-commit-hooks.yaml`** entries for the new hooks; root **`README`**, **`specs/hooks.md`**, **`specs/README.md`**, and **`meta-accepted-values.md`** updated so the hook family and pre-commit **`rev:`** examples stay aligned.
- **Tests**: **`tests/hook_families/meta_accepted_values/`** and **`tests/fixtures/yaml/meta_accepted_values/`** cover the new CLIs (mirrors the **`models/`** scenarios for **`seeds/`**, **`snapshots/`**, **`exposures/`**).

## [0.1.1] — 2026-04-19

**First public release.** Use **`v0.1.1`** (or this commit) as the first tag intended for general pre-commit **`rev:`** pins.

**0.1.0** was a **pre-release** (internal / early tagging only); there is no separate feature delta from 0.1.0—the shipped behavior is described under the 0.1.0 section below.

## [0.1.0] — 2026-04-19 (pre-release)

> Not promoted as a public release; superseded by **0.1.1** for **`rev:`** pinning.

### Added

- **`*-allowed-keys`** hooks for **`models`**, **`macros`**, **`seeds`**, **`snapshots`**, and **`exposures`**: validate top-level keys on each resource entry against Fusion-oriented allowlists in **`specs/resource-keys.md`** (with **`--required`** / **`--forbidden`**).
- **`*-allowed-meta-keys`** hooks for **`models`**, **`seeds`**, **`snapshots`**, **`exposures`**, and **`macros`**: validate keys under **`config.meta`** with optional **`--allowed`**, plus **`--required`** / **`--forbidden`**.
- Shared YAML loading and parsing (**`yaml_handling`**) per **`specs/yaml-handling.md`**.
- MIT license; **`pyproject.toml`** metadata (authors, URLs, keywords, classifiers) for tooling and documentation.

[0.1.2]: https://github.com/scrambldchannel/dbt-yaml-guardrails/releases
[0.1.1]: https://github.com/scrambldchannel/dbt-yaml-guardrails/releases
[0.1.0]: https://github.com/scrambldchannel/dbt-yaml-guardrails/releases
