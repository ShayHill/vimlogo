"""Construct the svg from parts.

:author: Shay Hill
:created: 2024-01-10
"""

import copy
import sys
from pathlib import Path

import svg_ultralight as su

from vim_logo import params_diamond, shared
from vim_logo.diamond import diamond, diamond_outer
from vim_logo.glyphs import gap_polygon, get_polygon_union, new_data_string
from vim_logo.letter_v import V_STROKE_WIDTH, elem_v, v_outer
from vim_logo.letters_im import (
    IM_STROKE_WIDTH,
    elem_im,
    letter_m_pts,
    letter_m_pts_mask,
)
from vim_logo.paths import OUTPUT


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

    for element in [elem_v, elem_im]:
        root.append(copy.deepcopy(element))

    _ = sys.stdout.write("Writing svg to " + str(output_path) + "\n")
    _ = su.write_svg(output_path, root)


if __name__ == "__main__":
    write_vim_logo()
