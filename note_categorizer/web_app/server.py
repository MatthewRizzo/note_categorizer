"""This is the server aspect of the web app. It is responsible for managing all
routes and handlers with requests from the client(s)."""
import logging
from typing import List
from typing import Optional
from typing import Dict

from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
import werkzeug.serving  # needed to make production worthy app that's secure

from note_categorizer.web_app import constants
from note_categorizer.web_app.web_utils import WebUtils
from note_categorizer.categorizer.parser import WebParser, ParsedData
from note_categorizer.common.category import Category
from note_categorizer.common.notes import Note

# pylint: disable=too-many-instance-attributes
class WebAppServer(WebUtils):
    """Class representing the server. Implements all routes and responds with
    the correct backend logic
    """

    def __init__(
        self, port: int, is_debug: bool, is_verbose: bool, use_localhost: bool
    ):
        """Construct the WebAppServer"""

        self._title = constants.APP_NAME
        self._app: Flask = Flask(self._title)
        self._is_verbose = is_verbose
        self._is_debug = is_debug
        self._is_threaded = True
        self._use_localhost: bool = use_localhost
        self.public_ip: str = WebUtils.get_public_ip()

        # Create any Parent Classes
        WebUtils.__init__(self, self._app, port)

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
        def process_submit_info():
            data: Dict[str, List[str]] = request.json
            notes: List[str] = data.get("notes")

            category_serial: List[str] = data.get("category_info")
            category_list = list(
                map(
                    # pylint: disable=unnecessary-lambda
                    lambda category_serial_str: Category.from_str(category_serial_str),
                    category_serial,
                )
            )

            if category_list is None:
                err_msg = "Failed to render category list from serial list"
                if self._is_verbose:
                    print(err_msg)
                return jsonify(err_msg)

            deserialized_note_list: List[Note] = []
            for note in notes:
                deserialized_note: Optional[List[Note]] = Note.from_str(note)

                if deserialized_note is None:
                    err_msg = f"Failed to render note string {note} into a Note"
                    if self._is_verbose:
                        print(err_msg)
                    continue

                deserialized_note_list.append(deserialized_note)

            parser: WebParser = WebParser(category_list, None)
            parsed_data: ParsedData = parser.parse_notes(deserialized_note_list)
            parser.calculate_category_time(parsed_data)
            return jsonify(parser.results_to_str(parsed_data, True))
