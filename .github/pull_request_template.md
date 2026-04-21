## Summary

What does this PR do? Link an issue: closes #

## Specs & docs

This project is **spec-driven** (see [`CONTRIBUTING.md`](CONTRIBUTING.md)): behavior belongs under [`specs/`](specs/).

- [ ] **Specs** (`specs/`, including `specs/hook-families/` when behavior changes) updated **with** or **before** code, as applicable
- [ ] **[`HOOKS.md`](HOOKS.md)** updated if hooks, families, flags, or the example `rev:` / inventory changed
- [ ] Root **[`README.md`](README.md)** updated only if the user-facing entry / examples need to change

## Tests

See [`specs/testing-strategy.md`](specs/testing-strategy.md).

- [ ] `uv run pytest` passes
- [ ] New or changed behavior covered by tests / fixtures where it makes sense

## Release notes

- [ ] **[`CHANGELOG.md`](CHANGELOG.md)** updated if this is user-facing (hook behavior, new hooks, breaking CLI changes). Version / tag bumps are often a separate maintainer step—ask in the PR if unsure.
