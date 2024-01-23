"""Construct the svg from parts.

:author: Shay Hill
:created: 2024-01-10
"""

import copy
from pathlib import Path

import svg_ultralight as su
from lxml.etree import _Element as EtreeElement  # type: ignore

from vim_logo import (
    diamond as diamond_module,
    letter_v as letter_v_module,
    letters_im as letters_im_module,
    params_diamond,
    shared,
)
from vim_logo.diamond import diamond, diamond_outer
from vim_logo.glyphs import gap_polygon, get_polygon_union, new_data_string
from vim_logo.letter_v import V_STROKE_WIDTH, elem_v, v_outer
from vim_logo.letters_im import (
    _IM_SCALE,
    IM_STROKE_WIDTH,
    elem_im,
    letter_m_pts,
    letter_m_pts_mask,
)
from vim_logo.paths import OUTPUT


def _mask_m(elem: EtreeElement) -> EtreeElement:
    mask_g = su.new_element("g", mask="url(#letter_m_mask)")
    mask_g.append(copy.deepcopy(elem))
    return mask_g


# def _new_background_stroke(elem: EtreeElement) -> EtreeElement:
#     """Create a fat white line around each element.

#     :param elem: a `g` element with a stroked path at elem[0]
#     :return: the path at elem[0] with larger than the g[0] stroke

#     The reference svg file has a white padding around the entire logo. This was
#     created with a polygon around the hull of the combined elements. I am using a
#     stroke here to the dimensions of this can be easily changed without worrying
#     about internal intersections and potential floating point errors.

#     This relies on several element characteristics:

#     * argument element is a `g` element
#     * argument element has `id` and `transform` attribs
#     * argument[0] is a path element
#     * argument[0] has a `stroke-width` attrib

#     This works to make an outline because the first element in the groups created by
#     this project is a path element defining the fat, black outline around that
#     element.
#     """
#     id_ = elem.attrib["id"]
#     transform = elem.attrib["transform"]
#     black_stroke_width = float(elem[0].attrib["stroke-width"])
#     white_stroke_width = black_stroke_width + shared.FULL_OLINE_WIDTH
#     # if id_ == "letter_m":
#     #     white_stroke_width = black_stroke_width + shared.FULL_OLINE_WIDTH / _SCALE_M

#     # if id_ == "letter_m":
#     #     white_stroke_width /= _SCALE_M
#     background = copy.deepcopy(elem[0])
#     background = su.update_element(
#         background,
#         id_=id_ + "_background",
#         transform=transform,
#         stroke=shared.FULL_OLINE_COLOR,
#         stroke_width=white_stroke_width
#     )
#     if id_ == "diamond":
#         background = _mask_m(background)
#     return background


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

    if shared.FULL_OLINE_WIDTH > IM_STROKE_WIDTH / 2:
        ltr_m = gap_polygon(
            letter_m_pts_mask, shared.FULL_OLINE_WIDTH + IM_STROKE_WIDTH
        )
    else:
        ltr_m = gap_polygon(letter_m_pts, shared.FULL_OLINE_WIDTH + IM_STROKE_WIDTH)
    background = [
        gap_polygon(v_outer, shared.FULL_OLINE_WIDTH + V_STROKE_WIDTH),
        gap_polygon(
            diamond_outer, shared.FULL_OLINE_WIDTH + params_diamond.STROKE_WIDTH
        ),
    ]
    background_paths = get_polygon_union(
        *background, letter_m_pts_mask, ltr_m, negative={2}
    )
    # background_paths = get_polygon_union(*background, ltr_m )
    # background_paths = get_polygon_union(ltr_m)
    d_background = new_data_string(*background_paths)
    root.append(
        su.new_sub_element(
            root,
            "path",
            d=d_background,
            fill=shared.FULL_OLINE_COLOR,
            stroke="#444444",
            stroke_width=0.05,
        )
    )

    root.append(diamond)

    # mask_g = su.new_sub_element(root, "g", mask="url(#letter_m_mask)")
    # mask_g.append(copy.deepcopy(diamond))

    for element in [elem_v, elem_im]:
        root.append(copy.deepcopy(element))

    _ = su.write_svg(output_path, root)
