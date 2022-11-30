"""Represents the notes should be represented."""

from typing import TypeVar
from typing import Type
from typing import List
from typing import Optional
from typing import NamedTuple
from math import ceil

from dataclasses import dataclass
from datetime import datetime, timedelta
from marshmallow import ValidationError


@dataclass
class NoteTime:
    """Class representing time"""

    start_time: Optional[datetime]
    end_time: Optional[datetime]
    time_difference_min: Optional[int]

    # Used when the user inputs just '+<minx>' rather than a range
    has_time_range: bool

    def compute_time_difference(self) -> int:
        """Calculates the time difference between the times in minutes"""
        if (
            self.has_time_range
            and self.end_time is not None
            and self.start_time is not None
        ):
            diff_seconds: timedelta = self.end_time - self.start_time
            seconds_diff = diff_seconds.total_seconds()
            minutes_diff: int = ceil(seconds_diff // 60)
            self.time_difference_min = minutes_diff
            return minutes_diff
        if self.has_time_range is False and self.time_difference_min is not None:
            return self.time_difference_min
        return 0


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
            time_info: TimeInfo = cls._check_for_time(raw_file_data.strip())
            return Note(time_info.time, time_info.info)  # type: ignore
        except ValidationError:
            print("Your input is of the wrong form. Please check the schema for note")
            return None

    @classmethod
    def _check_for_time(cls: Type[NoteStatic], data: str) -> TimeInfo:
        """Check's to see if the start and end time is listed or not.
        If it is, returns a tuple representing them.
        \nNOTE: The expected line format is '10:25-10:45: or '+<minx>:'"""
        time_info = None
        if "-" not in data and ":" in data and "+" in data.split(":")[0]:
            time_info = cls._handle_time_difference_in_note(data)

        elif "-" in data and ":" in data:
            # default case of there being a time range
            time_info = cls._handle_time_range(data)
        elif ("-" in data or "+" in data) and " " in data:
            time_info = cls._handle_improper_colon_format(data)

        if time_info is None:
            # can assume it is all just info and no time
            time = NoteTime(None, None, None, True)
            time_info = TimeInfo(time, data)

        return time_info

    @classmethod
    def _handle_time_range(cls, data: str, verbose: bool = True) -> Optional[TimeInfo]:
        """Handles when a note has a time range.
        # Return
        * `None` - When the data is determined to NOT be using time ranges.
        * `TimeInfo` - When the data has time ranges and they are determined
        """
        note_time = NoteTime(None, None, None, True)
        if " " in data:
            time_info_pair = data.split(" ", maxsplit=1)
        else:
            time_info_pair = ["", data]

        try:
            start_time_str, end_time_str = time_info_pair[0].split("-")
        except ValueError as err:
            if verbose:
                print(err)
                print(f"Unpacking a time_info_pair {time_info_pair} failed")
            return None

        note_time.start_time = cls._pick_correct_time_fmt(start_time_str)
        note_time.end_time = cls._pick_correct_time_fmt(end_time_str)

        return TimeInfo(note_time, time_info_pair[1])

    @classmethod
    def _handle_time_difference_in_note(
        cls, data: str, verbose: bool = True
    ) -> Optional[TimeInfo]:
        """Generates TimeInfo when the user has a note with time difference
        rather than a time range.
        # Return
        * `None` - When the data is determined to NOT be using time differences.
        * `TimeInfo` - When the data has time differences and they are determined
        """
        # When user just adds time difference
        time = NoteTime(None, None, None, False)

        if "+" not in data:
            return None

        # get minute from '+<min>:'
        str_time_diff = (
            data.split("+", maxsplit=1)[1]
            .split(" ", maxsplit=1)[0]
            .split(":", maxsplit=1)[0]
            .strip()
        )
        try:
            time_diff = int(str_time_diff)
        except TypeError as err:
            if verbose:
                print(err)
                print(
                    "The +<min>: section of a note did not have a valid number for <min>"
                )
            return None

        time.time_difference_min = time_diff
        info_without_colon = data.split(str(str_time_diff), maxsplit=1)[1]
        if ":" in data:
            info: str = data.split(": ", maxsplit=1)[1]
        elif len(info_without_colon) > 0:
            info = info_without_colon.strip()
        else:
            return None

        return TimeInfo(time, info)

    @classmethod
    def _handle_improper_colon_format(cls, data: str) -> Optional[TimeInfo]:
        """Based on testing, some users forget to add the ':' but are otherwise
        correct. This function handles that case by ignoring the missing colon\
        and routing to the correct handler.
        # Return
        * `None` - When the data is determined to NOT be using time differences or ranges.
        * `TimeInfo` - When the data has time info and it can be determined.
        """
        time_difference_res = cls._handle_time_difference_in_note(data, True)
        if time_difference_res is not None:
            return time_difference_res

        time_range_res = cls._handle_time_range(data, False)
        if time_range_res is not None:
            return time_range_res

        # Means there is DEFINETLY no time info
        return None

    @classmethod
    def _parse_time(
        cls,
        time_fmt_string: str,
        raw_time: str,
        time_type: str,
        verbose: bool = False,
    ) -> Optional[datetime]:
        """Attempts to parse a string with a given time fmt string

        # Args
            * time_fmt_string (str): The time format string to use
            * raw_time (str): The raw string (potentially) containing a time value
            * time (NoteTime): A NoteTime object to manipulate as needed
            * type (str): Start or end
            * verbose (bool, optional): Should error handling be verbose

        # Returns
            * Optional[datetime]:
                * The time found within the string if it exists
                * None if there is no time
        """
        err_msg = (
            "not part of a properly formatted note. It should be HH:MM: <notes here>"
        )
        try:
            return datetime.strptime(raw_time, time_fmt_string)
        except ValueError as err:
            if verbose:
                print(err)
                print(f"The {time_type} time {raw_time}" + err_msg)
            return None

    @classmethod
    def _pick_correct_time_fmt(cls, time_str: str) -> Optional[datetime]:
        """Tries to find the correct time format string to use for the given time string.
        # Return
        * The datetime if one is found
        * None if no format strings worked"""
        # Allow for other formats
        format_strings = ["%H:%M", "%H%M"]

        format_start_time = None
        # Keep going until the correct format string is used
        for fmt_string in format_strings:
            format_start_time = cls._parse_time(fmt_string, time_str, "start")
            if format_start_time is not None:
                break

        return format_start_time

    def __str__(self) -> str:
        res_str = ""
        if self.time.has_time_range is True:
            if self.time.start_time is None:
                res_str += "HH:MM"
            else:
                res_str += str(self.time.start_time.time()).strip()

            res_str += "-"

            if self.time.end_time is None:
                res_str += "HH:MM"
            else:
                res_str += str(self.time.end_time.time()).strip()
        else:
            res_str = f"+{self.time.time_difference_min}"

        res_str += f": {self.info}"
        return res_str

    @classmethod
    def notes_list_to_str_list(cls, note_list: List[NoteStatic]) -> List[str]:
        """Converts a list of notes to a list of strings representing them"""
        # pylint: disable=unnecessary-lambda
        return list(map(lambda note: "* " + str(note), note_list))
