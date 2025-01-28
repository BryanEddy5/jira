
run:
	poetry run typer ./src/cli/entry.py

app-lint:
	poetry run ruff format && poetry run ruff check --unsafe-fixes --fix

init:
	poetry install