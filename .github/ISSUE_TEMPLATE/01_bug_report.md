---
name: Bug report
about: Something is wrong with a hook, CLI, or docs—help us reproduce it.
labels: ["bug"]
---

## Summary

What went wrong? (One or two sentences.)

## Hook / area (if applicable)

- Hook id (e.g. `model-allowed-keys`) or command, or “docs” / “specs” / “CI”:

## Version

- **`rev:`** in `.pre-commit-config.yaml` (or commit SHA / tag), or **`pyproject.toml`** `version` if you run the package locally:

## What you expected

## What happened instead

Include stderr / a short quote of the violation message if relevant.

## Minimal repro

- Small YAML snippet **or** path pattern (e.g. `models/**/*.yml`) that triggers the issue.
- If you can, note whether it involves **`config.meta`**, **`models:`**, etc.

## Extra context

Anything else (dbt / Fusion version, OS)—optional.
