setup:
	uv sync --group lint
lint:
	uv run ruff check .