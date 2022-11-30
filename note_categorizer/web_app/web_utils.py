"""Module containing utility functions for the web app"""
# ------------------------------STANDARD DEPENDENCIES-----------------------------#
from pathlib import Path
from flask import Flask
import requests
from requests.exceptions import ReadTimeout

# ------------------------------Project Imports-----------------------------#
from note_categorizer.web_app import constants
from note_categorizer.common.common_utils import CommonUtils

# pylint: disable=too-few-public-methods
class WebUtils(CommonUtils):
    """Uility class to handle common things such as pathing"""

    root_dir_path = CommonUtils.get_repo_top_dir()
    web_app_dir_path = Path(root_dir_path / constants.PATH_FROM_ROOT_TO_WEB_APP)
    frontend_dir_path = Path(web_app_dir_path / constants.FRONTEND_DIR_NAME)
    static_dir_path = Path(frontend_dir_path / constants.STATIC_DIR_NAME)
    templates_dir_path = Path(frontend_dir_path / constants.TEMPLATE_DIR_NAME)
    app: Flask
    port: int

    def __init__(self, app: Flask = None, port: int = None) -> None:
        """Class used to implement any helper functions needed for flask that
        don't directly achieve functionality
        """
        self.cls = self.__class__

        # onyl set the vars if they are not already set
        self.cls.app = app if app is not None else self.cls.app
        self.cls.port = port if port is not None else self.cls.port

    @classmethod
    def get_static_dir_path(cls) -> Path:
        """Get the abs path to the static dir"""
        return cls.static_dir_path

    @classmethod
    def get_templates_dir_path(cls) -> Path:
        """Get the abs path to the template dir"""
        return cls.templates_dir_path

    def print_routes(self) -> None:
        """Print all get-able links served by this app"""
        print("Existing URLs:")
        print("\n".join(self._get_available_uri()))
        print("-------------------------------\n")

    def _get_available_uri(self) -> list:
        """Returns a list of all GET-able endpoints"""
        # pylint: disable=unnecessary-lambda-assignment
        create_url = lambda endpoint: f"http://localhost:{self.cls.port}{endpoint}"
        available_links = list(map(create_url, self.cls.app.url_map.iter_rules()))
        available_links.sort()
        return available_links

    @classmethod
    def get_public_ip(cls) -> str:
        """Gets the public / external ip of this device.
        # Return
        * localhost if the public ip could not be obtained.
        * The full ip public address"""
        base = "http://"
        try:
            ip_dot_notation = str(
                requests.get(
                    "https://api.ipify.org", timeout=constants.REQUESTS_TIMEOUT_SEC
                ).content.decode("utf8")
            )
            return base + ip_dot_notation
        except ReadTimeout as err:
            print(err)
            print("Error with get request for public ip")
            return "localhost"

    @classmethod
    def get_app_base_url_str(cls, port: int) -> str:
        """# Return
        The base url for this app (i.e. `http://localhost:port`
        Note: If the public ip cannot be obtained. 0.0.0.0 is used instead"""
        base_ip = cls.get_public_ip()
        full_base = base_ip + ":" + str(port)
        return full_base
