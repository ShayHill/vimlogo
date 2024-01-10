"""Overlay new svg elements to the reference image.

:author: Shay Hill
:created: 2023-12-30
"""

from lxml import etree
from pathlib import Path
import copy

from vim_logo.paths import REFERENCE_IMAGE_PATH
from vim_logo.letters_im import letter_m, letter_i, letter_m_mask
from vim_logo.letter_v import letter_v
from vim_logo.shared import VIEWBOX as VIEWBOX
from vim_logo.diamond import diamond
import svg_ultralight as su
from vim_logo.main import write_vim_logo

_TEST_OUTPUT = Path(__file__).parent / "test_output"


def test_reference():
    write_vim_logo(_TEST_OUTPUT / "test_reference.svg")
