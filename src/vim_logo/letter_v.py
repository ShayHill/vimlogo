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
* overall height
* distance from a to b
* distance from b to c
* distance from c to d
* distance from l to m
* bevels on the xy plane (XY_BEVEL)

Bevels into the z plane (Z_BEVEL) are calculated from the XY_BEVEL such that at a
right corner A, B, C, the first bevel point will be collinear with BC and second
bevel point collinear with AB. The only way to decrease or increase these bevels is
to decrease or increase the XY_BEVEL. This was the main source of "cheating" in the
original vim.org logo.

The angle will end up near to, but not exactly at 45 degrees. This is required to
match the width and height of the vim.org logo. In the original,  e->f was 45
degrees, but l->k was not. This cheat allowed the letter to remain in the original
footprint. Removing the cheat means I need to slightly adjust the angle.

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
from offset_poly import offset_polygon, offset_poly_per_edge
from offset_poly.offset import PolyType

from vim_logo import shared
from vim_logo.glyphs import new_data_string, gap_polygon
from vim_logo.reference_paths import (
    ref_v,
    get_dims,
    ref_v_oline,
    ref_v_bevels,
    ref_view_center,
    ref_v_dim_bevels,
    ref_v_lit_bevels,
    start_from_first_lexigraphically_sorted_point,
)
from vim_logo.glyphs import get_polygon_union


if TYPE_CHECKING:
    from lxml.etree import _Element as EtreeElement  # type: ignore

TWO_VEC2 = tuple[tuple[float, float], tuple[float, float]]


# ===============================================================================
#   dimensions and parameters hand-tuned
# ===============================================================================

# The small bevels on the xy plane. The larger bevels size is a function of this in
# order to make the impossible bevels with the correct angles.
XY_BEVEL = 2.5

# For a right-angle corner A, B, C, set bevel width so the first bevel point will be
# collinear with BC and second bevel point collinear with AB. This z bevel is only
# used for serifs and the bottom of the V.
Z_BEVEL = XY_BEVEL * math.sin(3 / 8 * math.pi) / math.sin(1 / 8 * math.pi)

# z bevels for outsides of the V strokes
Z_BEVEL_MID = Z_BEVEL + XY_BEVEL / 2

# z bevels for insides of the V strokes
Z_BEVEL_FAT = Z_BEVEL + XY_BEVEL

# ===============================================================================
#   dimensions and parameters inferred from reference image
# ===============================================================================

# reference width and height of the face of the letter V
V_WIDTH, V_HEIGHT = get_dims(ref_v)

V_STROKE_WIDTH = (get_dims(ref_v_oline)[0] - get_dims(ref_v_bevels)[0]) / 2

_left_serif = ref_v[-3:] + ref_v[:7]
_right_serif = ref_v[9:17]
_bot_flat = ref_v[17:20]

# average width of the top serifs
ABx = (get_dims(_left_serif)[0] + get_dims(_right_serif)[0]) / 2

# average the height of the top serifs
BCy = (get_dims(_left_serif)[1] + get_dims(_right_serif)[1]) / 2

# average distance between serif sides and v strokes. The wider overhang on the right
# side of the top, left serif is ignored, as the character of the original is much
# better captured with the proportions of the left sides of the top serifs.
CDx = (get_dims(_left_serif[:3])[0] + get_dims(_right_serif[:3])[0]) / 2

# the flat bottom of the V
LMx = get_dims(_bot_flat)[0]

# the height of the short side of the right serif of the V
JKy = get_dims(ref_v[14:17])[1]


import math
from typing import Iterator


def get_vecs(pts: list[tuple[float, float]]) -> Iterator[tuple[float, float]]:
    for a, b in zip(pts, pts[1:] + pts[:1]):
        yield vec2.vsub(b, a)


def get_slopes(pts: list[tuple[float, float]]) -> Iterator[float]:
    for vec in get_vecs(pts):
        if vec[0] == 0:
            yield math.inf
        else:
            yield vec[1] / vec[0]


def get_norms(pts: list[tuple[float, float]]) -> Iterator[float]:
    for vec in get_vecs(pts):
        yield vec2.get_norm(vec)


def get_two(
    pts: list[tuple[float, float]], *ixs: int
) -> Iterator[tuple[tuple[float, float], tuple[float, float]]]:
    for i, j in zip(ixs, ixs[1:]):
        yield pts[i], pts[j]


def _get_seg_gap(seg_a: TWO_VEC2, seg_b: TWO_VEC2) -> float:
    """Get the gap between two line segments.

    :param seg_a: the first line segment.
    :param seg_b: the second line segment.
    :return: the gap between the two segments.
    """
    line_a = vec2.get_standard_form(seg_a)
    gaps = [vec2.get_line_point_distance(line_a, x) for x in seg_b]
    return sum(gaps) / 2


ref_outer = [
    *get_two(ref_v_dim_bevels[0], 2, 3),
    *get_two(ref_v_lit_bevels[0], 0, 1, 2, 3, 4, 5),
    *get_two(ref_v_dim_bevels[1], 7, 8, 9, 0, 1),
    *get_two(ref_v_lit_bevels[2], 4, 0),
    *get_two(ref_v_dim_bevels[3], 2, 3),
    *get_two(ref_v_lit_bevels[3], 0, 1, 2, 3, 4, 5),
    *get_two(ref_v_dim_bevels[2], 7, 0, 1, 2),
    *get_two(ref_v_lit_bevels[1], 0, 1, 2),
]

ref_outer = start_from_first_lexigraphically_sorted_point([x[0] for x in ref_outer])


def _get_x_intercept(abc: tuple[float, float, float], y: float) -> tuple[float, float]:
    """Get the x intercept of a line defined by a, b, and c, at a given y value."""
    a, b, c = abc
    x = (-b * y - c) / a
    return x, y


def _get_y_intercept(abc: tuple[float, float, float], x: float) -> tuple[float, float]:
    """Get the y intercept of a line defined by a, b, and c, at a given x value."""
    a, b, c = abc
    y = (-a * x - c) / b
    return x, y


AAA = list(get_vecs(ref_v))
aaa = list(get_vecs(ref_outer))
bbb = list(get_slopes(ref_v))
ccc = list(get_norms(ref_outer))

itlc = (ref_v[0][0], ref_v[1][1])
otlc = (ref_outer[0][0], ref_outer[1][1])

irel = [vec2.vsub(x, itlc) for x in ref_v]
orel = [vec2.vsub(x, otlc) for x in ref_outer]

irel2 = [vec2.vsub(x, otlc) for x in ref_v]
orel2 = [vec2.vsub(x, itlc) for x in ref_outer]


from vim_logo.reference_paths import _get_bounds as gb


# outer_pts = [x for x in ref_v_bevels if x not in ref_v]


pts = ref_v

scored = []
for i in range(40, 41):
    # unit = abs(pts[0][1]) / i
    relative = [vec2.vsub(x, pts[0]) for x in pts]
    unit = abs(relative[1][1]) / i
    scaled_x = (x[1] / unit for x in relative)
    error = sum(abs(round(x) - x) for x in scaled_x)
    scaled = [f"{x[0]/unit:.2f},{x[1]/unit:.2f}" for x in relative]
    scaled = [f"{x[1]/unit:.2f}" for x in relative]
    scored.append((error, i))
scored.sort()


gaps = []
for i in range(len(ref_outer)):
    seg_a = ref_outer[i], ref_outer[(i + 1) % len(ref_outer)]
    if i < 8:
        j = i
    else:
        j = i + 1
    seg_b = ref_v[j], ref_v[(j + 1) % len(ref_v)]
    gaps.append(_get_seg_gap(seg_a, seg_b))


def _get_ray_intersection(ray_a: TWO_VEC2, ray_b: TWO_VEC2) -> tuple[float, float]:
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


def _get_abcd_intersection(seg_ab: TWO_VEC2, seg_cd: TWO_VEC2) -> tuple[float, float]:
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


sml_bev = 2 + 13 / 16
lrg_bev_old = (BCy - 2 * sml_bev) / 2
lrg_bev = sml_bev * math.sin(3 / 8 * math.pi) / math.sin(1 / 8 * math.pi)
lrg_bev = 5 + 10 / 16
lrg_bev = 8 * math.sin(1 / 4 * math.pi)
sml_bev = lrg_bev * math.sin(1 / 8 * math.pi) / math.sin(3 / 8 * math.pi)


ABx = 100 - lrg_bev * 2
BCy = 17
CDx = 19

BARx = ABx - BCy - CDx


def _get_letter_v_rough_outline() -> list[tuple[float, float]]:
    """Plot the rough outline of the letter V, starting from top left then clockwise."""

    # points along the top of the V serifs, left to right.
    pnt_a, pnt_b = (0, 0), (ABx, 0)
    pnt_i, pnt_j = (V_WIDTH - ABx, 0), (V_WIDTH, 0)

    # points on the lower outside corners of the V serifs, left to right.
    pnt_o, pnt_c, pnt_h = (vec2.vadd(p, (0, BCy)) for p in (pnt_a, pnt_b, pnt_i))

    # points on the lower inside corners of the V serifs. There is no
    # such point to the left of pnt_k.
    pnt_n, pnt_g = (vec2.vadd(p, (CDx, 0)) for p in (pnt_o, pnt_h))
    pnt_d = vec2.vadd(pnt_c, (-CDx, 0))

    # point k is a little higher than the others to make the right side of the V a
    # bit pointier.
    pnt_k = vec2.vadd(pnt_j, (0, JKy))

    # points on the bottom of the V, left to right.
    pnt_m = (CDx, V_HEIGHT)
    pnt_l = (CDx + LMx, V_HEIGHT)

    # infer the angle of the letter V from the existing points. The remaining points
    # will be calculated from this angle.
    v_right_leg_vector = vec2.vsub(pnt_k, pnt_l)
    v_angle = vec2.get_signed_angle((0, -1), v_right_leg_vector)

    pnt_f = vec2.vadd(pnt_g, (0, Z_BEVEL_FAT / math.sin(v_angle)))

    # inside corner of the V
    pnt_e = _get_ray_intersection((pnt_d, (0, 1)), (pnt_f, v_right_leg_vector))

    # fmt: off
    return [
        pnt_a, pnt_b, pnt_c, pnt_d, pnt_e, pnt_f, pnt_g, pnt_h,
        pnt_i, pnt_j, pnt_k, pnt_l, pnt_m, pnt_n, pnt_o
    ]
    # fmt: on




def _translate_line(
    abc: tuple[float, float, float], vec: tuple[float, float]
) -> tuple[float, float, float]:
    """Translate a line defined by a, b, and c by a vector."""
    a, b, c = abc
    x, y = vec
    c -= a * x + b * y
    return a, b, c


# the outer width of the left, top serif of the V.
# Justification: In the reference SVG, the outer left is 100.14235 units wide. Going
# with 100.15625 because it is an integer when multiplied by 96, which seems to be a
# trend with other numbers in the reference SVG.
OUTER_AB = 9615 / 96  # 100.15625


# the outer height of the left, top serif of the V.
# Justification: In the reference SVG, 28.4375 appears twice. This is the outside
# height of the left, top serif of the V AND the distance between the inner top of
# the right serif and the top of the innder right diagonal of the V (the vertical
# distance between inner points F and I. For what it's worth, 28.4375 * 96 (ppi of
# the reference SVG) is an integer: 2730.
OUTER_BC = 2730 / 96  # 28.4375


# the inner height of the left, top serif of the V.
# Justification: In the reference SVG, the inner, left serif is 16.99219 units tall.
# The right is 17.0625. 17.0625 * 96 is also an integer (1638), so I'm going with
# that. This will set both the inner and outer bevels.
INNER_BC = 1638 / 96  # 17.0625


# the inner horizontal line on the bottom right of the top-left serif of the V.
# Justification: Once again, the exact measurement in the file is an integer when
# multiplied by 96. That's too nice of a coincidence.
INNER_CD = 1818 / 96  # 18.9375


# the outer horizontal line on the bottom right of the top-left serif of the V.
# Justification: This is an important measurement because it sets (along with
# OUTER_DE) the width and height of the V. I cannot find a justification for the
# measured value in the reference SVG: 14.11328. This is that value rounded to the
# nearest 96th. Other points in the reference are even 96ths relative to this value.
# I don't know where this value came from. It is close to INNER_BC-LRG_BEV/2.
OUTER_CD = 1355 / 96  # 14.114583333333334


# the outer vertical line on the inside of the V.
# Justification: The left serif is pretty consistent, but there are few clues as to
# how the original designer might have selected an overall width and height for the
# letter V. I looked for a measurement that would be an integer when multiplied by
# 96, and this is what I found. The y value between the top of the inner left serif
# and the outer E point is 102.09375, which is 9801 / 96.
OUTER_DE = 9801 / 96 - INNER_CD - (OUTER_BC - INNER_BC) / 2  # 83.15625

BEV_NM = 636 / 96 # 6.625

INNER_LM = 22588 / 96 - INNER_BC

LRG_BEV = (OUTER_BC - INNER_BC) / 2
SML_BEV = LRG_BEV * math.sin(3 / 8 * math.pi) / math.sin(1 / 8 * math.pi)
INNER_AB = OUTER_AB - LRG_BEV * 2

# the x value of the left and right sides of the right serif of the V.
# Justification: Snapped to nearest 96th.
INNER_Hx = 14149 / 96 
INNER_Jx = 22588 / 96
INNER_Lx = 3539 / 96
INNER_Ly = 20957 / 96

OUTER_Dx = OUTER_AB - OUTER_CD - LRG_BEV
INNER_Dx = INNER_AB - INNER_CD

INNER_FG = OUTER_BC - INNER_BC







def get_rough3():
    pnt_a = (0, 0)
    pnt_b = (INNER_AB, 0)
    pnt_c = (INNER_AB, INNER_BC)
    pnt_d = vec2.vadd(pnt_c, (-INNER_CD, 0))

    pnt_fx = INNER_Hx + INNER_BC
    pnt_e = vec2.vadd(pnt_d, (0, pnt_fx - pnt_d[0] + 2 * LRG_BEV))
    pnt_f = (pnt_fx, OUTER_BC)
    pnt_g = (pnt_fx, INNER_BC)
    pnt_h = (INNER_Hx, INNER_BC)
    pnt_i = (INNER_Hx, 0)
    pnt_j = (INNER_Jx, 0)
    pnt_k = (INNER_Jx, INNER_FG)

    vec_kl = _translate_line((-1, -1, 0), pnt_k)
    pnt_l = _get_y_intercept(vec_kl, INNER_Lx)
    pnt_l = (INNER_Lx, INNER_Ly)
    pnt_m = (INNER_BC, pnt_l[1])
    pnt_n = (INNER_BC, INNER_BC)
    pnt_o = (0, INNER_BC)

    return [pnt_a, pnt_b, pnt_c, pnt_d, pnt_e, pnt_f, pnt_g, pnt_h, pnt_i, pnt_j, pnt_k, pnt_l, pnt_m, pnt_n, pnt_o]








# ===============================================================================
#   Values calculated from the above measurements.
# ===============================================================================

LRG_BEV = (OUTER_BC - INNER_BC) / 2

# the bevels on the inside face of the V. These are only about 85% of the width of
# the reference-image bevels. There are only two ways to get the "impossible" bevel
# shading to work: 1) define the small bevels relative to the large bevels at exactly
# this ratio, or 2) use "graph paper bevels" only on the right-hand, 90-degree turns.
# Graph-paper bevels are bevels that are not the same distance from the inner 
SML_BEV = lrg_bev * math.sin(1 / 8 * math.pi) / math.sin(3 / 8 * math.pi)


def rel_to(abs: list[tuple[float, float]], pnt: tuple[float, float]) -> list[tuple[float, float]]:
    """Convert a list of absolute points to relative points."""
    rel = []
    for abs_pnt in abs:
        rel.append(vec2.vsub(abs_pnt, pnt))
    return rel




def _get_letter_v_rough_outline() -> list[tuple[float, float]]:
    bottom = get_dims(ref_v)[1]
    v_slope = 1.04
    pnt_a = (0, 0)
    pnt_b = (ABx, 0)
    pnt_c = vec2.vadd(pnt_b, (0, BCy))
    pnt_d = vec2.vadd(pnt_c, (-CDx, 0))
    pnt_e = vec2.vadd(pnt_d, (0, BARx * 2))
    pnt_fy = BCy + 11.375  # + 17 - 2 * sml_bev
    lin_ef = vec2.get_standard_form((pnt_e, vec2.vadd(pnt_e, (1, -1))))
    pnt_f = _get_x_intercept(lin_ef, pnt_fy)
    lin_kl = _translate_line(lin_ef, (53 + 8.5, 0))

    ref_f_br = vec2.get_standard_form(ref_v[16:18])
    aaa = vec2.get_line_point_distance(ref_f_br, ref_v[7])
    bbb = vec2.get_line_point_distance(ref_f_br, ref_v[8])

    # pnt_fx = pnt_e[0] + (pnt_e[1] - pnt_fy)

    # pnt_f = (pnt_fx, pnt_fy)
    pnt_g = (pnt_f[0], BCy)
    pnt_h = (pnt_g[0] - BCy, pnt_g[1])

    pnt_ky = BCy + sml_bev  # - 2 * sml_bev
    # pnt_ky = BCy - 2 * sml_bev
    pnt_i = (pnt_h[0], 0)
    pnt_j = (pnt_h[0] + ABx - 1, 0)
    pnt_k = (pnt_j[0], BCy - 2 * sml_bev)
    pnt_k = _get_x_intercept(lin_kl, pnt_ky)
    pnt_j = (pnt_k[0], 0)

    pnt_k = (pnt_k[0], BCy - 2 * sml_bev)
    # pnt_lx = BCy + sml_bev + BCy - sml_bev
    # pnt_ly = pnt_k[1] + (pnt_k[0] - pnt_lx)
    # pnt_l = (pnt_lx, pnt_ly)
    pnt_lx = BCy * 2 + sml_bev
    pnt_l = _get_y_intercept(lin_kl, pnt_lx)
    pnt_m = (BCy, pnt_l[1])
    # pnt_l = (BCy * 2 + sml_bev, bottom)
    # pnt_m = (BCy, pnt_l[1])
    pnt_n = (pnt_m[0], BCy)
    pnt_o = (0, pnt_n[1])

    pts = [
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

    vecs = [vec2.vsub(b, a) for a, b in zip(pts, pts[1:] + pts[-1:])]
    # slopes = [float("inf") if x is 0 else y / x for x, y in vecs]
    slopes = []
    for vec in vecs:
        if vec[0] == 0:
            slopes.append(float("inf"))
        else:
            slopes.append(vec[1] / vec[0])

    # vec_lk = vec2.vsub(pnt_k, pnt_l)
    # slope = abs(vec_lk[1] / vec_lk[0])
    # pnt_e_x = pnt_d[0]
    # pnt_e_y = pnt_f[1] + (pnt_f[0] - pnt_e_x) * slope
    # pnt_e = (pnt_e_x, pnt_e_y)
    # fmt: off
    return [
        pnt_a, pnt_b, pnt_c, pnt_d, pnt_e, pnt_f, pnt_g, pnt_h,
        pnt_i, pnt_j, pnt_k, pnt_l, pnt_m, pnt_n, pnt_o
    ]
    # fmt: on


def _bevel_90_turns(pts: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Find any 90-degree turns in a list of points and replace them with a bevel."""
    new_pts: list[tuple[float, float]] = []
    for a, b, c in zip(pts[-1:] + pts[:-1], pts, pts[1:] + pts[:1]):
        vec_ba = vec2.set_norm(vec2.vsub(a, b), sml_bev)
        vec_cb = vec2.set_norm(vec2.vsub(b, c), sml_bev)
        angle = vec2.get_signed_angle(vec_ba, vec_cb)
        if math.isclose(angle, math.pi / 2):
            new_pts.append(vec2.vadd(b, vec_ba))
            new_pts.append(vec2.vsub(b, vec_cb))
        else:
            new_pts.append(b)
    return new_pts


def _bevel_and_refine_letter_v_outline(
    pts: list[tuple[float, float]]
) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    """Refine the letter V outline to match the vim.org logo."""
    v_angle = vec2.get_signed_angle((0, 1), vec2.vsub(pts[4], pts[5]))
    norm_56 = vec2.get_norm(vec2.vsub(pts[5], pts[6]))

    lin_kl = vec2.get_standard_form((pts[10], pts[11]))
    outer_k = vec2.vadd(pts[9], (lrg_bev, INNER_BC))

    # norm

    pts = _bevel_90_turns(pts)
    inner = pts
    # outer = [x.xsect for x in offset_polygon(inner, -Z_BEVEL)]
    bevels = [-lrg_bev] * (len(inner) - 1)

    # for i in (7, 8):
    #     bevels[i] = -Z_BEVEL_FAT

    bevels[6] = INNER_Dx - OUTER_Dx
    bevels[7] = -INNER_FG * math.sin(math.pi / 4)
    bevels[16] = vec2.get_line_point_distance(lin_kl, outer_k)

    # bevels[19] -= 1

    # for i in (17, 20):
    #     bevels[i] = -Z_BEVEL_MID
    outer = [x.xsect for x in offset_poly_per_edge(inner, bevels, PolyType.POLYGON)]

    # The bevels at points 8 and 9 (equivalent to points f and j to lie at the bevel
    # intersection near point g. This allows for the odd bevel near point g.
    outer[8] = outer[9] = _get_abcd_intersection(
        (outer[7], inner[9]), (outer[10], outer[9])
    )
    return inner, outer


v_inner, v_outer = _bevel_and_refine_letter_v_outline(_get_letter_v_rough_outline())
v_inner, v_outer = _bevel_and_refine_letter_v_outline(get_rough3())

_REF_V_TL = (ref_v[0][0], ref_v[1][1])


_old_cam_to_v_tl = vec2.vsub(_REF_V_TL, ref_view_center)
_new_v_tl = vec2.vadd(shared.VIEW_CENTER, _old_cam_to_v_tl)
_V_TRANS = "translate({} {})".format(*_new_v_tl)

v_inner = [vec2.vadd(p, _new_v_tl) for p in v_inner]
v_outer = [vec2.vadd(p, _new_v_tl) for p in v_outer]


def _new_letter_v() -> EtreeElement:
    """Create a `g` svg element for the letter V.

    :return: `g` svg element.
    """
    d_outer = new_data_string(v_outer)
    d_inner = new_data_string(v_inner)
    oline = [gap_polygon(v_outer, V_STROKE_WIDTH)]
    oline_paths = get_polygon_union(*oline)
    d_oline = new_data_string(*oline_paths)

    letter_v = su.new_element("g", id="letter_v")

    def add_path(id_: str, d: str, **attributes: str | float):
        """Add a new subelement path to letter_v."""
        _ = su.new_sub_element(letter_v, "path", id_=id_, d=d, **attributes)

    add_path(id_="v_outline", d=d_oline, fill=shared.FAT_STROKE_COLOR)
    add_path(id_="v_lit_bevels", d=d_outer, fill=shared.GRAY_LIT, **shared.PIN_STROKE)

    # begin dim bevels
    dim_bevels = [
        [*v_outer[3:8], *v_inner[2:8][::-1]],
        [*v_outer[9:11], *v_inner[9:12][::-1]],
        [*v_outer[15:19], *v_inner[14:21][::-1]],
        [*v_outer[20:22], *v_inner[20:23][::-1]],
    ]
    dim_bevel_style = {"fill": shared.GRAY_DIM, **shared.PIN_STROKE}
    for i, d_bevel in enumerate(new_data_string(x) for x in dim_bevels):
        _ = add_path(id_=f"v_dim_bevel_{i}", d=d_bevel, **dim_bevel_style)
    # end dim bevels

    add_path(id_="v_face", d=d_inner, fill=shared.VIM_GRAY, **shared.PIN_STROKE)

    # for (x1, y1), (x2, y2) in ref_outer:
    #     _ = su.new_sub_element(letter_v, "line", x1=x1, y1=y1, x2=x2, y2=y2, stroke_width=2, stroke="purple")

    # # for i in range(3, 4):
    # #     x1, y1 = ref_v_lit_bevels[i][0]
    # #     x2, y2 = ref_v_lit_bevels[i][1]
    # _ = su.new_sub_element(letter_v, "line", x1=x1, y1=y1, x2=x2, y2=y2, stroke="red")
    # _ = su.new_sub_element(letter_v, "path", d=new_data_string([x[0] for x in ref_outer]), fill="none", stroke_width=0.25, stroke="green")

    return letter_v


elem_v = _new_letter_v()
