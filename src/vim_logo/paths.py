"""Paths to project binaries and data files.

:author: Shay Hill
:created: 2023-12-30
"""

from pathlib import Path

_PROJECT_DIR = Path(__file__).parent.parent.parent

REFERENCE_IMAGE_PATH = _PROJECT_DIR / "reference" / "vimlogo.svg"

OUTPUT = _PROJECT_DIR / "output"
