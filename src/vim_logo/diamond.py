"""The green diamond behind the letters.

:author: Shay Hill
:created: 2023-12-30
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import svg_ultralight as su
import vec2_math as vec2
from basic_colormath import hex_to_rgb, hsl_to_rgb, rgb_to_hex, rgb_to_hsl
from offset_poly import offset_polygon
from vim_logo import params_diamond as params

from vim_logo import shared, vec3
from vim_logo.glyphs import new_data_string
from vim_logo.illumination import (
    LIGHT_SOURCES,
    LightSource,
    Material,
    diamond_material,
    illuminate,
    set_material_color,
)
from vim_logo.letters_im import MED_STROKE_WIDTH
from vim_logo.reference_paths import (
    get_dims,
    ref_diamond_inner,
    ref_diamond_oline,
    ref_diamond_outer,
)

if TYPE_CHECKING:
    from lxml.etree import _Element as EtreeElement  # type: ignore

    from vim_logo.vec3 import Vec3

Vec2 = tuple[float, float]



_STROKE_COLOR = shared.MID_STROKE_COLOR
_BEVEL_SLOPE = params.BEVEL_SLOPE
_OD = params.OD
_ID = params.ID
_STROKE_WIDTH = params.STROKE_WIDTH

_DIAMOND_TRANS = "translate({} {})".format(*shared.VIEW_CENTER)


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


def _get_diamond_points(rad: float) -> list[tuple[float, float]]:
    """Four points of a diamond centered at the origin, clockwise from +x.

    :param rad: radius of the diamond (distance of each point from the origin)
    :return: [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]

    This is clockwise in a right-handed coordinate system, which looks unintuitive.
    """
    return [(rad, 0), (0, rad), (-rad, 0), (0, -rad)]


def _new_diamond() -> EtreeElement:
    """Return a diamond element."""
    outer = _get_diamond_points(_OD / 2)
    inner = _get_diamond_points(_ID / 2)

    bevels: list[list[Vec2]] = []
    for i in range(4):
        bevels.append([inner[i], inner[(i + 1) % 4], outer[(i + 1) % 4], outer[i]])
    diamond = su.new_element("g", id_="diamond", transform=_DIAMOND_TRANS)
    _ = su.new_sub_element(
        diamond,
        "path",
        id_="diamond_thick_outline",
        d=new_data_string(outer),
        fill="none",
        stroke=_STROKE_COLOR,
        stroke_width=_STROKE_WIDTH,
    )
    _ = su.new_sub_element(
        diamond,
        "path",
        id_="diamond_face",
        d=new_data_string(inner),
        fill=shared.VIM_GREEN
    )
    for i, bevel in enumerate(bevels):
        normal = _get_bevel_surface_normal(bevel[0], bevel[1], _BEVEL_SLOPE)
        _ = su.new_sub_element(
            diamond,
            "path",
            id_=f"diamond_bevel_{i}",
            d=new_data_string(bevel),
            fill=illuminate(normal, diamond_material, *LIGHT_SOURCES),
            **shared.PIN_STROKE,
        )
    return diamond


diamond = _new_diamond()
