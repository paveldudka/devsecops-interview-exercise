.PHONY: verify-env baseline test lint typecheck format run

verify-env:
	@command -v uv >/dev/null || { echo "uv is required"; exit 1; }
	uv sync --locked --all-groups
	@uv run --frozen python -c 'import sys; assert (3, 12) <= sys.version_info[:2] < (3, 14), "Python 3.12 or 3.13 is required"'
	@uv run --frozen python -c 'import fastapi, httpx; print("environment ready")'

baseline: lint typecheck test

test:
	uv run --frozen pytest

lint:
	uv run --frozen ruff format --check .
	uv run --frozen ruff check .

typecheck:
	uv run --frozen mypy

format:
	uv run --frozen ruff format .
	uv run --frozen ruff check --fix .

run:
	uv run --frozen uvicorn content_fetcher.api:app --reload
