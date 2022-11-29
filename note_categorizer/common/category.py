"""Represents the different categories and how individual notes should
be grouped together. Maps a category name to its description"""

from typing import List
from typing import TypeVar
from typing import Type
from marshmallow import Schema, fields
from marshmallow.decorators import post_load

# Added for static type checking on constructor functions
StaticCategory = TypeVar("StaticCategory", bound="Category")


class Category:
    """Represents a category"""

    def __init__(self, name: str, keywords: List[str]) -> None:
        """Initializes a category. Makes all keywords lowercase."""
        # One work name for the category
        self.name: str = name

        # Keywords that ~can~ be asscribed to notes of this category
        added_keywords = self.generate_keywords_from_name(keywords)
        unformatted_keywords = keywords + added_keywords
        self._keywords: List[str] = list(
            map(lambda keyword: keyword.lower(), unformatted_keywords)
        )

    def generate_keywords_from_name(self, default_keywords: List[str]) -> List[str]:
        """Adds to the list of keywords by generating them from category name.
        Does not allow for duplicates with existing keywords.
        # Return
        * The keywords generated
        # Parameters
        * `default_keywords` - The keywords passed to the constructor
        """
        name_components = self.name.split(" ")
        new_keywords = []
        for component in name_components:
            if component.lower() not in default_keywords:
                new_keywords.append(component.lower())
        return new_keywords

    def is_keyword_present(self, phrase: str) -> bool:
        """Checks the given phrase to see if any keywords of this category are present.
        # Return
            * True if a keyword is present
            * False otherwise."""
        lowercase_phrase = phrase.lower()
        for keyword in self._keywords:
            if keyword in lowercase_phrase:
                return True
        return False

    @classmethod
    def from_serial_list(cls, serial_list: List[dict]) -> List[StaticCategory]:
        """Generates a list of instantiated members of the class from a list of
        serial data representing the class."""
        return list(
            map(lambda serial_data: CategorySchema().load(serial_data), serial_list)
        )

    @classmethod
    def from_dict(cls: Type[StaticCategory], serial_data_dict: dict) -> StaticCategory:
        """Instantiates a category object from a dictionary representing it"""
        return CategorySchema().load(serial_data_dict)


class CategorySchema(Schema):
    """Schema representing a single category. Useful for deserializing data."""

    name = fields.String()
    keywords = fields.List(fields.String())

    @post_load
    # pylint: disable=unused-argument
    def create_category(self, data: dict, **kwargs) -> Category:
        """Creates a category"""
        return Category(**data)
