"""The green diamond behind the letters.

:author: Shay Hill
:created: 2023-12-30
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import svg_ultralight as su
import vec2_math as vec2
from offset_poly import offset_polygon

from vim_logo import vec3
from vim_logo.glyphs import new_data_string
from vim_logo.illumination import LightSource, Material, illuminate, set_material_color
from vim_logo import shared


from basic_colormath import rgb_to_hsl, hsl_to_rgb, rgb_to_hex, hex_to_rgb

if TYPE_CHECKING:
    from lxml.etree import _Element as EtreeElement  # type: ignore

    from vim_logo.vec3 import Vec3

Vec2 = tuple[float, float]

Z_BEVEL = 3 * 2
BEVEL_SLOPE = 8


def _push_hsl(color: str, hue_shift: float=0, sat_shift: float=0, lit_shift: float=0) -> str:
    """Shift the hue, saturation, and lightness of a color.

    :param color: hex color str, e.g., "#ff3322"
    :param hue_shift: -365 to 365, maximum amount to change hue
    :param sat_shift: -100 to 100, maximum amount to change saturation
    :param lit_shift: -100 to 100, maximum amount to change lightness
    :return: (r, g, b)

    The intermediate hue, sat, and lit values are in the ranges
    [0, 365), [0, 100], and [0, 100].
    """
    hue, sat, lit = rgb_to_hsl(hex_to_rgb(color))
    hue = (hue + hue_shift) % 365
    sat = max(0, min(100, sat + sat_shift))
    lit = max(0, min(100, lit + lit_shift))
    return rgb_to_hex(hsl_to_rgb((hue, sat, lit)))

MATERIAL = set_material_color(
    (0, 0, 1),
    Material(
        _push_hsl(shared.VIM_GREEN, hue_shift=1, sat_shift=-20, lit_shift=4),
        ambient=3.5,
        diffuse=6,
        specular=.5,
        hue_shift=0.0,
        sat_shift=0,
    ),
    *shared.LIGHT_SOURCES_WHITE,
)


def _get_bevel_surface_normal(
    pnt_a2: tuple[float, float], pnt_b2: tuple[float, float], slope: float
) -> Vec3:
    """Calculate the surface normal of a bevel.

    :param pnt_a2: one point on the inside edge of the bevel (xy plane)
    :param pnt_b2: point clockwise from pnt_a on the inside edge of the bevel
        (xy plane)
    :param slope: slope of the bevel. This will be usually be negative, because pnt_a
        and pnt_b will be on the inside edge (which is usually higher).

    This is different from most modelling code I've done, because faces in the Vim
    logo are defined a) clockwise and b) in a right-handed coordinate system. I
    usually do the opposite, but I've kept the Vim convention this time.
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


def _new_diamond(rad: float) -> EtreeElement:
    """Return a diamond element."""
    outer = _get_diamond_points(rad)
    inner = [x.xsect for x in offset_polygon(outer, Z_BEVEL)]
    bevels: list[list[Vec2]] = []
    for i in range(4):
        bevels.append([inner[i], inner[(i + 1) % 4], outer[(i + 1) % 4], outer[i]])
    diamond = su.new_element("g")
    _ = su.new_sub_element(
        diamond, "path", d=new_data_string(outer), fill="none", **shared.MID_STROKE
    )
    _ = su.new_sub_element(
        diamond, "path", d=new_data_string(inner), fill=shared.VIM_GREEN
        # diamond, "path", d=new_data_string(inner), fill=illuminate((0, 0, 1), MATERIAL, *shared.LIGHT_SOURCES),

    )
    for bevel in bevels:
        normal = _get_bevel_surface_normal(bevel[0], bevel[1], BEVEL_SLOPE)
        _ = su.new_sub_element(
            diamond,
            "path",
            d=new_data_string(bevel),
            fill=illuminate(normal, MATERIAL, *shared.LIGHT_SOURCES),
        )
    for bevel in bevels:
        _ = su.new_sub_element(
            diamond, "path", d=new_data_string(bevel), fill="none", **shared.PIN_STROKE
        )
    return diamond


diamond = _new_diamond(71 * 1.9)
