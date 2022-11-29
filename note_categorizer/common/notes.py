"""Represents the notes should be represented."""

from typing import TypeVar
from typing import Type
from typing import List
from typing import Optional
from typing import NamedTuple
import sys

from dataclasses import dataclass
from datetime import datetime
from marshmallow import ValidationError


@dataclass
class NoteTime:
    """Class representing time"""

    start_time: Optional[datetime]
    end_time: Optional[datetime]


class TimeInfo(NamedTuple):
    """Class representing time and info of a note"""

    time: NoteTime
    info: str


# Added for static type checking on constructor functions
NoteStatic = TypeVar("NoteStatic", bound="Note")


@dataclass
class Note:
    """Represents a single note"""

    time: NoteTime
    info: str

    @classmethod
    def from_str(cls: Type[NoteStatic], raw_file_data: str) -> Optional[NoteStatic]:
        """Instantiates a note object from a string with all needed information
        using JUST a string (i.e. a line from a file)
        """
        try:
            time, info = cls._check_for_time(raw_file_data.strip())
            return Note(time, info)  # type: ignore
        except ValidationError:
            print("Your input is of the wrong form. Please check the schema for note")
            return None

    @classmethod
    def _check_for_time(cls: Type[NoteStatic], data: str) -> TimeInfo:
        """Check's to see if the start and end time is listed or not.
        If it is, returns a tuple representing them.
        \nNOTE: The expected line format is '10:25-10:45: '"""
        time = NoteTime(None, None)
        if "-" not in data or ":" not in data:
            # can assume it is all just info and no time
            return TimeInfo(time, data)

        time_format_str = "%H:%M"
        time_info_pair = data.split(": ", maxsplit=1)
        start_time_str, end_time_str = time_info_pair[0].split("-")

        # pylint: disable=unnecessary-lambda-assignment
        err_msg_func = (
            lambda time_type, time_str: f"The {time_type} time '{time_str}' is "
        )
        err_msg = (
            "not part of a properly formatted note. It should be HH:MM: <notes here>"
        )
        try:
            time.start_time = datetime.strptime(start_time_str, time_format_str)
        except ValueError as err:
            print(err)
            print(err_msg_func("start", start_time_str) + err_msg)
            time.start_time = None
            sys.exit(1)

        try:
            time.end_time = datetime.strptime(end_time_str, time_format_str)
        except ValueError as err:
            print(err)
            print(err_msg_func("end", end_time_str) + err_msg)
            time.end_time = None
            sys.exit(1)

        return TimeInfo(time, time_info_pair[1])

    def __str__(self) -> str:
        res_str = "* "
        if self.time.start_time is None:
            res_str += "HH:MM"
        else:
            res_str += str(self.time.start_time.time()).strip()

        res_str += "-"

        if self.time.end_time is None:
            res_str += "HH:MM"
        else:
            res_str += str(self.time.end_time.time()).strip()

        res_str += f": {self.info}"
        return res_str

    @classmethod
    def notes_list_to_str_list(cls, note_list: List[NoteStatic]) -> List[str]:
        """Converts a list of notes to a list of strings representing them"""
        # pylint: disable=unnecessary-lambda
        return list(map(lambda note: str(note), note_list))
