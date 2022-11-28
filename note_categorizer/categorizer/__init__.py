"""Init for the categorizer aspect of the project"""
import note_categorizer.categorizer.parser

# pylint: disable=redefined-builtin
all = [
    # This is the only officially 'exported' class of the library.
    # Others should NOT get used outside of the categorizer project.
    "parser",
]
