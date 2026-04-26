SANDBOX_FILE  = tests/hook_sandbox/sandbox.yml
SANDBOX_CFG   = tests/hook_sandbox/.pre-commit-sandbox.yaml

.PHONY: test sandbox-hooks vulture
test:
	uv run pytest

sandbox-hooks:
	pre-commit run --config $(SANDBOX_CFG) --files $(SANDBOX_FILE)

vulture:
	uv run vulture --config pyproject.toml
