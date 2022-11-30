"""Module responsible for reading in the notes / category file and rendering
it into a valid dictionary."""
from dataclasses import dataclass
from pathlib import Path
from typing import List
from typing import Union
from typing import Optional
import sys
import os
import abc

from note_categorizer.common.category import Category
from note_categorizer.common.notes import Note


@dataclass
class TextReader(abc.ABC):
    """Class to read in from a text file"""

    file_path: Path

    def validate_file_exists(self, file_type: str) -> None:
        """Validates the given file paths actually exist.
        Exists if the file doesnt exist."""
        path_dne_msg = f"The file {self.file_path} for the "
        path_dne_msg += f"{file_type} file doesn't exist. Please try again"
        if not os.path.exists(self.file_path):
            print(path_dne_msg)
            sys.exit(1)

    def read_in_file(self) -> List[str]:
        """Reads in the file and outputs a list. Each index represents a line"""
        with open(self.file_path, "r", encoding="utf-8") as input_file:
            return input_file.readlines()

    @abc.abstractmethod
    def generate_list(self) -> Union[List[Category], List[Note]]:
        """Uses the information in the text file to generate the serial datastructure
        representing notes or categories."""


@TextReader.register
class CategoryReader(TextReader):
    """Class to render the text from a file into a category dict"""

    def __init__(self, file_path: Path):
        """Validates the file exists and renders it into a dictionary"""
        super().__init__(file_path)
        self.validate_file_exists("category")

    def generate_list(self) -> List[Category]:
        """Parses every line of the file to define each "category" dict"""
        file_lines: List[str] = self.read_in_file()
        categories: List[Category] = []

        for category_line in file_lines:
            if len(category_line.strip()) == 0:
                continue
            new_category = Category.from_str(category_line)
            if new_category is None:
                print(f"Category line {category_line} is malformatted. Skipping.")
                valid_category_line = "Bob Dylan: music folk concert"
                valid_category_line_no_keyword = "Giant:"
                print("Valid category line:")
                print(f"{valid_category_line}\n{valid_category_line_no_keyword}")
            else:
                categories.append(new_category)

        return categories


@TextReader.register
class NoteReader(TextReader):
    """Class to render the text from a file into a Note object"""

    def __init__(self, file_path: Path):
        """Validates the file exists and renders it into a dictionary"""
        super().__init__(file_path)
        self.validate_file_exists("note")

    def generate_list(self) -> List[Note]:
        """Parses every line of the file to define each "category" dict"""
        file_lines: List[str] = self.read_in_file()
        notes: List[Note] = []

        for note_line in file_lines:
            new_category: Optional[Note] = Note.from_str(note_line)
            if new_category is None:
                valid_note_line = "10:25-10:45: Saw Bob talking about his concert."
                print(f"Note line {note_line} is malformatted. Skipping.")
                print(f"Valid note line: {valid_note_line}")
            else:
                notes.append(new_category)

        return notes
