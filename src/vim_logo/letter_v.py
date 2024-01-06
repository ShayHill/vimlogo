"""The giant letter V in the Vim logo.

There are small bevels at every 90-degree right turn (going clockwise). Ignoring
those for the moment, the letter is basically built like this.

a----------b     i----------j
|          |     |          |
o--n    d--c     h--g       k
   |    |           |      /
   |    |           f     /
   |    |          /     /
   |    |         /     /
   |    |        /     /
   |    |       /     /
   |    |      /     /
   |    |     /     /
   |    |    /     /
   |    |   /     /
   |    |* /     /
   |    | /     /
   |    e      /
   |          /
   |         /
   |        /
   |       /
   m------l

I've parameterized the letter as:
* overall width
* distance from a to b
* distance from b to c
* distance from c to d
* distance from l to m
* angle from e to f (and l to k)
* bevels on the xy plane (XY_BEVEL)

Bevels into the z plane (Z_BEVEL) are calculated from the XY_BEVEL such that at a
right corner A, B, C, the first bevel point will be collinear with BC and second
bevel point collinear with AB. The only way to decrease or increase these bevels is
to decrease or increase the XY_BEVEL. This was the main source of "cheating" in the
original vim.org logo.

To set that angle to exactly 45 degrees, I've had to widen the letter. In the
original e->f was 45 degrees, but l->k was not. This cheat allowed the letter to
remain in the original footprint. Removing the cheat means I need a shorter or wider
letter V.

The distance from f to g is set so that e->f and *->g are parallel. This is due to
the funny construction of the bevels.

After building this basic shape, I bevel the 90-degree right turns (at a, b, c, h, i,
j, m, and o) to get 23 points, starting with the ccw bevel point at point a. I then
offset all of these points to get a second set of 23 points which define a polygon
BEVEL distance outside the original polygon.

These bevels require some adjustment at points 8 and 9 (equivalent to points f and j,
neither of which are beveled). These bevel points are made identical and equal to the
intersection of bevel edges 7->8 (equivalent to e->f) and 9->10 (equivalent to g->h).

The final construction is a white polygon over the entire outer bevels, a gray
polygon over the letter itself, shaded polygons explicity defined for shaded bevels,
and a thin outline around the letter to hide the seams between the letter and shaded
polygons.
       
:author: Shay Hill
:created: 2024-01-03
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import svg_ultralight as su
import vec2_math as vec2
from vec2_math import _seg_to_ray as seg_to_ray  # type: ignore
from offset_poly import offset_polygon
from vim_logo import shared
import math

from vim_logo.diamond import (
    get_bevel_surface_normal,
)
from vim_logo.glyphs import new_data_string
from vim_logo.illumination import LightSource, Material, illuminate, set_material_color

if TYPE_CHECKING:
    from lxml.etree import _Element as EtreeElement  # type: ignore

# first point is the inside corner of the V then COUNTERCLOCKWISE


BEVEL_SLOPE = 4
XY_BEVEL = 2.5
TWO_VEC2 = tuple[tuple[float, float], tuple[float, float]]

# For a right-angle corner A, B, C, set bevel width so the first bevel point will be
# collinear with BC and second bevel point collinear with AB
Z_BEVEL = XY_BEVEL * math.sin(3 / 8 * math.pi) / math.sin(1 / 8 * math.pi)

V_WIDTH = 235
ABx = 88
BCy = 17
CDx = 16.5
LMx = BCy + XY_BEVEL
V_ANGLE = math.pi / 3.85

V_VECTOR = (-math.cos(V_ANGLE), math.sin(V_ANGLE))

MATERIAL = set_material_color(
    (0, 0, 1),
    Material(shared.VIM_GRAY, ambient=3, diffuse=7, specular=0.0, hue_shift=0.1),
    *shared.LIGHT_SOURCES,
)


def get_letter_v_rough_outline() -> list[tuple[float, float]]:
    # points along the top of the V serifs, left to right.
    pnt_a, pnt_b = (0, 0), (ABx, 0)
    pnt_i, pnt_j = (V_WIDTH - ABx, 0), (V_WIDTH, 0)

    # points on the lower outside corners of the V serifs, left to right.
    pnt_o, pnt_c, pnt_h, pnt_k = (
        vec2.vadd(p, (0, BCy)) for p in (pnt_a, pnt_b, pnt_i, pnt_j)
    )

    # raise pnt_k to be more like the vim.org logo, where pnt_k appears to be the top
    # point of what would have been an extension of the right, top serif.
    pnt_k = vec2.vsub(pnt_k, (0, XY_BEVEL))

    # points on the lower inside corners of the V serifs. There is no
    # suck point to the left of pnt_k.
    pnt_n, pnt_g = (vec2.vadd(p, (CDx, 0)) for p in (pnt_o, pnt_h))
    pnt_d = vec2.vadd(pnt_c, (-CDx, 0))

    pnt_f = vec2.vadd(pnt_g, (0, Z_BEVEL / math.sin(V_ANGLE)))

    # inside corner of the V
    pnt_e = get_ray_intersection((pnt_d, (0, 1)), (pnt_f, V_VECTOR))

    # bottom of the V
    bottom_pnt = get_ray_intersection((pnt_n, (0, 1)), (pnt_k, V_VECTOR))
    pnt_m = vec2.vsub(bottom_pnt, (0, LMx / math.sin(V_ANGLE)))
    pnt_l = vec2.vadd(pnt_m, (LMx, 0))

    return [
        pnt_a,
        pnt_b,
        pnt_c,
        pnt_d,
        pnt_e,
        pnt_f,
        pnt_g,
        pnt_h,
        pnt_i,
        pnt_j,
        pnt_k,
        pnt_l,
        pnt_m,
        pnt_n,
        pnt_o,
    ]


def get_ray_intersection(ray_a: TWO_VEC2, ray_b: TWO_VEC2) -> tuple[float, float]:
    """Get the intersection of two lines, each defined by a point and a vector."""
    pnt_a, vec_a = ray_a
    pnt_b, vec_b = ray_b
    line_a = vec2.get_standard_form((pnt_a, vec2.vadd(pnt_a, vec_a)))
    line_b = vec2.get_standard_form((pnt_b, vec2.vadd(pnt_b, vec_b)))
    xsect = vec2.get_line_intersection(line_a, line_b)
    if xsect is None:
        msg = "rays are parallel or coincident"
        raise ValueError(msg)
    return xsect


def get_abcd_intersection(seg_ab: TWO_VEC2, seg_cd: TWO_VEC2) -> tuple[float, float]:
    """Get the intersection of two lines, each defined by two points on the line.

    :param seg_ab: two points on the first line.
    :param seg_cd: two points on the second line.
    :return: the intersection point.
    """
    line_ab, line_cd = vec2.get_standard_form(seg_ab), vec2.get_standard_form(seg_cd)
    xsect = vec2.get_line_intersection(line_ab, line_cd)
    if xsect is None:
        msg = "rays are parallel or coincident"
        raise ValueError(msg)
    return xsect


def bevel_90_turns(pts: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Find any 90-degree turns in a list of points and replace them with a bevel."""
    new_pts: list[tuple[float, float]] = []
    for a, b, c in zip(pts[-1:] + pts[:-1], pts, pts[1:] + pts[:1]):
        vec_ba = vec2.set_norm(vec2.vsub(a, b), XY_BEVEL)
        vec_cb = vec2.set_norm(vec2.vsub(b, c), XY_BEVEL)
        angle = vec2.get_signed_angle(vec_ba, vec_cb)
        if math.isclose(angle, math.pi / 2):
            print(f"beveling {b}")
            new_pts.append(vec2.vadd(b, vec_ba))
            new_pts.append(vec2.vsub(b, vec_cb))
        else:
            new_pts.append(b)
    return new_pts


_letter_v_pts = get_letter_v_rough_outline()

_letter_v_pts = bevel_90_turns(_letter_v_pts)

_letter_v_pts = [vec2.vadd(pt, (36, 29)) for pt in _letter_v_pts]

inner = _letter_v_pts
outer = [x.xsect for x in offset_polygon(inner, -Z_BEVEL)]

outer[8] = outer[9] = get_abcd_intersection((outer[7], inner[9]), (outer[10], outer[9]))
# aaa = get_abcd_intersection((outer[7], inner[9]), (outer[10], outer[9]))


# _letter_v_pts = [
#     (0, 0),
#     (ABx, BCy),
#     ),

SHADE_GRAY = "#7f7f7f"

def _new_letter(name: str, *ptss: list[tuple[float, float]]) -> EtreeElement:
    """Create a `g` svg element for a small letter.

    :param name: id of the `g` element.
    :param ptss: list of lists of (x, y) points in a linear spline.
    :return: `g` svg element.
    """
    # skewed = [[_skew_point(pt) for pt in pts] for pts in ptss]
    skewed = ptss
    data_string = " ".join([new_data_string(pts) for pts in skewed])
    data_string_outer = new_data_string(outer)
    data_string_inner = new_data_string(inner)
    len_pts = len(inner)
    bevels: list[list[tuple[float, float]]] = []

    letter_v = su.new_element("g", id=name)
    for i in range(len_pts):
        bevels.append(
            [outer[i], outer[(i + 1) % len_pts], inner[(i + 1) % len_pts], inner[i]]
        )

    _ = su.new_sub_element(
        letter_v,
        "path",
        d=data_string_outer,
        fill="none",
        stroke=shared.FAT_STROKE_COLOR,
        stroke_width=shared.FAT_STROKE_WIDTH,
    )
    _ = su.new_sub_element(
        letter_v,
        "path",
        d=data_string_outer,
        fill="#ffffff",
    )
    # beg shading bevels
    shaded = [
       [*outer[3:8], *inner[2:8][::-1]],
       [*outer[9:11], *inner[9:12][::-1]],
       [*outer[15:19], *inner[14:21][::-1]],
       [*outer[20:22], *inner[20:23][::-1]],
    ]
    for polygon in shaded:
        _ = su.new_sub_element(
            letter_v,
            "path",
            d=new_data_string(polygon),
            fill=SHADE_GRAY,
            stroke=shared.PIN_STROKE_COLOR,
            stroke_width=shared.PIN_STROKE_WIDTH,
        )
    # end shading bevels
    _ = su.new_sub_element(
        letter_v,
        "path",
        d=data_string,
        fill=shared.VIM_GRAY,
        stroke=shared.PIN_STROKE_COLOR,
        stroke_width=shared.PIN_STROKE_WIDTH,
    )
    # for bevel in bevels[:8]:
    #     normal = get_bevel_surface_normal(bevel[0], bevel[1], BEVEL_SLOPE)
    #     _ = su.new_sub_element(
    #         letter_v,
    #         "path",
    #         d=new_data_string(bevel),
    #         fill=illuminate(normal, MATERIAL, *shared.LIGHT_SOURCES),
    #     )
    # for bevel in bevels:
    #     _ = su.new_sub_element(
    #         letter_v,
    #         "path",
    #         d=new_data_string(bevel),
    #         fill="none",
    #         stroke="#ff0000",  # shared.PIN_STROKE_COLOR,
    #         stroke_width=shared.PIN_STROKE_WIDTH,
    #     )

    # group = su.new_element("g", id=name)

    # outline = su.new_sub_element(group, "path", d=data_string)
    # _ = su.update_element(outline, stroke=_STROKE_COLOR, stroke_width=_STROKE_WIDTH)
    return letter_v


letter_v = _new_letter("letter_v", _letter_v_pts)
