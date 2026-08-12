"""The green diamond behind the letters.

Simple diamonds, but the inner diamond and at least one of the bevels will have the
letter_m_mask removed from them, so the diamond and some bevels will have more than
four points.

The reference SVG accomplished the same thing with overlaying white polygons, but
there were a lot of mistakes. This is (arguably, because there's also masking) the
right way to do it.

:author: Shay Hill
:created: 2023-12-30
"""

from typing import NamedTuple

import vec2_math as vec2
from basic_colormath import rgb_to_hex

from vimlogo import params_diamond as params
from vimlogo import shared
from vimlogo.glyphs import gap_polygon, get_polygon_union
from vimlogo.gooch_shading import Material
from vimlogo.letters_im import letter_m_mask
from vimlogo.params_diamond import LIGHT_LOCATION


def _new_diamond_points(rad: float) -> list[tuple[float, float]]:
    """Four points of a diamond centered at the origin, clockwise from -x.

    :param rad: radius of the diamond (distance of each point from the origin)
    :return: [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]

    This is clockwise in a right-handed coordinate system, which looks unintuitive.
    """
    at_origin = [(-rad, 0), (0, -rad), (rad, 0), (0, rad)]
    return [vec2.vadd(pnt, shared.VIEW_CENTER) for pnt in at_origin]


# this value is used elsewhere to build the background
diamond_outer = _new_diamond_points(params.OD / 2)


diamond_material = Material(
    base=params.DIAMOND_MATERIAL_BASE,
    cool=params.DIAMOND_MATERIAL_COOL,
    warm=params.DIAMOND_MATERIAL_WARM,
    cool_color_ratio=params.DIAMOND_MATERIAL_COOL_COLOR_RATIO,
    warm_color_ratio=params.DIAMOND_MATERIAL_WARM_COLOR_RATIO,
    cool_lum_scalar=params.DIAMOND_MATERIAL_COOL_LUM_SCALAR,
    warm_lum_scalar=params.DIAMOND_MATERIAL_WARM_LUM_SCALAR
)

diamond_shader = diamond_material.new_shader(LIGHT_LOCATION)


def illuminate_bevel(pts: list[tuple[float, float]]) -> str:
    """Illuminate a bevel.

    :param pts: xy polygon points
    :return: hex color of the illuminated bevel
    """
    normal_x, normal_y = vec2.qrotate(vec2.vsub(pts[0], pts[1]), 1)
    normal = (normal_x, normal_y, 0)
    return rgb_to_hex(diamond_shader(normal))


class Diamond(NamedTuple):
    """Control points for the diamond."""

    ol: list[tuple[float, float]]
    face: list[tuple[float, float]]
    q1: list[tuple[float, float]]
    q2: list[tuple[float, float]]
    q3: list[tuple[float, float]]
    q4: list[tuple[float, float]]


def _new_diamond() -> Diamond:
    """Get the control points for the diamond.

    :return: [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
    """
    outline = get_polygon_union(
        gap_polygon(diamond_outer, params.STROKE_WIDTH),
        letter_m_mask,
        negative={1},
        # gap_polygon(diamond_outer, 0), letter_m_mask, negative={1}
    )
    face = _new_diamond_points(params.ID / 2)
    bevels: list[list[tuple[float, float]]] = []
    for i in range(4):
        j = (i + 1) % 4
        bevels.append([face[j], face[i], diamond_outer[i], diamond_outer[j]])
    sw = shared.PIN_STROKE_WIDTH / 2
    return Diamond(
        ol=outline[0],
        face=gap_polygon(_new_diamond_points(params.ID / 2), -sw),
        q1=gap_polygon(bevels[1], -sw),
        q2=gap_polygon(bevels[0], -sw),
        q3=gap_polygon(bevels[3], -sw),
        q4=gap_polygon(bevels[2], -sw),
    )


diamond_cpts = _new_diamond()
