.PHONY: verify-env baseline test lint typecheck

verify-env:
	@command -v uv >/dev/null || { echo "uv is required"; exit 1; }
	@python3 -c 'import sys; assert (3, 12) <= sys.version_info[:2] < (3, 14), "Python 3.12 or 3.13 is required"'
	uv sync --frozen --all-groups
	@uv run python -c 'import fastapi, httpx; print("environment ready")'

baseline: lint typecheck test

test:
	uv run pytest

lint:
	uv run ruff format --check .
	uv run ruff check .

typecheck:
	uv run mypy
