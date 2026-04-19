# Project Scope

See **`README.md`** in this folder for how this fits with the other specs (`project-spec.md`, `yaml-handling.md`, `hooks.md`).

## **In scope**

These items should be considered in scope:

+ Parsing and checking the validity according to user defined rules for all dbt resource types that exist as of dbt core 1.10
+ Exposing a stable CLI entrypoint for pre-commit hooks

## **Out of scope**

These items should be considered out of scope:

+ SQL linting
+ dbt_project.yml policy
+ Running dbt commands, or parsing any dbt artifacts (e.g. manifest.json, catalog.json)

## **Fusion first**

This project is intended to focus on future proofing dbt projects against stricter model properties requirements as dbt core development moves toward compatibility with the new dbt Fusion engine. This means stricter enforcement of yaml standards such as which keys are allowed to appear in certain places. Models are the most important resource type.
