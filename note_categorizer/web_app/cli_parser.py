"""Module responsible for parsing CLI args relevant to the Web App"""
# ------------------------------STANDARD DEPENDENCIES-----------------------------#
import argparse
import os
from typing import Dict
from typing import Any
from pathlib import Path

# ------------------------------Project Imports-----------------------------#
from note_categorizer.web_app import constants

# pylint: disable=too-few-public-methods
class CLIParser:
    """Class responsible for parsing cli args to the Web App program.
    After creation, parsed args are available via get_parsed_args()"""

    def __init__(self):
        self.parser = argparse.ArgumentParser(description=constants.APP_NAME)
        self._create_expected_params()

        self._args = vars(self.parser.parse_args())

    def get_parsed_args(self) -> Dict[str, Any]:
        """# Return
        The arguments from CLI after parsing the passed in flags.
        """
        return self._args

    def _create_expected_params(self) -> None:
        """#post
        The `parse_args()` can be called
        """
        env_port = os.environ.get("PORT")
        self.parser.add_argument(
            "-p",
            "--port",
            type=int,
            required=False,
            help="The port The Web App is run from",
            default=env_port if env_port is not None else constants.DEFAULT_PORT,
            dest="port",
        )

        # debugMode will default to false - only true when the flag exists
        self.parser.add_argument(
            "--debugModeOn",
            action="store_true",
            dest="debugMode",
            required=False,
            help="Use debug mode for development environments",
            default=False,
        )
        self.parser.add_argument(
            "--debugModeOff",
            action="store_false",
            dest="debugMode",
            required=False,
            help="Dont use debug mode for production environments",
            default=True,
        )

        self.parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            default=False,
            dest="verbose",
            help="Set this flag to have more information get printed",
        )

        localhost_help = "Set this flag to have all displayed url's"
        localhost_help += "be localhost instead of an actual IP"
        self.parser.add_argument(
            "-l",
            "--localhost",
            action="store_true",
            default=False,
            dest="use_localhost",
            help=localhost_help,
        )

        project_root_help = "Set this flag to have all displayed url's"
        project_root_help += "be localhost instead of an actual IP"
        self.parser.add_argument(
            "-r",
            "--project_root_path",
            default=None,
            type=Path,
            help=project_root_help,
        )
