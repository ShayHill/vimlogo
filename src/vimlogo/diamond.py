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

from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

import vec2_math as vec2

from vimlogo import params_diamond as params
from vimlogo import shared, vec3
from vimlogo.glyphs import gap_polygon, get_polygon_union
from vimlogo.illumination import LIGHT_SOURCES, diamond_material, illuminate
from vimlogo.letters_im import letter_m_mask

if TYPE_CHECKING:
    from vimlogo.vec3 import Vec3


_BEVEL_SLOPE = params.BEVEL_SLOPE
_OD = params.OD
_ID = params.ID
_STROKE_WIDTH = params.STROKE_WIDTH


def _get_bevel_surface_normal(
    pnt_a2: tuple[float, float], pnt_b2: tuple[float, float], slope: float
) -> Vec3:
    """Calculate the surface normal of a bevel.

    :param pnt_a2: one point on the inside edge of the bevel (xy plane)
    :param pnt_b2: point clockwise from pnt_a on the inside edge of the bevel
        (xy plane)
    :param slope: slope of the bevel. This is the slope of the bevels from outside
        in, so a positive number.

    Faces are defined clockwise in a right-handed coordinate system.
    """
    vec_ab2 = vec2.vsub(pnt_a2, pnt_b2)
    vec_ac2 = vec2.set_norm(vec2.qrotate(vec_ab2, 3))
    pnt_c_xy = vec2.vadd(pnt_a2, vec_ac2)

    pnt_a3 = (*pnt_a2, 0)
    pnt_c3 = (*pnt_c_xy, slope)
    vec_ab3 = (*vec_ab2, 0)
    vec_ac3 = vec3.normalize(vec3.subtract(pnt_c3, pnt_a3))

    return vec3.normalize(vec3.cross(vec_ac3, vec_ab3))


def _new_diamond_points(rad: float) -> list[tuple[float, float]]:
    """Four points of a diamond centered at the origin, clockwise from -x.

    :param rad: radius of the diamond (distance of each point from the origin)
    :return: [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]

    This is clockwise in a right-handed coordinate system, which looks unintuitive.
    """
    at_origin = [(-rad, 0), (0, -rad), (rad, 0), (0, rad)]
    return [vec2.vadd(pnt, shared.VIEW_CENTER) for pnt in at_origin]


# this value is used elsewhere to build the background
diamond_outer = _new_diamond_points(_OD / 2)


def _subtract_m(pts: list[tuple[float, float]]) -> str:
    """Subtract the letter_m_mask from a polygon.

    :param pts: xy polygon points
    :return: path data string with the letter_m_mask subtracted from it
    """
    paths = get_polygon_union(pts, letter_m_pts_mask, negative={1})
    return new_data_string(*paths)


def illuminate_bevel(pts: list[tuple[float, float]]) -> str:
    """Illuminate a bevel.

    :param pts: xy polygon points
    :return: hex color of the illuminated bevel
    """
    normal = _get_bevel_surface_normal(pts[1], pts[0], _BEVEL_SLOPE)
    return illuminate(normal, diamond_material, *LIGHT_SOURCES)


class Diamond(NamedTuple):
    """Control points for the diamond."""

    ol: list[tuple[float, float]]
    face: list[tuple[float, float]]
    q1: list[tuple[float, float]]
    q2: list[tuple[float, float]]
    q3: list[tuple[float, float]]
    q4: list[tuple[float, float]]


def new_cpts_diamond() -> Diamond:
    """Get the control points for the diamond.

    :return: [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
    """
    outline = get_polygon_union(
        gap_polygon(diamond_outer, _STROKE_WIDTH), letter_m_mask, negative={1}
    )
    face = _new_diamond_points(_ID / 2)
    bevels: list[list[tuple[float, float]]] = []
    for i in range(4):
        j = (i + 1) % 4
        bevels.append([face[j], face[i], diamond_outer[i], diamond_outer[j]])
    sw = shared.PIN_STROKE_WIDTH / 2
    return Diamond(
        ol=outline[0],
        face=gap_polygon(_new_diamond_points(_ID / 2), -sw),
        q1=gap_polygon(bevels[1], -sw),
        q2=gap_polygon(bevels[0], -sw),
        q3=gap_polygon(bevels[3], -sw),
        q4=gap_polygon(bevels[2], -sw),
    )


diamond_cpts = new_cpts_diamond()
