"""Tests relating to the category module of common"""
from typing import List

from note_categorizer.common.category import Category
from note_categorizer.common.category import CategorySchema

data_list = [
    {"name": "bob", "keywords": ["task1"]},
    {"name": "sally", "keywords": ["empire", "email"]},
]


def test_from_serial_list() -> None:
    """Test validating schema for list of categories"""
    category_list: List[Category] = Category.from_serial_list(data_list)
    list_len = len(category_list)

    len_err_msg = f"Deserialized list has length {list_len}, expected 2"
    assert list_len == 2, len_err_msg
    type_err_msg = "Deserialized data in the list is not a Category"
    assert isinstance(category_list[0], Category), type_err_msg
    assert category_list[0].name in ["bob", "sally"]
    assert category_list[1].name in ["bob", "sally"]


def test_categoryschema() -> bool:
    """Test validating schema for 1 category."""
    category: Category = CategorySchema().load(data_list[0])

    type_err_msg = "Deserialized data in the list is not a Category"
    assert isinstance(category, Category), type_err_msg
    name_err_msg = f"Deserialized category name {(category.name)} should be Bob."
    assert category.name == "bob", name_err_msg

    expected_keywords = data_list[0]["keywords"]
    for keyword in expected_keywords:
        err_msg = f"Keyword {keyword} was not present in deserialized schema: "
        err_msg += f"{category._keywords}"  # pylint: disable=protected-access
        assert category.is_keyword_present(keyword) is True, err_msg

    return True


def test_is_keyword_present() -> None:
    """Test checking if keyword is present"""
    category: Category = CategorySchema().load(data_list[0])
    err_msg = "Keyword task1 was not present in deserialized schema: "
    err_msg += f"{category._keywords}"  # pylint: disable=protected-access
    assert category.is_keyword_present("task1") is True, err_msg

    keyword_err_msg = "Keyword 'foo' is not a keyword for the category. \
        But was found anyway."
    keyword_not_present_err_msg = keyword_err_msg
    assert category.is_keyword_present("foo") is False, keyword_not_present_err_msg


def test_from_dict() -> None:
    """Testing if loading a single dict works"""
    category: Category = Category.from_dict(data_list[0])
    assert isinstance(category, Category) is True
    for keyword in data_list[0]["keywords"]:
        assert category.is_keyword_present(keyword)
