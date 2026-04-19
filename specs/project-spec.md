# Project Constitution: dbt-yaml-guardrails

## 1. Goal

Build a set of pre-commit hooks that apply configurable standards to dbt yaml that define properties for dbt resource types (e.g. models, macros, sources etc) with a focus on a dbt Fusion mindset.

## 2. Tech Stack & Standards
- **Language:** Python 3.10+
- **Tooling:** uv, pytest, github
- **Libraries** ruamel.yaml, typer
- **Structure** Python source layout

## 3. Rules & Guidelines for Cursor
- Read `README.md`, `specs/project-spec.md`, and **`specs/README.md`** (for spec reading order and links) before starting any task.
- Use atomic commits via `git` after each functional component completion.

## 4. Workflow
1. Stop and allow human review before proceeding to the next task.
