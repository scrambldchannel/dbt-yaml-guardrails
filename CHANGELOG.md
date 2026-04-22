# Changelog

All notable changes to this project are documented here. Versions match **git tags** (and `**version`** in `**pyproject.toml**`). This project is distributed as a **pre-commit** Git repository, not via PyPI.

## [0.4.0](https://github.com/scrambldchannel/dbt-yaml-guardrails/releases) — 2026-04-22

### Changed

- **Release metadata:** `**pyproject.toml**` `**version**` is **0.4.0**; pre-commit `**rev:**` examples in **`README.md`**, **`HOOKS.md`**, and **`specs/hook-families/meta-accepted-values.md`** use **`v0.4.0`**. No CLI or spec behavior change beyond the version pin—tag **v0.4.0** for consumers who track releases by git ref.

## [0.3.0](https://github.com/scrambldchannel/dbt-yaml-guardrails/releases) — 2026-04-21

### Added

- `**macro-meta-accepted-values**`: same behavior as the other `***-meta-accepted-values**` CLIs, for entries under `**macros:**` (`**--key**`, `**--values**`, optional `**--optional**`). Implementation: `**src/dbt_yaml_guardrails/hook_families/meta_accepted_values/macro_meta_accepted_values.py**`; `**[project.scripts]**`, `**.pre-commit-hooks.yaml**`, and docs/specs updated. Tests: `**tests/hook_families/meta_accepted_values/test_macro_meta_accepted_values.py**` and `**tests/fixtures/yaml/meta_accepted_values/macros/**`.
- `***-tags-accepted-values`** hooks (`**model**`, `**seed**`, `**snapshot**`, `**exposure**`, `**macro**`): validate `**config.tags**` (string or list of strings) against `**--values**` when `**tags**` is declared; missing `**config**` or `**tags**` passes (see `**specs/hook-families/tags-accepted-values.md**`). Implementation: `**src/dbt_yaml_guardrails/hook_families/tags_accepted_values/**`; `**[project.scripts]**`, `**.pre-commit-hooks.yaml**`, `**HOOKS.md**` example block, and `**specs/**` index updated.

### Changed

- **Tests**: `**tests/hook_families/tags_accepted_values/`** and `**tests/fixtures/yaml/tags_accepted_values/**` cover the tags family; `**tests/hook_families/meta_accepted_values/**` includes `**macro**` where applicable.

## [0.2.1](https://github.com/scrambldchannel/dbt-yaml-guardrails/releases) — 2026-04-21

### Changed

- `***-meta-accepted-values**`: the value at `**--key**` may be a **YAML list of strings** (flow or block list); **each** element must appear in `**--values`** after trim. Single-string leaves unchanged.
- **Spec**: `**specs/hook-families/meta-accepted-values.md`** — `**--values**` applies to **leaf** paths only (extend `**--key`** to reach a string field, e.g. `**owner.name**`); docs and hook descriptions updated accordingly.

## [0.2.0](https://github.com/scrambldchannel/dbt-yaml-guardrails/releases) — 2026-04-20

### Added

- `***-allowed-config-keys**` hooks (`**model**`, `**macro**`, `**seed**`, `**snapshot**`, `**exposure**`): validate **top-level keys under each entry’s `config:`** mapping against Fusion-oriented allowlists in `**specs/resource-config-keys.md**`, with `**--required**` / `**--forbidden**` (see `**specs/hook-families/allowed-config-keys.md**`). Implementation: `**src/dbt_yaml_guardrails/hook_families/allowed_config_keys/**` and `**resource_config_keys.py**`.
- **Specs & docs**: `**specs/resource-config-keys.md`** (config-key allowlists; split from top-level `**resource-keys.md**`), plus updates to `**HOOKS.md**`, `**specs/hooks.md**`, `**specs/README.md**`, and related hook-family specs so `**rev:**` and shipped hooks stay aligned.

### Changed

- **Tests**: `**tests/hook_families/allowed_config_keys/`** and `**tests/fixtures/yaml/allowed_config_keys/**` cover the new CLIs.

## [0.1.2](https://github.com/scrambldchannel/dbt-yaml-guardrails/releases) — 2026-04-19

### Added

- `***-meta-accepted-values**` hooks (`**model**`, `**seed**`, `**snapshot**`, `**exposure**`): validate a **string** leaf at a **dot path** under `**config.meta`** against a comma-separated `**--values**` allowlist, with optional `**--optional**` when the path may be absent (see `**specs/hook-families/meta-accepted-values.md**`).

### Changed

- **Packaging & docs**: `**[project.scripts]`** and `**.pre-commit-hooks.yaml**` entries for the new hooks; root `**README**`, `**specs/hooks.md**`, `**specs/README.md**`, and `**meta-accepted-values.md**` updated so the hook family and pre-commit `**rev:**` examples stay aligned.
- **Tests**: `**tests/hook_families/meta_accepted_values/`** and `**tests/fixtures/yaml/meta_accepted_values/**` cover the new CLIs (mirrors the `**models/**` scenarios for `**seeds/**`, `**snapshots/**`, `**exposures/**`).

## [0.1.1](https://github.com/scrambldchannel/dbt-yaml-guardrails/releases) — 2026-04-19

**First public release.** Use `**v0.1.1`** (or this commit) as the first tag intended for general pre-commit `**rev:**` pins.

**0.1.0** was a **pre-release** (internal / early tagging only); there is no separate feature delta from 0.1.0—the shipped behavior is described under the 0.1.0 section below.

## [0.1.0](https://github.com/scrambldchannel/dbt-yaml-guardrails/releases) — 2026-04-19 (pre-release)

> Not promoted as a public release; superseded by **0.1.1** for `**rev:`** pinning.

### Added

- `***-allowed-keys**` hooks for `**models**`, `**macros**`, `**seeds**`, `**snapshots**`, and `**exposures**`: validate top-level keys on each resource entry against Fusion-oriented allowlists in `**specs/resource-keys.md**` (with `**--required**` / `**--forbidden**`).
- `***-allowed-meta-keys**` hooks for `**models**`, `**seeds**`, `**snapshots**`, `**exposures**`, and `**macros**`: validate keys under `**config.meta**` with optional `**--allowed**`, plus `**--required**` / `**--forbidden**`.
- Shared YAML loading and parsing (`**yaml_handling**`) per `**specs/yaml-handling.md**`.
- MIT license; `**pyproject.toml**` metadata (authors, URLs, keywords, classifiers) for tooling and documentation.
