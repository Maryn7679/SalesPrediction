setup:
	uv sync
	uv tool install ruff
lint:
	uv run ruff check .