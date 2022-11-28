"""Acts as main for parser project. This gets exposed to libraries which consume
it. """

from typing import Dict
from typing import List
from typing import NamedTuple
from dataclasses import dataclass


from note_categorizer.common.category import Category

class ParsedData(NamedTuple):
    """Represents parsed data"""
    known_assignments: Dict[Category, List[str]]

    # Notes that still need to be added to a category
    unknown_assignments: List[str]

    def is_fully_parsed(self) -> bool:
        """ # Return
            * True when there are no more unknown assignments for notes.
            * False otherwise.
        """
        return len(self.unknown_assignments) == 0

@dataclass
class Parser():
    """Overall parser. Intended to be used as a library for other modules and
    projects."""
    valid_categories: List[Category]
