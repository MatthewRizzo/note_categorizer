# note_categorizer

A python-based Web App to group notes together based on expressions and or
categories. Useful for grouping livesteam notes into categories (i.e. for
lawyers when making timesheets).

## Running the Program

### Running Via Command Line

This program is easy to run via command line using poetry! Just run

```bash
poetry run categorizer_cli <your flags>
```

The most important flags to use are `--category_path` and `--notes_path` to
provide the program the location of your files. Otherwise, the program
defaults to looking for files at the top directory of the project.

#### Example Input Files

Please see [example_category_file.txt](example_category_file.txt) and
[example_notes.txt](example_notes.txt) for examples of creating input files
to program. Note this does NOT apply when using the program via Web App

## Developing the Project

This project maintains a strict typing and linting checker. To get up to
standard, please run `poetry install --with dev` within the top level directory
of the project. This will handle any setup and installation required.

Next, please run
`poetry run pre-commit install --hook-type pre-commit --hook-type pre-push`.
This is required to setup the pre-commit and push hooks to run before either
action is taken by git. This enforces all checkers BEFORE non-complient code is
pushed to remote.

**Note**: you do not need to be within a poetry shell for the hooks to get used
once they are installed.

For more context, please see [mattrizzo_devops](https://github.com/MatthewRizzo/mattrizzo_devops).

### Install

Install is made super easy using poetry and the [Makefile](./Makefile).
Simply run

```bash
make dev-install
```

and the entire project will be setup for you to both run and develop!

### Testing

Though no formal CI is currently setup within GitHub, please do not push code
that fails the pytest configuration as defined by
[`pyproject.toml`](pyproject.toml).

Additionally, the command `make all_test` using the [Makefile](./Makefile) will
run through all tests (static and unit testing) for you!

## Todo

* Add front end ability to edit a note's category
