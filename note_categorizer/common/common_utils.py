"""Module containing utility functions for both the Web App and categorizer"""

from typing import Optional
from pathlib import Path
import os
from git import Repo

# pylint: disable=too-few-public-methods
class CommonUtils:
    """Class that exposes classmethod utility functions"""

    project_root_abs_path: Optional[Path] = None

    @classmethod
    def get_repo_top_dir(cls) -> Path:
        """Retrieves the path to the top-level directory of the repository"""
        if cls.project_root_abs_path is None:
            git_repo = Repo(os.getcwd(), search_parent_directories=True)
            git_root = git_repo.git.rev_parse("--show-toplevel")
            cls.project_root_abs_path = git_root
        return Path(cls.project_root_abs_path)
