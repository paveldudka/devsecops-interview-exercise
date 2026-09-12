.PHONY: verify-env baseline test lint typecheck run

verify-env:
	@command -v uv >/dev/null || { echo "uv is required"; exit 1; }
	uv sync --frozen --all-groups
	@uv run python -c 'import sys; assert (3, 12) <= sys.version_info[:2] < (3, 14), "Python 3.12 or 3.13 is required"'
	@uv run python -c 'import fastapi, httpx; print("environment ready")'

baseline: lint typecheck test

test:
	uv run pytest

lint:
	uv run ruff format --check .
	uv run ruff check .

typecheck:
	uv run mypy

run:
	uv run uvicorn content_fetcher.api:app --reload
