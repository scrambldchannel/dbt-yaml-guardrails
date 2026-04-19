# Contributing

**Be kind** — assume good intent, keep feedback specific and respectful.

## Spec-driven development

Behavior lives in **`specs/`**. Start from **[`specs/README.md`](specs/README.md)** (reading order) and **[`specs/project-spec.md`](specs/project-spec.md)** (constitution). Change or extend specs **before** or **with** code so reviews stay grounded in written intent.

## Dev environment & tests

Requires **Python 3.10+** and **[uv](https://docs.astral.sh/uv/)**.

```bash
uv sync --extra dev
uv run pytest
```

Details: **[`specs/testing-strategy.md`](specs/testing-strategy.md)**.
