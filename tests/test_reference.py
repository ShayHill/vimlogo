"""Overlay new svg elements to the reference image.

:author: Shay Hill
:created: 2023-12-30
"""

from lxml import etree
from pathlib import Path
import copy

from vim_logo.paths import REFERENCE_IMAGE_PATH
from vim_logo.letters_im import letter_m, letter_i, letter_m_mask
from  vim_logo.letter_v import letter_v
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

transform_2 = "translate({} {})".format(
    *(su.format_number(x) for x in (-x_center, -y_center))
)

transform_3 = "translate({} {})".format(
    *(su.format_number(x) for x in (x_center * scale, y_center * scale))
)

transform_4 = "scale(1)translate({} {})".format(
    *(su.format_number(x) for x in (-x_center * scale, -y_center * scale))
)

transform = "scale({})".format(
    *(su.format_number(x) for x in (1, tx, ty))
)

def test_reference():
    reference_svg = etree.parse(REFERENCE_IMAGE_PATH)
    # root =  reference_svg.getroot()
    # defs = root[0]
    root = su.new_svg_root(x_=0, y_=0, width_=293.57495, height_=293.80619, print_width_=293.57495)
    defs = su.new_sub_element(root, "defs")
    _ = su.update_element(letter_m_mask, transform=transform_4)
    mask = su.new_sub_element(defs, "mask", id="letter_m_mask_mask")
    _ = su.new_sub_element(mask, "rect", x=-500, y=-500, width=1000, height=1000, fill="white")
    _ = su.update_element(letter_m_mask, fill="black")
    mask.append(letter_m_mask)


    for element in [diamond]:
        elem = copy.deepcopy(element)
        _ = su.update_element(elem, transform=transform_3)
        _ = su.update_element(elem, mask="url(#letter_m_mask_mask)")
        root.append(elem)

    for element in [letter_v]:
        elem = copy.deepcopy(element)
        # _ = su.update_element(elem, transform=transform2)
        root.append(elem)

    for element in [letter_i, letter_m]:
        elem = copy.deepcopy(element)
        # _ = su.update_element(elem, opacity=0.5)
        _ = su.update_element(elem, transform=transform)
        root.append(elem)

    # letter_i_ = copy.deepcopy(letter_i)
    # su.update_element(letter_i_, transform=transform)
    # letter_m_ = copy.deepcopy(letter_m)
    # su.update_element(letter_m_, transform=transform)
    # root.append(letter_i_)
    # root.append(letter_m_)
    _ = su.write_svg(_TEST_OUTPUT / "test_reference.svg", root, pretty_print=True)






