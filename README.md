# dbt-yaml-guardrails

A lightweight set of pre-commit hooks that enforce standards on dbt property YAML (Fusion-oriented). Behavior is specified under [`specs/`](specs/). Read [`specs/scope.md`](specs/scope.md) for an idea of what it does, and does not, attempt to do.

## Motivation

I wanted a simple, dependency-light framework that would enforce user-configurable standards on dbt property YAML without relying on the presence of dbt artifacts. I was especially interested in enforcing a Fusion-compatible YAML structure for those looking to eventually migrate.

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

## Use in GitHub Actions

Use the same **`.pre-commit-config.yaml`** you use locally. For **pull requests**, you can run hooks only on **files that changed** between the PR base and head with **`--from-ref`** and **`--to-ref`** (install pre-commit, then run from the repository root, where the config file lives).

```yaml
# .github/workflows/pre-commit.yml — example for pull_request; adjust as needed
name: pre-commit
on: pull_request
jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - run: python -m pip install pre-commit
      - run: pre-commit run --show-diff-on-failure --from-ref "${{ github.event.pull_request.base.sha }}" --to-ref "${{ github.event.pull_request.head.sha }}"
```

For **`push`** events (no pull request) you might use `pre-commit run --all-files` or another `--from-ref` / `--to-ref` range. [pre-commit’s CI docs](https://pre-commit.com/#usage-in-continuous-integration) and the [`pre-commit` action](https://github.com/pre-commit/action) cover caching, wrappers, and more.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) (spec-driven workflow, dev setup, tests). Issues and change discussion: [GitHub Issues](https://github.com/scrambldchannel/dbt-yaml-guardrails/issues).

## License

This project is licensed under the [MIT License](LICENSE).
