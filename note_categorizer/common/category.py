"""Represents the different categories and how individual notes should
be grouped together. Maps a category name to its description"""

from typing import List
from typing import TypeVar
from typing import Type
from typing import Optional
from typing import Any
from marshmallow import Schema, fields
from marshmallow.decorators import post_load
from marshmallow import ValidationError

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

    def __eq__(self, obj: Any) -> bool:
        """Define how 2 categories are equal"""
        if not isinstance(obj, Category):
            return False

        other_category = Category.copy(obj)
        return self.name.lower() == other_category.name.lower()

    def __hash__(self) -> int:
        """Redefine hash function so class is hashable.
        Only required because __eq__ was overriden"""
        return hash(self.name.lower())

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

    def __str__(self) -> str:
        """Define a str representation of Category"""
        return self.name

    @classmethod
    def from_serial_list(
        cls, serial_list: List[dict]
    ) -> Optional[List[StaticCategory]]:
        """Generates a list of instantiated members of the class from a list of
        serial data representing the class.
        # Return
        * None if there was an error deserializing the data to the right schema
        * The list of categories"""
        try:
            return list(
                map(lambda serial_data: CategorySchema().load(serial_data), serial_list)
            )
        except ValidationError:
            print("Your input is of the wrong form. Please check the schema")
            return None

    @classmethod
    def from_dict(
        cls: Type[StaticCategory], serial_data_dict: dict
    ) -> Optional[StaticCategory]:
        """Instantiates a category object from a dictionary representing it"""
        try:
            return CategorySchema().load(serial_data_dict)
        except ValidationError:
            print("Your input is of the wrong form. Please check the schema")
            return None

    @classmethod
    def from_str(
        cls: Type[StaticCategory], serial_data: str
    ) -> Optional[StaticCategory]:
        """Instantiates a category object from a string representing it."""
        serial_data = serial_data.strip()

        # User forgot to put :
        if ":" not in serial_data:
            return Category(serial_data, [])  # type: ignore

        name_keyword_pair: List[str] = serial_data.split(":", maxsplit=1)
        keywords_str: str = name_keyword_pair[1]
        if keywords_str.count(" ") > 0:
            raw_keywords: List[str] = keywords_str.split(" ")
            keywords = list(map(lambda keyword: keyword.strip(), raw_keywords))
            keywords = list(filter(lambda keyword: keyword != "", keywords))
        elif len(keywords_str) > 0:
            keywords = [keywords_str.strip()]
        else:
            keywords = []
        return Category(name_keyword_pair[0], keywords)  # type: ignore

    @classmethod
    def copy(cls, obj_to_copy: StaticCategory) -> StaticCategory:
        """Shallow one object of the class into another"""
        # XXX(mrizzo) This IS an object of this class. but mypy + pylint get confused
        # pylint: disable=protected-access
        return Category(obj_to_copy.name, obj_to_copy._keywords)  # type: ignore


class CategorySchema(Schema):
    """Schema representing a single category. Useful for deserializing data."""

    name = fields.String()
    keywords = fields.List(fields.String())

    @post_load
    # pylint: disable=unused-argument
    def create_category(self, data: dict, **kwargs) -> Category:
        """Creates a category"""
        return Category(**data)
