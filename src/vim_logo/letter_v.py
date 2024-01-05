"""The giant letter V in the Vim logo.

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
unit = 5.6785

# first point is the inside corner of the V then COUNTERCLOCKWISE


# BEVEL_WIDTH = 6
BEVEL_SLOPE = 4
XY_BEVEL = 3
LINE_SEGMENT = tuple[tuple[float, float], tuple[float, float]]


BEVEL_WIDTH = XY_BEVEL * math.sin(3 / 8 * math.pi) / math.sin(1 / 8 * math.pi)

V_WIDTH = 235
# V_HEIGHT = 218.304693
V_TOP_SERIF_WIDTH = 88
V_TOP_SERIF_HEIGHT = 17
V_BOTTOM_SERIF_WIDTH = V_TOP_SERIF_HEIGHT + XY_BEVEL
V_SERIF_CUT = 25


VERTICAL_BAR_WIDTH = 55

ABx = V_TOP_SERIF_WIDTH
BCy = V_TOP_SERIF_HEIGHT
CDx = (V_TOP_SERIF_WIDTH - VERTICAL_BAR_WIDTH) / 2
FGy = BCy - XY_BEVEL * 2

V_ANGLE = math.pi / 3.925 / 1.5
V_VECTOR = (-math.sin(V_ANGLE), math.cos(V_ANGLE))

MATERIAL = set_material_color(
    (0, 0, 1),
    Material(shared.VIM_GRAY, ambient=3, diffuse=7, specular=0.0, hue_shift=0.1),
    *shared.LIGHT_SOURCES,
)

# YS = [0, V_TOP_SERIF_HEIGHT, V_TOP_SERIF_HEIGHT * 2 - XY_BEVEL * 2, V_HEIGHT, V_HEIGHT]


row_0 = [(0, 0), (V_TOP_SERIF_WIDTH, 0), (V_WIDTH - V_TOP_SERIF_WIDTH, 0), (V_WIDTH, 0)]
row_1: list[tuple[float, float]] = []
new_y = V_TOP_SERIF_HEIGHT
for i, (x, _) in enumerate(row_0):
    if i % 2 == 0:
        row_1.append((x, new_y))
        row_1.append((x + CDx, new_y))
    else:
        row_1.append((x - CDx, new_y))
        row_1.append((x, new_y))
row_1[-2:] = [vec2.vadd(row_1[-1], (0, -XY_BEVEL))]

row2_offset = BEVEL_WIDTH / (math.sin(V_ANGLE))
row_2 = [(row_1[5][0], row_1[5][1] + row2_offset)]

vec_de = vec2.get_standard_form((row_1[2], vec2.vadd(row_1[2], (0, 1))))
vec_fe = vec2.get_standard_form((row_2[0], vec2.vadd(row_2[0], V_VECTOR)))

row_3 = [vec2.get_line_intersection(vec_de, vec_fe)]

top_of_slant = vec2.vadd(row_1[-1], (0, XY_BEVEL))
vec_kl = vec2.get_standard_form((row_1[-1], vec2.vadd(row_1[-1], V_VECTOR)))
vec_nm = vec2.get_standard_form((row_1[1], vec2.vadd(row_1[1], (0, 1))))


def los(theta: float, n: float) -> float:
    """Use the law of signs to find how far to travel down the x axis to get n units up the y axis."""
    return n * math.sin(math.pi / 2 - theta) / math.sin(theta)


def get_ray_intersection(
    pnt_a: tuple[float, float],
    vec_a: tuple[float, float],
    pnt_b: tuple[float, float],
    vec_b: tuple[float, float],
) -> tuple[float, float]:
    """Get the intersection of two lines, each defined by a point and a vector."""
    line_a = vec2.get_standard_form((pnt_a, vec2.vadd(pnt_a, vec_a)))
    line_b = vec2.get_standard_form((pnt_b, vec2.vadd(pnt_b, vec_b)))
    xsect = vec2.get_line_intersection(line_a, line_b)
    if xsect is None:
        msg = "rays are parallel or coincident"
        raise ValueError(msg)
    return xsect


def get_abcd_intersection(
    seg_ab: LINE_SEGMENT, seg_cd: LINE_SEGMENT
) -> tuple[float, float]:
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


bottom_point = vec2.get_line_intersection(vec_kl, vec_nm)
point_m = vec2.vadd(bottom_point, (0, los(V_ANGLE, -V_BOTTOM_SERIF_WIDTH)))
vec_ml = vec2.get_standard_form((point_m, vec2.vadd(point_m, (1, 0))))
point_l = vec2.get_line_intersection(vec_ml, vec_kl)


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


_letter_v_pts = [
    row_0[0],
    row_0[1],
    row_1[3],
    row_1[2],
    row_3[0],
    row_2[0],
    row_1[5],
    row_1[4],
    row_0[2],
    row_0[3],
    row_1[6],
    point_l,
    point_m,
    row_1[1],
    row_1[0],
]

_letter_v_pts = bevel_90_turns(_letter_v_pts)

_letter_v_pts = [vec2.vadd(pt, (36, 29)) for pt in _letter_v_pts]

inner = _letter_v_pts
outer = [x.xsect for x in offset_polygon(inner, -BEVEL_WIDTH)]

outer[8] = outer[9] = get_abcd_intersection((outer[7], inner[9]), (outer[10], outer[9]))
# aaa = get_abcd_intersection((outer[7], inner[9]), (outer[10], outer[9]))


# _letter_v_pts = [
#     (0, 0),
#     (ABx, BCy),
#     ),

# (V_TOP_SERIF_WIDTH, YS[0]), (0, YS[1]), (-V_SERIF_CUT, YS[1]),


def _new_letter(name: str, *ptss: list[tuple[float, float]]) -> EtreeElement:
    """Create a `g` svg element for a small letter.

    :param name: id of the `g` element.
    :param ptss: list of lists of (x, y) points in a linear spline.
    :return: `g` svg element.
    """
    # skewed = [[_skew_point(pt) for pt in pts] for pts in ptss]
    skewed = ptss
    data_string = " ".join([new_data_string(pts) for pts in skewed])
    data_string_inner = new_data_string(outer)
    data_string_outer = new_data_string(inner)
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
        d=data_string_inner,
        fill="none",
        stroke=shared.FAT_STROKE_COLOR,
        stroke_width=shared.FAT_STROKE_WIDTH,
    )
    _ = su.new_sub_element(letter_v, "path", d=data_string, fill=shared.VIM_GRAY)
    for bevel in bevels[:8]:
        normal = get_bevel_surface_normal(bevel[0], bevel[1], BEVEL_SLOPE)
        _ = su.new_sub_element(
            letter_v,
            "path",
            d=new_data_string(bevel),
            fill=illuminate(normal, MATERIAL, *shared.LIGHT_SOURCES),
        )
    for bevel in bevels:
        _ = su.new_sub_element(
            letter_v,
            "path",
            d=new_data_string(bevel),
            fill="none",
            stroke="#ff0000",  # shared.PIN_STROKE_COLOR,
            stroke_width=shared.PIN_STROKE_WIDTH,
        )

    # group = su.new_element("g", id=name)

    # outline = su.new_sub_element(group, "path", d=data_string)
    # _ = su.update_element(outline, stroke=_STROKE_COLOR, stroke_width=_STROKE_WIDTH)
    return letter_v


letter_v = _new_letter("letter_v", _letter_v_pts)


_letter_v_pts = [
    (105.55717, 153.80024),
    (105.55717, 46.089297),
    (121.61576, 46.089297),
    (124.49467, 43.280707),
    (124.49467, 31.905707),
    (121.61576, 29.097107),
    (38.4556, 29.097107),
    (35.647, 31.905707),
    (35.647, 43.280707),
    (38.4556, 46.089297),
    (52.63919, 46.089297),
    (52.63919, 244.59321),
    (56.31108, 247.4018),
    (72.510285, 247.4018),
    (270.93998, 40.472107),
    (270.93998, 32.335387),
    (268.06108, 29.097107),
    (185.90873, 29.097107),
    (183.02983, 31.905707),
    (183.02983, 43.351017),
    (185.90873, 46.159607),
    (200.09233, 46.159607),
    (200.09233, 57.534607),
    (105.55717, 153.80024),
]


V_WIDTH = max(pt[0] for pt in _letter_v_pts) - min(pt[0] for pt in _letter_v_pts)
V_HEIGHT = max(pt[1] for pt in _letter_v_pts) - min(pt[1] for pt in _letter_v_pts)

print(f"width: {V_WIDTH}")
print(f"height: {V_HEIGHT}")

unit = 2.8
for a, b in zip(_letter_v_pts, _letter_v_pts[1:]):
    vx, vy = a
    dx, dy = vec2.vsub(a, b)
    print(f"{vx / unit:.4f}, {vy / unit:.4f}", end=" => ")
    print(f"{dx / unit:.4f}, {dy / unit:.4f}")
