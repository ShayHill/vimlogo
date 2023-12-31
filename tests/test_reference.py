"""Overlay new svg elements to the reference image.

:author: Shay Hill
:created: 2023-12-30
"""

from lxml import etree
from pathlib import Path
import copy

from vim_logo.paths import REFERENCE_IMAGE_PATH
from vim_logo.letters_im import letter_m, letter_i
from vim_logo.diamond import diamond
import svg_ultralight as su

_TEST_OUTPUT = Path(__file__).parent / "test_output"

# ===============================================================================
#   Hard-coded transformations to align with reference image
# ===============================================================================

unit = 5.6785

scale = unit / 3
tx = 183.60404 / scale
ty = 185.12055 / scale
x_center = 293.57495 / 2 / scale
y_center = 293.80618 / 2 / scale

transform_1 = "scale({})translate({} {})".format(
    *(su.format_number(x) for x in (scale, x_center, y_center))
)

transform = "scale({})translate({} {})".format(
    *(su.format_number(x) for x in (scale, tx, ty))
)

def test_reference():
    reference_svg = etree.parse(REFERENCE_IMAGE_PATH)
    root = reference_svg.getroot()
    for element in [diamond]:
        elem = copy.deepcopy(element)
        _ = su.update_element(elem, transform=transform_1)
        root.append(elem)
    for element in [letter_i, letter_m]:
        elem = copy.deepcopy(element)
        _ = su.update_element(elem, transform=transform)
        root.append(elem)
    # letter_i_ = copy.deepcopy(letter_i)
    # su.update_element(letter_i_, transform=transform)
    # letter_m_ = copy.deepcopy(letter_m)
    # su.update_element(letter_m_, transform=transform)
    # root.append(letter_i_)
    # root.append(letter_m_)
    _ = su.write_svg(_TEST_OUTPUT / "test_reference.svg", root)






