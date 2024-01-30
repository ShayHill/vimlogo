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


Bevels into the z plane (Z_BEVEL) are calculated from each other such that at a right
corner A, B, C, the first bevel point will be collinear with BC and second bevel
point collinear with AB. The only way to decrease or increase these bevels is to
decrease or increase the XY_BEVEL. This was the main source of "cheating" in the
original vim.org logo.

The angle on the top of the diagonal line is 45 degrees. The outside of the angled V
stroke is *not* parallel. This is required to match the width and height of the
vim.org logo.

After building this basic shape, I bevel the 90-degree right turns (at a, b, c, h, i,
j, m, and o) to get 23 points, starting with the ccw bevel point at point a. I then
offset all of these points to get a second set of 23 points which define a polygon
BEVEL distance outside the original polygon.

These bevels require some adjustment at points 8 and 9 (equivalent to points f and j,
neither of which are beveled). These bevel points are made identical and equal to the
intersection of bevel edges 7->8 (equivalent to e->f) and 9->10 (equivalent to g->h).

The final construction is a black polygon which will show as an outline around the
letter V, a white polygon over the entire outer bevels, a gray polygon over the
letter itself, shaded polygons explicity defined for shaded bevels, and a thin
outline around the letter to hide the seams between the letter and shaded polygons.

------

Keeping this here, because I had to build it by hand and might want it for future work.

from vim_logo.reference_paths import (
    ref_v_dim_bevels,
    ref_v_lit_bevels,
    start_from_first_lexigraphically_sorted_point
)


def get_chain(
    points: list[tuple[float, float]], *indices: int
) -> Iterator[tuple[float, float]]:
    #Get two points from a list of points.

    #:param points: the list of points.
    #:param indices: the indices of the points to return.
    #:return: the two points.
    #
    return (points[i] for i in indices[:-1])


ref_outer = [
    *get_chain(ref_v_dim_bevels[0], 2, 3),
    *get_chain(ref_v_lit_bevels[0], 0, 1, 2, 3, 4, 5),
    *get_chain(ref_v_dim_bevels[1], 7, 8, 9, 0, 1),
    *get_chain(ref_v_lit_bevels[2], 4, 0),
    *get_chain(ref_v_dim_bevels[3], 2, 3),
    *get_chain(ref_v_lit_bevels[3], 0, 1, 2, 3, 4, 5),
    *get_chain(ref_v_dim_bevels[2], 7, 0, 1, 2),
    *get_chain(ref_v_lit_bevels[1], 0, 1, 2),
]

ref_outer = start_from_first_lexigraphically_sorted_point(ref_outer)

:author: Shay Hill
:created: 2024-01-03
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import svg_ultralight as su
import vec2_math as vec2
from offset_poly import offset_poly_per_edge
from offset_poly.offset import PolyType

from vimlogo import shared
from vimlogo.glyphs import get_polygon_union, new_data_string
from vimlogo.reference_paths import (
    get_dims,
    ref_v,
    ref_v_bevels,
    ref_v_oline,
    ref_view_center,
)

if TYPE_CHECKING:
    from lxml.etree import _Element as EtreeElement  # type: ignore

TWO_VEC2 = tuple[tuple[float, float], tuple[float, float]]

V_STROKE_WIDTH = (get_dims(ref_v_oline)[0] - get_dims(ref_v_bevels)[0]) / 2


def _get_y_intercept(abc: tuple[float, float, float], x: float) -> tuple[float, float]:
    """Get the value of a line defined by a, b, and c, at a given x value."""
    a, b, c = abc
    y = (-a * x - c) / b
    return x, y


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


def _translate_line(
    abc: tuple[float, float, float], vec: tuple[float, float]
) -> tuple[float, float, float]:
    """Translate a 2d line in standard `Ax+Bc+C` format.

    :param abc: the line to translate.
    :param vec: the vector by which to translate the line.
    """
    a, b, c = abc
    x, y = vec
    c -= a * x + b * y
    return a, b, c


# ===============================================================================
#   Measurements made from the source
# ===============================================================================

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


# the bevel along the right side of the vertical V stroke.
# Justification: The justification for this bevel width has to do with aligning bevel
# points in ways I do not repeat in this version, because they require too many
# kludges later on. This is the measured value rounded to the nearest 96th.
BEVEL_DE = 1002 / 96  # 10.4375


# the bevel along the left side of the vertical V stroke.
# Justification: This is used twice, to thicken both the bevel and the black stroke
# along MN to balance out the bottoms of the left serif. Importantly, the bevel and
# black stroke are not wide enough to make a symmetrical outline around the black
# outline of the V. That measurement would be 7.625. The original designer went with
# one less, and I think it looks good.
BEVEL_MN = 636 / 96  # 6.625


# values required to set the width and height of the letter V.
# Justification: Snapped reference points to nearest 96th.
INNER_Hx = 14149 / 96
INNER_Jx = 22588 / 96
INNER_Lx = 3539 / 96
INNER_Ly = 20957 / 96


# ===============================================================================
#   Values calculated from the above measurements.
# ===============================================================================

LRG_BEV = (OUTER_BC - INNER_BC) / 2

# the bevels on the inside face of the V. These are only about 85% of the width of
# the reference-image bevels. There are only two ways to get the "impossible" bevel
# shading to work: 1) define the small bevels relative to the large bevels at exactly
# this ratio, or 2) use "graph paper bevels" only on the right-hand, 90-degree turns.
# Graph-paper bevels are bevels that are not the same distance from the inner
SML_BEV = LRG_BEV * math.sin(1 / 8 * math.pi) / math.sin(3 / 8 * math.pi)

INNER_AB = OUTER_AB - 2 * LRG_BEV

INNER_FG = OUTER_BC - INNER_BC


def _get_letter_v_rough_outline() -> list[tuple[float, float]]:
    """Define the inner face of the letter V, without small bevels."""
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

    # fmt: off
    return [
        pnt_a, pnt_b, pnt_c, pnt_d, pnt_e, pnt_f, pnt_g, pnt_h,
        pnt_i, pnt_j, pnt_k, pnt_l, pnt_m, pnt_n, pnt_o,
    ]
    # fmt: on


def _bevel_90_turns(pts: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Find any 90-degree turns in a list of points and replace them with a bevel.

    :param pts: A list of points.
    :reture: A list of points with any points at 90-degree turns replaced with two
        points, each a hard-coded distance away from the original point.
    """
    new_pts: list[tuple[float, float]] = []
    for a, b, c in zip(pts[-1:] + pts[:-1], pts, pts[1:] + pts[:1]):
        vec_ba = vec2.set_norm(vec2.vsub(a, b), SML_BEV)
        vec_cb = vec2.set_norm(vec2.vsub(b, c), SML_BEV)
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
    """Refine the letter V outline to match the vim.org logo.

    :param pts: The rough outline of the letter V.
    :return: inner and outer points. There will be one more point in the outer list,
        as the outer bevels meet to combine points f and g in the inner bevels.

    Bevel the 90-degree corners on the xy plane, then bevel the entire outline
    (conceptually) into the z axis. Not all of the bevels are the same width. In the
    reference, pretty much none of them are. The reference has 4 extra-wide bevels,
    three based on paths between points places in seemingly intentional ways, and a
    fourth (on the left of the vertical bar) seemingly arbitrary. I have used the
    normal bevel size here to keep the bottom left corner of the V looking good.
    """
    inner = _bevel_90_turns(pts)
    bevels = [-LRG_BEV] * (len(inner) - 1)

    # from measurements in the source
    bevels[6] = -BEVEL_DE

    # from inner segment fg
    bevels[7] = -INNER_FG * math.sin(math.pi / 4)

    # the bevel on line kl is made wide enough to pass through a point on the outer
    # bevels (outer_k) with similar (and therefore assumed intentional) dimensions as
    # lines in other parts of the picture.
    line_kl = vec2.get_standard_form((pts[10], pts[11]))
    outer_k = vec2.vadd(pts[9], (LRG_BEV, INNER_BC))
    bevels[16] = vec2.get_line_point_distance(line_kl, outer_k)

    # hard-coded from reference
    bevels[19] = -BEVEL_MN

    outer = [x.xsect for x in offset_poly_per_edge(inner, bevels, PolyType.POLYGON)]

    # combine points f and g for the outer points.
    outer[8] = outer[9] = _get_abcd_intersection(
        (outer[7], inner[9]), (outer[10], outer[9])
    )
    return inner, outer


def _get_translated_v_outlines() -> (
    tuple[list[tuple[float, float]], list[tuple[float, float]]]
):
    """Get the outlines of the letter V, translated to the reference position.

    :return: inner and outer points. There will be one more point in the outer list,
        as the outer bevels meet to combine points f and g in the inner bevels.
    """
    v_inner, v_outer = _bevel_and_refine_letter_v_outline(_get_letter_v_rough_outline())

    _REF_V_TL = (ref_v[0][0], ref_v[1][1])

    _old_cam_to_v_tl = vec2.vsub(_REF_V_TL, ref_view_center)
    _new_v_tl = vec2.vadd(shared.VIEW_CENTER, _old_cam_to_v_tl)
    _V_TRANS = "translate({} {})".format(*_new_v_tl)

    # fmt: off
    return (
        [vec2.vadd(p, _new_v_tl) for p in v_inner],
        [vec2.vadd(p, _new_v_tl) for p in v_outer]
    )
    # fmt: on


v_inner, v_outer = _get_translated_v_outlines()


def _new_letter_v() -> EtreeElement:
    """Create a `g` svg element for the letter V.

    :return: `g` svg element.

    This is the only element where the outline is not uniform. The outline on the
    left side of the vertical v stroke is a bit thicker.
    """
    d_outer = new_data_string(v_outer)
    d_inner = new_data_string(v_inner)

    oline_bevels = [-LRG_BEV] * len(v_outer)
    oline_bevels[18] = -BEVEL_MN
    oline = [
        x.xsect for x in offset_poly_per_edge(v_outer, oline_bevels, PolyType.POLYGON)
    ]

    oline_paths = get_polygon_union(oline)
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

    return letter_v


elem_v = _new_letter_v()
