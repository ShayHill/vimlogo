"""Paths to project binaries and data files.

:author: Shay Hill
:created: 2023-12-30
"""

from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent.parent

REFERENCE_IMAGE_PATH = PROJECT_DIR / "reference" / "vimlogo.svg"

OUTPUT = PROJECT_DIR / "output"

PYPROJECT_TOML = PROJECT_DIR / "pyproject.toml"

GIT_DIR = PROJECT_DIR / ".git"
