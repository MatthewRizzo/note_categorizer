# note_categorizer

A python-based Web App to group notes together based on expressions and or
categories. Useful for grouping livesteam notes into categories (i.e. for
lawyers when making timesheets).

## Developing the Project

This project maintains a strict typing and linting checker. To get up to
standard, please run `poetry install` within the top level directory of the
project. This will handle any setup and installation required.

Next, please run
`poetry run pre-commit install --hook-type pre-commit --hook-type pre-push`.
This is required to setup the pre-commit and push hooks to run before either
action is taken by git. This enforces all checkers BEFORE non-complient code is
pushed to remote.

**Note**: you do not need to be within a poetry shell for the hooks to get used
once they are installed.

For more context, please see [mattrizzo_devops](https://github.com/MatthewRizzo/mattrizzo_devops).

## Todo

* Initialize Web App Front end
* Add front end ability to define categories (name + keywords) in a nice way
* Add front end ability to past a list of notes -> sent to parser
