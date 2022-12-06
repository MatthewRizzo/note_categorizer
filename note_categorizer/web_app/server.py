"""This is the server aspect of the web app. It is responsible for managing all
routes and handlers with requests from the client(s)."""
import logging
from typing import List
from typing import Optional
from typing import Tuple
from typing import Dict
from typing import Any
from typing import NamedTuple
from pathlib import Path


from flask import Flask
from flask import render_template
from flask import request
import werkzeug.serving  # needed to make production worthy app that's secure

from note_categorizer.web_app import constants
from note_categorizer.web_app.web_utils import WebUtils
from note_categorizer.categorizer.parser import WebParser, ParsedData
from note_categorizer.common.category import Category
from note_categorizer.common.notes import Note


class RequestResponseJson(NamedTuple):
    """Class representing the generic structure of a response to a request."""

    # Set to empty string to have it be ignore by frontend
    processed_data: str
    are_uncategorized: bool
    uncategorized_list: List[str]
    category_list: List[str]


# pylint: disable=too-many-instance-attributes
class WebAppServer(WebUtils):
    """Class representing the server. Implements all routes and responds with
    the correct backend logic
    """

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        port: int,
        is_debug: bool,
        is_verbose: bool,
        use_localhost: bool,
        project_root_path: Path,
    ):
        """Construct the WebAppServer"""

        self._title = constants.APP_NAME
        self._app: Flask = Flask(self._title)
        self._is_verbose = is_verbose
        self._is_debug = is_debug
        self._is_threaded = True
        self._use_localhost: bool = use_localhost
        self.public_ip: str = WebUtils.get_public_ip()

        self._parser: WebParser
        self._parsed_data: ParsedData

        # Create any Parent Classes
        WebUtils.__init__(self, self._app, port, project_root_path)

        # refreshes flask if html files change
        if self._is_debug:
            self._app.config["TEMPLATES_AUTO_RELOAD"] = True

        # Set the static and tempalte dir
        self._app.static_folder = str(self.get_static_dir_path())
        self._app.template_folder = str(self.get_templates_dir_path())

        self._logger = logging.getLogger("werkzeug")
        self._host = "0.0.0.0"
        self._port = port
        log_level = logging.INFO if self._is_debug is True else logging.ERROR
        self._logger.setLevel(log_level)

        self.generate_routes()

        if self._is_verbose:
            self.print_routes()

    def start_server(self) -> None:
        """Function that spawns the server. Note this will be a blocking
        call. Do NOT expect to call other functions after this one until the
        Web App dies"""

        if self._is_debug:
            self._app.run(
                host=self._host,
                port=self._port,
                debug=self._is_debug,
                threaded=self._is_threaded,
            )
        else:
            # FOR PRODUCTION
            werkzeug.serving.run_simple(
                hostname=self._host,
                port=self._port,
                application=self._app,
                use_debugger=self._is_debug,
                threaded=self._is_threaded,
            )

    def generate_routes(self) -> None:
        """Generates all routes needed"""
        # Recheck the public ip
        self.public_ip = self.get_public_ip()

        if self._use_localhost is False:
            self.base_route = self.get_app_base_url_str(self._port)
        else:
            # when local host is used, dont give a regular ip to start the route
            self.base_route = f"http://localhost:{self._port}"

        self.create_homepage()
        self.create_api_routes()

        if self._is_verbose:
            print(f"base url = {self.base_route}")

    def create_homepage(self) -> None:
        """Generates the homepage route and adds them to to the app"""

        @self._app.route("/", methods=["GET"])
        def index():
            return render_template("homepage.html", title=self._title)

    def create_api_routes(self) -> None:
        """Generates internal api routes and adds them to to the app"""

        @self._app.route("/submit_info", methods=["POST"])
        def process_submit_info() -> dict:
            if not isinstance(request.json, dict):
                return RequestResponseJson("", False, [], [])._asdict()

            data: Dict[str, List[str]] = request.json
            category_list, deserialized_note_list = self._deserialize_info(data)

            self._parser = WebParser(category_list, None, self._is_verbose)
            self._parsed_data = self._parser.parse_notes(deserialized_note_list)
            self._parser.calculate_category_time(self._parsed_data)

            return generate_response_after_calculation()

        @self._app.route("/submit_uncategorized_update", methods=["POST"])
        def process_uncategorized_update() -> dict:
            """Request has categories for at least one of the uncategorized notes"""
            if not isinstance(request.json, dict):
                return RequestResponseJson("", False, [], [])._asdict()

            newly_categorized: Dict[str, str] = request.json

            for note_str in newly_categorized:
                category_str = newly_categorized[note_str]
                note_to_categorize: Optional[Note] = Note.from_str(note_str.strip())
                make_note_err_msg = f"Received note string {note_str} from Request."
                make_note_err_msg += "This is an invalid note string."
                if note_to_categorize is None:
                    print(make_note_err_msg)
                    continue

                new_category: Optional[Category] = Category.from_str(category_str)
                if new_category is None:
                    categorize_err_msg = (
                        f"Received category string {category_str} from Request."
                    )
                    categorize_err_msg += "This is an invalid note string."
                    print(categorize_err_msg)
                    continue

                self._parsed_data.add_to_known_assignments(
                    note_to_categorize, new_category
                )
                if self._is_verbose:
                    category_notes = self._parsed_data.get_category_notes(new_category)
                    if category_notes is not None:
                        print(category_notes[-1])

            # Recalculate time now that more info is known
            self._parser.calculate_category_time(self._parsed_data)

            return generate_response_after_calculation()

        def generate_response_after_calculation() -> Dict[str, Any]:
            """Generates the response after calculation when similar response is required"""
            are_uncategorized = self._parsed_data.is_fully_parsed() is False
            uncategorized_note_str_list = list(
                # pylint: disable=unnecessary-lambda
                map(lambda note: str(note), self._parsed_data.get_unknown_notes())
            )
            new_processed_data = self._parser.results_to_str(self._parsed_data, True)

            response = RequestResponseJson(
                new_processed_data,
                are_uncategorized,
                uncategorized_note_str_list,
                self._parser.get_valid_category_list_str(),
            )
            return response._asdict()

    def _deserialize_info(
        self, data: Dict[str, List[str]]
    ) -> Tuple[List[Category], List[Note]]:
        """Uses data from the info post request to deserialize into note list and category list"""
        notes: List[str] = data.get("notes", [])

        category_serial: List[str] = data.get("category_info", [])
        category_list = []
        for category_str in category_serial:
            if len(category_str.strip()) == 0:
                continue
            opt_category: Optional[Category] = Category.from_str(category_str)
            if opt_category is None:
                continue
            category_list.append(opt_category)

        deserialized_note_list: List[Note] = []
        for note in notes:
            if len(note.strip()) == 0:
                continue
            deserialized_note: Optional[Note] = Note.from_str(note)

            if deserialized_note is None:
                err_msg = f"Failed to render note string {note} into a Note"
                if self._is_verbose:
                    print(err_msg)
                continue

            deserialized_note_list.append(deserialized_note)

        return (category_list, deserialized_note_list)
