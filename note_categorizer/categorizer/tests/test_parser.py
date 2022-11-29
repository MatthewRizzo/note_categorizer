"""Tests the parser module / related classes"""
from typing import Optional

from note_categorizer.categorizer.parser import Parser
from note_categorizer.common.category import Category

data_list = [
    {"name": "bob", "keywords": ["task1"]},
    {"name": "sally", "keywords": ["empire", "email"]},
]


def test_parser() -> None:
    """Test the parser"""
    parser: Optional[Parser] = Parser.from_json_notation(data_list)
    assert (
        parser is not None
    ), "Creating parser from json failed due to validation. This shouldn't happen."
    assert parser.get_category_by_name("test") is None

    parser.add_category(Category("test", ["foo_keyword"]))
    category = parser.get_category_by_name("test")

    assert isinstance(category, Category), "No category with name 'test' found."
    keyword_err_msg = "Keyword 'foo_keyword' not found in category"
    assert category.is_keyword_present("foo_keyword") is True, keyword_err_msg
