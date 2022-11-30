"""Only used if categorizer is used as the executable rather than a library.
i.e. This is mutually exclusive with the Web App. It loads info from files."""
import argparse
from typing import Dict
from typing import Any
from typing import Optional
from typing import List
from pathlib import Path

from note_categorizer.categorizer.text_file_reader import CategoryReader
from note_categorizer.categorizer.text_file_reader import NoteReader
from note_categorizer.categorizer.parser import ParsedData, TerminalParser
from note_categorizer.common.category import Category
from note_categorizer.common.notes import Note
from note_categorizer.common.common_utils import CommonUtils


def _read_args() -> Dict[str, Any]:
    """Parses cli args and returns them."""
    parser = argparse.ArgumentParser()
    abs_repo_top_dir: Path = CommonUtils.get_repo_top_dir()
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


def display_category_results(
    category: Category,
    terminal_note_parser: TerminalParser,
    completed_parsing: ParsedData,
    args: Dict[str, Any],
) -> None:
    """Displays results to terminal for a given category.
    Halfway deprecated."""
    category_notes: Optional[List[Note]] = completed_parsing.get_category_notes(
        category
    )
    print(f"Category {category.name} notes:\n")
    if category_notes is not None:
        print("\n".join(Note.notes_list_to_str_list(category_notes)))
        if args["add_times"] is True:
            start_msg = "Total Time Difference (minutes):"
            print(f"{start_msg} {terminal_note_parser.get_category_time(category)}")
    else:
        print("No notes for this category")
    print("---------------------------------------------------------\n\n")


def display_results(
    category_list: List[Category],
    terminal_note_parser: TerminalParser,
    completed_parsing: ParsedData,
    args: Dict[str, Any],
) -> None:
    """Display all results to terminal. Halfway deprecated."""
    for category in category_list:
        display_category_results(
            category, terminal_note_parser, completed_parsing, args
        )

    if not completed_parsing.is_fully_parsed():
        print("Unknown category notes: ")
        for note in completed_parsing.get_unknown_notes():
            print(note)


def main() -> None:
    """Entry to this executable. Should only be used when NOT running Web App"""

    args: Dict[str, Any] = _read_args()

    category_reader = CategoryReader(args["category_path"])
    category_list: List[Category] = category_reader.generate_list()

    note_reader = NoteReader(args["notes_path"])
    note_list: List[Note] = note_reader.generate_list()

    terminal_note_parser = TerminalParser(category_list, {})
    parsed_notes: ParsedData = terminal_note_parser.parse_notes(note_list)

    completed_parsing: ParsedData = terminal_note_parser.resolve_unknowns(parsed_notes)
    if args["add_times"] is True:
        terminal_note_parser.calculate_category_time(completed_parsing)

    res = terminal_note_parser.results_to_str(completed_parsing, True)
    print(res)


if __name__ == "__main__":
    main()
