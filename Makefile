
run:
	poetry run typer ./src/cli/entry.py

app-lint:
	poetry run ruff check --unsafe-fixes --fix && poetry run ruff format

init:
	poetry install