#!/usr/bin/env
"""Main used for the Web App"""
# ------------------------------STANDARD DEPENDENCIES-----------------------------#
from typing import Dict, Any
import urllib.request
import sys

# ------------------------------Project Imports-----------------------------#
from note_categorizer.web_app.cli_parser import CLIParser
from note_categorizer.web_app.server import WebAppServer


def has_internet() -> bool:
    """This application REQUIRES there be internet.
    Check to make sure the device has it by pinging a common website.
    # Return
    * True if it has internet
    * False otherwise
    """
    try:
        # pylint: disable=unused-variable
        with urllib.request.urlopen("http://google.com") as open_url:
            pass
        return True
    # We dont actually care about the error, just that it doesnt reach the webpage
    # pylint: disable=bare-except
    except:
        return False


# pylint: disable=too-few-public-methods
class Main:
    """Class encapsulating a 'main' for the Web App.
    Just instantiating it is all that is required to start up the app"""

    def __init__(self) -> None:
        """Instantiate this class to start the Web App.
        Self contained. Handles CLI flags and everything else
        """
        if not has_internet():
            print("This device has no internet connection. Cannot Start. Exiting.")
            sys.exit(1)

        self.cli_parser = CLIParser()
        cli_args: Dict[str, Any] = self.cli_parser.get_parsed_args()

        self.app = WebAppServer(
            cli_args["port"],
            cli_args["debugMode"],
            cli_args["verbose"],
            cli_args["use_localhost"],
            cli_args["project_root_path"],
        )
        self.app.start_server()


def start() -> None:
    """Entry point to the Web App main"""
    Main()


if __name__ == "__main__":
    start()
