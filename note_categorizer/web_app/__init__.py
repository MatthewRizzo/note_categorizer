"""Init for the entire Web App"""

import note_categorizer.web_app.server
from note_categorizer.categorizer import parser

# pylint: disable=redefined-builtin
all = ["server", "parser"]
