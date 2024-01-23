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

import functools as ft
from typing import TYPE_CHECKING

import svg_ultralight as su
import vec2_math as vec2

from vim_logo import params_diamond as params
from vim_logo import shared, vec3
from vim_logo.glyphs import gap_polygon, get_polygon_union, new_data_string
from vim_logo.illumination import LIGHT_SOURCES, diamond_material, illuminate
from vim_logo.letters_im import letter_m_pts_mask

if TYPE_CHECKING:
    from lxml.etree import _Element as EtreeElement  # type: ignore

    from vim_logo.vec3 import Vec3


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


def _illuminate_bevel(pts: list[tuple[float, float]]) -> str:
    """Illuminate a bevel.

    :param pts: xy polygon points
    :return: hex color of the illuminated bevel
    """
    normal = _get_bevel_surface_normal(pts[0], pts[1], _BEVEL_SLOPE)
    return illuminate(normal, diamond_material, *LIGHT_SOURCES)


def _new_elem_diamond() -> EtreeElement:
    """Create a `g` element for the green diamond.

    :return: `g` element with `path` elements for the diamond outline, diamond face,
        and diamond bevels
    """
    face = _new_diamond_points(_ID / 2)
    face_d = _subtract_m(face)

    oline_d = _subtract_m(gap_polygon(diamond_outer, _STROKE_WIDTH))

    diamond = su.new_element("g", id_="diamond")
    add_path = ft.partial(su.new_sub_element, diamond, "path")
    _ = add_path(id_="diamond_outline", d=oline_d, fill=shared.K_STROKE)
    _ = add_path(id_="diamond_face", d=face_d, fill=shared.VIM_GREEN)

    for i in range(4):
        j = (i + 1) % 4
        bevel = [face[i], face[j], diamond_outer[j], diamond_outer[i]]
        bevel_d = _subtract_m(bevel)
        _ = add_path(
            id_=f"diamond_bevel_{i}",
            d=bevel_d,
            fill=_illuminate_bevel(bevel),
            **shared.PIN_STROKE,
        )
    return diamond


diamond = _new_elem_diamond()
