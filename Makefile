# Makefile for all actions to run in the system

package=note_categorizer

dev-install:
	curl -sSL https://install.python-poetry.org | python3.10 - --version 1.2.2
	poetry install

test:
	poetry run pytest --cov --cov-report html --cov-report term-missing --cov-fail-under 80

type:
	poetry run mypy -p ${package}

linter:
	poetry run pylint ${package}

format:
	poetry run black ${package}

all_test: test type linter

build:
	poetry build

# Run the terminal and add up times
# Defaults to using "category_file.txt" and "note_file.txt" unless other flags
# added
run_terminal:
	poetry run categorizer_cli --add_times

run_web:
	poetry run categorizer_web_app

debug_web:
	poetry run python note_categorizer/web_app/main.py --debugModeOn --localhost --verbose
