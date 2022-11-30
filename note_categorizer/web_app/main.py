#!/usr/bin/env
"""Main used for the Web App"""
# ------------------------------STANDARD DEPENDENCIES-----------------------------#
from typing import Dict, Any

# ------------------------------Project Imports-----------------------------#
from note_categorizer.web_app.cli_parser import CLIParser
from note_categorizer.web_app.server import WebAppServer

# pylint: disable=too-few-public-methods
class Main:
    """Class encapsulating a 'main' for the Web App.
    Just instantiating it is all that is required to start up the app"""

    def __init__(self) -> None:
        """Instantiate this class to start the Web App.
        Self contained. Handles CLI flags and everything else
        """
        self.cli_parser = CLIParser()
        cli_args: Dict[str, Any] = self.cli_parser.get_parsed_args()

        self.app = WebAppServer(
            cli_args["port"],
            cli_args["debugMode"],
            cli_args["verbose"],
            cli_args["use_localhost"],
        )
        self.app.start_server()


def start() -> None:
    """Entry point to the Web App main"""
    Main()


if __name__ == "__main__":
    start()
