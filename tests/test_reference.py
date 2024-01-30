"""Overlay new svg elements to the reference image.

:author: Shay Hill
:created: 2023-12-30
"""

from pathlib import Path

from vimlogo.main import write_vim_logo

_TEST_OUTPUT = Path(__file__).parent / "test_output"


def test_reference():
    write_vim_logo(_TEST_OUTPUT / "test_reference.svg")
