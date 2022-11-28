"""Represents the different categories and how individual notes should
be grouped together. Maps a category name to its description"""

from dataclasses import dataclass
from typing import List


@dataclass
class Category():
    """Represents a category"""
    # One work name for the category
    name: str

    # Keywords that ~can~ be asscribed to notes of this category
    keywords: List[str]
