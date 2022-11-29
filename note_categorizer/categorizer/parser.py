"""Acts as main for parser project. This gets exposed to libraries which consume
it. """

from typing import Dict
from typing import List
from typing import Optional
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

    # pylint: disable=fixme
    # TODO: the parsing algorithm
