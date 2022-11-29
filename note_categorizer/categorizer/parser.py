"""Acts as main for parser project. This gets exposed to libraries which consume
it. """

from typing import Dict
from typing import List
from typing import Optional
from typing import NamedTuple
from typing import Type, TypeVar
from dataclasses import dataclass

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
        category_info: List[Note] = self.known_assignments.get(category, [])
        category_info.append(note)
        self.known_assignments[category] = category_info

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


# Added for static type checking on constructor functions
ParserStatic = TypeVar("ParserStatic", bound="Parser")


@dataclass
class Parser:
    """Overall parser. Intended to be used as a library for other modules and
    projects."""

    valid_categories: List[Category]

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
        cls: Type[ParserStatic], serial_list: List[dict]
    ) -> Optional[ParserStatic]:
        """Instantiates object of class when the input data is a list rendered
        from a json file (i.e. after load).
        # Return
        * None When deserializing the data failed.
        * A parser object otherwise.
        """
        category_list: Optional[List[Category]] = Category.from_serial_list(serial_list)
        if category_list is not None:
            return cls(category_list)
        return None

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
