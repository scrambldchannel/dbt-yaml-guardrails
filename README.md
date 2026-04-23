# dbt-yaml-guardrails

A lightweight set of pre-commit hooks that enforce standards on dbt property YAML (Fusion-oriented). Behavior is specified under [`specs/`](specs/).

## Motivation

I wanted a simple, dependency light, framework that would simply enforce user configurable standards on dbt properties files without relying on the presence of dbt artifacts.

## Example Usage

Here is a short example of how the hooks might be configured on a project. Read more about [pre-commit](https://pre-commit.com/) for an idea of how to create your own configuration, and see a full hook list in [`HOOKS.md`](HOOKS.md).

```yaml
repos:
  - repo: https://github.com/scrambldchannel/dbt-yaml-guardrails
    rev: v0.4.2
    hooks:
      # Check that model top level keys are valid and make description required
      - id: model-allowed-keys
        files: ^models/
        args: ["--required", "description"]

      # Check that model config keys are valid and forbid the use of schema and database
      - id: model-allowed-config-keys
        files: ^models/
        args: ["--forbidden", "schema,database"]

      # Check that if a model has a domain key defined under meta, it must be in a defined list
      - id: model-meta-accepted-values
        files: ^models/
        name: Accepted Domains
        alias: accepted-domains
        args: ["--key", "domain", "--values", "sales,hr,finance,all", "--optional"]

      # Check that a model has a required owner key under meta which matches a defined list
      - id: model-meta-accepted-values
        files: ^models/
        name: Accepted Owners
        alias: accepted-owners
        args: ["--key", "owner", "--values", "alex,annemarie,ryu,ken"]
```


## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) (spec-driven workflow, dev setup, tests). Issues and change discussion: [GitHub Issues](https://github.com/scrambldchannel/dbt-yaml-guardrails/issues).

## License

This project is licensed under the [MIT License](LICENSE).
