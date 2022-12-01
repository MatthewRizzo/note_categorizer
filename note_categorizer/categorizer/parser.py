"""Acts as main for parser project. This gets exposed to libraries which consume
it. """

from typing import Dict
from typing import List
from typing import Optional
from typing import NamedTuple
from typing import Type, TypeVar
from dataclasses import dataclass
import abc

from note_categorizer.common.category import Category
from note_categorizer.common.notes import Note


class ParsedData(NamedTuple):
    """Represents parsed data"""

    known_assignments: Dict[Category, List[Note]]

    # Notes that still need to be added to a category
    unknown_assignments: List[Note]

    def is_fully_parsed(self) -> bool:
        """# Return
        * True when there are no more unknown assignments for notes.
        * False otherwise.
        """
        return len(self.unknown_assignments) == 0

    def add_to_known_assignments(self, note: Note, category: Category) -> None:
        """Adds the note to the correct category.
        Creates the category in the dict if it isn't present already."""
        print(f"Adding note '{note}' to category '{category}'")
        category_info: List[Note] = self.known_assignments.get(category, [])
        category_info.append(note)
        self.known_assignments[category] = category_info

        # If this note used to be unknown, remove it
        if note in self.unknown_assignments:
            self.unknown_assignments.remove(note)

    def get_category_notes(self, category: Category) -> Optional[List[Note]]:
        """Retrieves the note(s) associated with this category.
        #  Return
        * The list of notes if the category had notes
        * None if the category had no notes"""
        return self.known_assignments.get(category, None)

    def get_unknown_notes(self) -> List[Note]:
        """Returns the notes that could not be assigned to a category."""
        return self.unknown_assignments

    def add_unknown_note(self, note: Note) -> None:
        """Adds a note to the list of ungrouped notes"""
        self.unknown_assignments.append(note)

    def move_unknown_to_known(
        self, unknown_note_index: int, new_category: Category
    ) -> None:
        """Moves a note from the unknowns to a category within the "known"""
        note_to_move: Note = self.unknown_assignments.pop(unknown_note_index)
        self.add_to_known_assignments(note_to_move, new_category)


# Added for static type checking on constructor functions
ParserStatic = TypeVar("ParserStatic", bound="Parser")
TerminalParserStatic = TypeVar("TerminalParserStatic", bound="TerminalParser")
WebParserStatic = TypeVar("WebParserStatic", bound="WebParser")


@dataclass
class Parser(abc.ABC):
    """Overall parser. Intended to be used as a library for other modules and
    projects."""

    valid_categories: List[Category]

    # Maps category to time in minutes. Only computed once fully parsed.
    category_total_time: Optional[Dict[Category, int]]

    def get_valid_category_list_str(self) -> List[str]:
        """Returns a list of strings where each element represents the
        string form of a category"""
        # pylint: disable=unnecessary-lambda-assignment disable=unnecessary-lambda
        convert_category_to_str = lambda category: str(category)
        return list(map(convert_category_to_str, self.valid_categories))

    def add_category(self, new_category: Category) -> None:
        """Adds a category to the list"""
        self.valid_categories.append(new_category)

    def get_category_by_name(self, name: str) -> Optional[Category]:
        """Returns a category (if it exists) based on its name"""
        for category in self.valid_categories:
            if category.name == name:
                return category
        return None

    @classmethod
    def from_json_notation(
        cls: Type[ParserStatic],
        serial_list: List[dict],
    ) -> Optional[ParserStatic]:
        """Instantiates object of class when the input data is a list rendered
        from a json file (i.e. after load).
        # Return
        * None When deserializing the data failed.
        * A parser object otherwise.
        """
        category_list: Optional[List[Category]] = Category.from_serial_list(serial_list)
        res: Optional[ParserStatic] = None
        if category_list is not None:
            res = cls(category_list, None)
        return res

    def compute_category_time(
        self, category: Category, fully_parsed_data: ParsedData
    ) -> None:
        """Computes the total time for the given category and saves it."""
        total_time_min = 0
        category_notes_list = fully_parsed_data.get_category_notes(category)
        if category_notes_list is None:
            return

        for note in category_notes_list:

            total_time_min = note.time.compute_time_difference()
            if self.category_total_time is None:
                self.category_total_time = {}

            category_total_time = int(self.category_total_time.get(category, 0))
            category_total_time += total_time_min
            self.category_total_time[category] = category_total_time

    def get_category_time(self, category: Category) -> int:
        """Returns the overall time difference in MINUTES for notes in the category"""
        if self.category_total_time is not None:
            return self.category_total_time[category]
        return 0

    def parse_notes(self, notes: List[Note]) -> ParsedData:
        """Parses the notes and splits them up by category as much as possible.
        # Return
        The parsed data.
        """
        parsed_data: ParsedData = ParsedData({}, [])
        for note in notes:
            category_found: bool = self._add_note_to_category(note, parsed_data)
            if category_found is False:
                parsed_data.add_unknown_note(note)

        return parsed_data

    def results_to_str(
        self, completed_parsing: ParsedData, display_time_sums: bool
    ) -> str:
        """Generates a string representing the results in a human-readable
        manner
        """
        res = ""
        for category in self.valid_categories:
            res += self._display_results(category, completed_parsing, display_time_sums)

        if not completed_parsing.is_fully_parsed():
            res += "\nUnknown category notes: "
            for note in completed_parsing.get_unknown_notes():
                res += f"\n{note}"

        return res

    def _display_results(
        self, category: Category, completed_parsing: ParsedData, display_time_sums: bool
    ) -> str:
        """Renders the current category into a string and returns it"""
        category_notes: Optional[List[Note]] = completed_parsing.get_category_notes(
            category
        )
        res = ""
        res += f"Category {category.name} notes:\n"
        if category_notes is not None:
            res += "\n".join(Note.notes_list_to_str_list(category_notes))
            if display_time_sums is True:
                start_msg = "\nTotal Time Difference (minutes):"
                res += f"{start_msg} {self.get_category_time(category)}"
        else:
            res += "No notes for this category"
        res += "\n---------------------------------------------------------\n\n"
        return res

    @abc.abstractmethod
    def resolve_unknowns(self, parsed_data: ParsedData) -> ParsedData:
        """Further parses the data by resolving unknown categorizations"""

    def calculate_category_time(self, parsed_data: ParsedData) -> None:
        """Computers the total time spent (in minutes) on each category."""
        for category in self.valid_categories:
            self.compute_category_time(category, parsed_data)

    def _add_note_to_category(self, note: Note, parsed_data: ParsedData) -> bool:
        """# Return
        True if a category was found for the note.
        False if no valid category for the note was found.
        """
        for category in self.valid_categories:
            if category.is_keyword_present(note.info):
                parsed_data.add_to_known_assignments(note, category)
                return True
        return False


@dataclass
class TerminalParser(Parser):
    """Class representing how to parse data when working through terminal"""

    valid_categories: List[Category]

    def resolve_unknowns(self, parsed_data: ParsedData) -> ParsedData:
        """Further parses the data by resolving unknown categorizations
        by prompting the user."""
        while not parsed_data.is_fully_parsed():
            selected_category: Category = self._prompt_user(
                parsed_data.get_unknown_notes()[0]
            )
            parsed_data.move_unknown_to_known(0, selected_category)
        print("Done Resolving unknown notes!\n----------------------------\n\n")
        return parsed_data

    def _prompt_user(self, note: Note) -> Category:
        """Prompts the user to get the correct category for the note.
        # Post Condition
        The category returned MUST be a valid category.
        """
        selected_category: Optional[Category] = None
        while selected_category is None:

            print("Valid category options: ")
            for idx, category in enumerate(self.valid_categories, start=0):
                print(f"{idx}) {category}")

            input_msg = f"Please select the category for this note: {note}"
            input_msg += "\nResponse) "
            selected_category_idx_str = input(input_msg)

            invalid_selection_msg = "That option is not valid. "
            invalid_selection_msg_suffix = " Please try again.\n\n"

            try:
                selected_category_idx = int(selected_category_idx_str)
            except ValueError as err:
                reason = "A non-integer was entered."
                print(invalid_selection_msg + reason + invalid_selection_msg_suffix)
                print(err)
                continue
            if (
                selected_category_idx < 0
                or selected_category_idx > len(self.valid_categories) - 1
            ):
                reason = f"Selection {selected_category_idx} is outside allowed range."
                print(invalid_selection_msg + reason + invalid_selection_msg_suffix)
                continue

            selected_category = self.valid_categories[selected_category_idx]
            print("\n")
        return selected_category


@dataclass
class WebParser(Parser):
    """Class representing how to parse data when working through Web App"""

    valid_categories: List[Category]

    def resolve_unknowns(self, parsed_data: ParsedData) -> ParsedData:
        """Further parses the data by resolving unknown categorizations
        by prompting the user."""
        # For now do nothing, and have unknowns get displayed
        # pylint: disable=fixme
        # TODO: figure out a prompting scheme that makes sense
        return parsed_data
