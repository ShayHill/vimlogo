"""Construct the svg from parts.

:author: Shay Hill
:created: 2024-01-10
"""

import copy
from pathlib import Path

import svg_ultralight as su

from vim_logo.diamond import diamond
from vim_logo.letter_v import letter_v
from vim_logo.letters_im import letter_i, letter_m, letter_m_mask, _SCALE_M
from vim_logo.paths import OUTPUT
from vim_logo import shared

from lxml.etree import _Element as EtreeElement  # type: ignore

def _mask_m(elem: EtreeElement) -> EtreeElement:
    mask_g = su.new_element("g", mask="url(#letter_m_mask)")
    mask_g.append(copy.deepcopy(elem))
    return mask_g

def _new_background_stroke(elem: EtreeElement) -> EtreeElement:
    """Create a fat white line around each element.

    :param elem: a `g` element with a stroked path at elem[0]
    :return: the path at elem[0] with larger than the g[0] stroke

    The reference svg file has a white padding around the entire logo. This was
    created with a polygon around the hull of the combined elements. I am using a
    stroke here to the dimensions of this can be easily changed without worrying
    about internal intersections and potential floating point errors.

    This relies on several element characteristics:

    * argument element is a `g` element
    * argument element has `id` and `transform` attribs
    * argument[0] is a path element
    * argument[0] has a `stroke-width` attrib

    This works to make an outline because the first element in the groups created by
    this project is a path element defining the fat, black outline around that
    element.
    """
    id_ = elem.attrib["id"]
    transform = elem.attrib["transform"]
    black_stroke_width = float(elem[0].attrib["stroke-width"])
    white_stroke_width = black_stroke_width + shared.FULL_OLINE_WIDTH 
    if id_ == "letter_m":
        white_stroke_width = black_stroke_width + shared.FULL_OLINE_WIDTH / _SCALE_M

    # if id_ == "letter_m":
    #     white_stroke_width /= _SCALE_M
    background = copy.deepcopy(elem[0])
    background = su.update_element(
        background,
        id_=id_ + "_background",
        transform=transform,
        stroke=shared.FULL_OLINE_COLOR,
        stroke_width=white_stroke_width
    )
    if id_ == "diamond":
        background = _mask_m(background)
    return background


def write_vim_logo(output_path: Path | str = OUTPUT / "vim_logo.svg"):
    """Write the vim logo to a file.

    :param output_path: path to write the svg to
    """
    root = su.new_svg_root(
        x_=shared.VIEWBOX[0],
        y_=shared.VIEWBOX[1],
        width_=shared.VIEWBOX[2],
        height_=shared.VIEWBOX[3],
        print_width_=shared.VIEWBOX[2],
    )

    for element in [diamond, letter_v, letter_m]:
        root.append(_new_background_stroke(element))


    # define the layer mask for the diamond
    defs = su.new_sub_element(root, "defs")
    mask = su.new_sub_element(defs, "mask", id="letter_m_mask")
    _ = su.new_sub_element(
        mask, "rect", width="100%", height="100%", fill="white"
    )
    _ = su.update_element(letter_m_mask, fill="black")
    mask.append(copy.deepcopy(letter_m_mask))

    root.append(_mask_m(diamond))

    # mask_g = su.new_sub_element(root, "g", mask="url(#letter_m_mask)")
    # mask_g.append(copy.deepcopy(diamond))

    for element in [letter_v, letter_i, letter_m]:
        root.append(copy.deepcopy(element))

    _ = su.write_svg(output_path, root)
