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
from vim_logo.glyphs import new_data_string
from vim_logo.reference_paths import ref_v, get_footprint, get_dims, ref_v_oline, ref_v_bevels


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

# the strokes are half underneath the bevels, so using both sides of the outline
# footprint will give the corrent 2x stroke width.
_V_STROKE_WIDTH = get_dims(ref_v_oline)[0] - get_dims(ref_v_bevels)[0]

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


def _bevel_90_turns(pts: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Find any 90-degree turns in a list of points and replace them with a bevel."""
    new_pts: list[tuple[float, float]] = []
    for a, b, c in zip(pts[-1:] + pts[:-1], pts, pts[1:] + pts[:1]):
        vec_ba = vec2.set_norm(vec2.vsub(a, b), XY_BEVEL)
        vec_cb = vec2.set_norm(vec2.vsub(b, c), XY_BEVEL)
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
    pts = _bevel_90_turns(pts)
    inner = pts
    outer = [x.xsect for x in offset_polygon(inner, -Z_BEVEL)]
    bevels = [-Z_BEVEL] * (len(inner) - 1)
    for i in (7, 8):
        bevels[i] = -Z_BEVEL_FAT
    for i in (17, 20):
        bevels[i] = -Z_BEVEL_MID
    outer = [x.xsect for x in offset_poly_per_edge(inner, bevels, PolyType.POLYGON)]

    # The bevels at points 8 and 9 (equivalent to points f and j to lie at the bevel
    # intersection near point g. This allows for the odd bevel near point g.
    outer[8] = outer[9] = _get_abcd_intersection(
        (outer[7], inner[9]), (outer[10], outer[9])
    )
    return inner, outer


inner, outer = _bevel_and_refine_letter_v_outline(_get_letter_v_rough_outline())


# TODO: move this transform to a main svg building function
inner = [vec2.vadd(pt, (36, 29)) for pt in inner]
outer = [vec2.vadd(pt, (36, 29)) for pt in outer]


def _new_letter_v() -> EtreeElement:
    """Create a `g` svg element for the letter V.

    :return: `g` svg element.
    """
    d_outer = new_data_string(outer)
    d_inner = new_data_string(inner)

    letter_v = su.new_element("g", id="letter_v")

    def add_path(id_: str, d: str, **attributes: str | float):
        """Add a new subelement path to letter_v."""
        _ = su.new_sub_element(letter_v, "path", id_=id_, d=d, **attributes)

    add_path(
        id_="v_outline",
        d=d_outer,
        fill="none",
        stroke=shared.FAT_STROKE_COLOR,
        stroke_width=_V_STROKE_WIDTH
    )
    add_path(id_="v_lit_bevels", d=d_outer, fill=shared.GRAY_LIT, **shared.PIN_STROKE)

    # begin dim bevels
    dim_bevels = [
        [*outer[3:8], *inner[2:8][::-1]],
        [*outer[9:11], *inner[9:12][::-1]],
        [*outer[15:19], *inner[14:21][::-1]],
        [*outer[20:22], *inner[20:23][::-1]],
    ]
    dim_bevel_style = {"fill": shared.GRAY_DIM, **shared.PIN_STROKE}
    for i, d_bevel in enumerate(new_data_string(x) for x in dim_bevels):
        _ = add_path(id_=f"v_dim_bevel_{i}", d=d_bevel, **dim_bevel_style)
    # end dim bevels

    add_path(id_="v_face", d=d_inner, fill=shared.VIM_GRAY, **shared.PIN_STROKE)

    return letter_v


letter_v = _new_letter_v()
