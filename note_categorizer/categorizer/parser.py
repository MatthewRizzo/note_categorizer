"""Acts as main for parser project. This gets exposed to libraries which consume
it. """

from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Type, TypeVar
from dataclasses import dataclass

from note_categorizer.common.category import Category


class ParsedData(NamedTuple):
    """Represents parsed data"""

    known_assignments: Dict[Category, List[str]]

    # Notes that still need to be added to a category
    unknown_assignments: List[str]

    def is_fully_parsed(self) -> bool:
        """# Return
        * True when there are no more unknown assignments for notes.
        * False otherwise.
        """
        return len(self.unknown_assignments) == 0


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

    @classmethod
    def from_json(cls: Type[ParserStatic], serial_list: List[dict]) -> ParserStatic:
        """Instantiates object of class when the input data is a dictionary.
        # Precondition
        The dictionary matches the schema presented by the category class"""
        category_list: List[Category] = Category.from_serial_list(serial_list)

        return cls(category_list)
