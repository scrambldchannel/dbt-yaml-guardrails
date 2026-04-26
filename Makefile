SANDBOX_FILE  = tests/hook_sandbox/sandbox.yml
SANDBOX_CFG   = tests/hook_sandbox/.pre-commit-sandbox.yaml

.PHONY: test sandbox-hooks vulture coverage
test:
	uv run pytest

sandbox-hooks:
	pre-commit run --config $(SANDBOX_CFG) --files $(SANDBOX_FILE)

# Release-time: measures line coverage of `dbt_yaml_guardrails`; uses `[tool.coverage.*]` in `pyproject.toml`.
coverage:
	uv run pytest --cov=dbt_yaml_guardrails --cov-config=pyproject.toml --cov-report=term-missing --cov-report=html:htmlcov

vulture:
	uv run vulture --config pyproject.toml
