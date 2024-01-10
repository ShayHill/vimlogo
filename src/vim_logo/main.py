"""Construct the svg from parts.

:author: Shay Hill
:created: 2024-01-10
"""

import copy
from pathlib import Path

import svg_ultralight as su

from vim_logo.diamond import diamond
from vim_logo.letter_v import letter_v
from vim_logo.letters_im import letter_i, letter_m, letter_m_mask
from vim_logo.paths import OUTPUT
from vim_logo.shared import VIEWBOX


def write_vim_logo(output_path: Path | str = OUTPUT / "vim_logo.svg"):
    """Write the vim logo to a file.

    :param output_path: path to write the svg to
    """
    root = su.new_svg_root(
        x_=VIEWBOX[0],
        y_=VIEWBOX[1],
        width_=VIEWBOX[2],
        height_=VIEWBOX[3],
        print_width_=VIEWBOX[2],
    )

    # define the layer mask for the diamond
    defs = su.new_sub_element(root, "defs")
    mask = su.new_sub_element(defs, "mask", id="letter_m_mask")
    _ = su.new_sub_element(
        mask, "rect", x=-500, y=-500, width=1000, height=1000, fill="white"
    )
    _ = su.update_element(letter_m_mask, fill="black")
    mask.append(letter_m_mask)

    for element in [diamond]:
        mask_g = su.new_sub_element(root, "g", mask="url(#letter_m_mask)")
        mask_g.append(copy.deepcopy(element))

    for element in [letter_v, letter_i, letter_m]:
        root.append(copy.deepcopy(element))

    _ = su.write_svg(output_path, root)
