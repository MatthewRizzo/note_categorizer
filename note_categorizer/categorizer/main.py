"""Only used if categorizer is used as the executable rather than a library.
i.e. This is mutually exclusive with the Web App. It loads info from files."""
import argparse
from typing import Dict
from typing import Any
from typing import Optional
from typing import List
from pathlib import Path
import os
from git import Repo

from note_categorizer.categorizer.text_file_reader import CategoryReader
from note_categorizer.categorizer.text_file_reader import NoteReader
from note_categorizer.categorizer.parser import ParsedData, Parser
from note_categorizer.common.category import Category
from note_categorizer.common.notes import Note


def _get_repo_top_dir() -> Path:
    """Retrieves the path to the top-level directory of the repository"""
    git_repo = Repo(os.getcwd(), search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")
    return Path(git_root)


def _read_args() -> Dict[str, Any]:
    """Parses cli args and returns them."""
    parser = argparse.ArgumentParser()
    abs_repo_top_dir: Path = _get_repo_top_dir()
    default_category_filename = "category_file.txt"
    default_category_path = abs_repo_top_dir / default_category_filename
    default_note_filename = "note_file.txt"
    default_note_path = abs_repo_top_dir / default_note_filename

    parser.add_argument(
        "-cp",
        "--category_path",
        default=default_category_path,
        help=f"Absolute path to the Category (matters) text file. \
                        Each line is <name>:<keywords seperated by spaces>.\
                        Note, that no keywords are NECESSARY, but the ':' is.\
                        Please see example_category_file.txt for an example.\
                        Defaults to {default_category_path}",
        type=Path,
    )
    parser.add_argument(
        "-np",
        "--notes_path",
        default=default_note_path,
        help="Absolute path to the notes text file. \
                        Each line is a single 'bulltet point' of notes to split\
                        into various categories.\
                        Please see example_notes_file.txt for an example.\
                        Defaults to {default_note_path}",
        type=Path,
    )
    parser.add_argument(
        "-a",
        "--add_times",
        action="store_true",
        default=False,
        help="Set this flag when you want to sum the time of all\
                        notes in a category. \
                        \nNOTE: This requires a notes line getting prefixed\
                        with 'HH:MM-HH:MM: '. This should be 24 hr time.",
    )

    return vars(parser.parse_args())


def main():
    """Entry to this executable. Should only be used when NOT running Web App"""

    args: Dict[str, Any] = _read_args()

    category_reader = CategoryReader(args["category_path"])
    category_list: List[Category] = category_reader.generate_list()

    note_reader = NoteReader(args["notes_path"])
    note_list: List[Note] = note_reader.generate_list()

    note_parser = Parser(category_list)
    parsed_notes: ParsedData = note_parser.parse_notes(note_list)

    for category in category_list:
        category_notes: Optional[List[Note]] = parsed_notes.get_category_notes(category)
        print(f"Category {category.name} notes:\n")
        if category_notes is not None:
            print("\n".join(Note.notes_list_to_str_list(category_notes)))
        else:
            print("No notes for this category")
        print("---------------------------------------------------------\n\n")

    if not parsed_notes.is_fully_parsed():
        print("Unknown category notes: ")
        for note in parsed_notes.get_unknown_notes():
            print(note)

    # pylint: disable=fixme
    # TODO: Ask user to resolve unknowns manually

    # pylint: disable=fixme
    # TODO: calculate the time for notes in a group


if __name__ == "__main__":
    main()
