"""Top level init for the project. All components get referenced here and used
by main."""
from note_categorizer.categorizer import parser
from note_categorizer.web_app import server

# pylint: disable=redefined-builtin
all = ["parser", "server"]
