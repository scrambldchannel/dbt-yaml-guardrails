SANDBOX_FILE  = tests/hook_sandbox/sandbox.yml
SANDBOX_CFG   = tests/hook_sandbox/.pre-commit-sandbox.yaml

.PHONY: test sandbox-hooks vulture-src vulture-tests

test:
	uv run pytest

sandbox-hooks:
	pre-commit run --config $(SANDBOX_CFG) --files $(SANDBOX_FILE)

vulture-src:
	uv run vulture src

vulture-tests:
	uv run vulture tests
