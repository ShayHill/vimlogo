"""The lowercase letters i and m in Vim.

The top, right corner of the letter m is the origin. Letters i and m are two g
elements.

This mostly but not exactly follows the existing Vim logo. The m was inconsistent, so
I made it more consistent and a bit closer to the source Crillee font.

:author: Shay Hill
:created: 2023-12-30
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import svg_ultralight as su

from vim_logo.glyphs import new_data_string, get_polygon_union, gap_polygon
from vim_logo import shared
from vim_logo.reference_paths import ref_view_center, ref_m_oline
from vim_logo.reference_paths import ref_m, get_dims
from offset_poly import offset_polygon, offset_poly_per_edge

import vec2_math as vec2

if TYPE_CHECKING:
    from lxml.etree import _Element as EtreeElement  # type: ignore


# smaller bevels of the letter i dot
_I_DOT_BEVEL = 1.5

# larger bevels and height / width of the serifs
_BEVEL = 3

# The top or bottom of the vertical line of the letter i, including the serif. The
# width of the bottom of a vertical bar on the letter m, including the serif.
_STROKE_BOT = 12

# width of the top of a vertical space on the letter m
_M_VOID = 10.5

_H_LINES = [
    -(_M_VOID - _BEVEL) - (_STROKE_BOT - _BEVEL),  # top of i dot (same gap as m legs)
    -(_M_VOID - _BEVEL),  # bottom of i dot
    0,  # top of m and i stroke (x-height)
    _BEVEL,  # bottom of divets on the top of the m
    9,  # top of voids between legs of the letter m
    27,  # top of the lower serif on the m and i stroke
    30,  # baseline
]


# ===============================================================================
#   Path transformations
# ===============================================================================


_REF_M_TL = ref_m[0]
_REF_M_R = 276.99076
_REF_M_B = 179.43305

_REF_M_W = ref_m[1][0] - ref_m[-1][0]
_REF_M_H = ref_m[13][1] - ref_m[0][1]
_SCALE_M = _REF_M_W / 51


# _MODEL_HEIGHT = 30
# _MODEL_M_WIDTH = 51

aaa = _REF_M_W / 51
bbb = _REF_M_H / 30
ys = sorted({y for x, y in ref_m})
min_x = min(x for x, y in ref_m if y in ys[1:3])
max_x = max(x for x, y in ref_m if y in ys[1:3])
min_y = min(y for x, y in ref_m)
max_y = max(y for x, y in ref_m)
_SCALE_M = (max_x - min_x) / 51
ddd = (max_y - min_y) / 30

_old_cam_to_m_tl = vec2.vsub(_REF_M_TL, ref_view_center)
_new_m_tl = vec2.vadd(shared.VIEW_CENTER, _old_cam_to_m_tl)

M_TRANS = f"translate({_new_m_tl[0]},{_new_m_tl[1]})scale({_SCALE_M})"


TX = 17 * 7.6
TY = 16.9 * 5.75


def _relx_to_absx(pts: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Convert a list of points from relative to absolute coordinates.

    This is tricky, because only the x values will be relative. The y values will
    already be absolute. The x values are describing the shape of the letter, while
    the y values are representative of the font's baseline, x-height, cap height,
    etc.
    """
    absx = [pts[0]]
    for i, pt in enumerate(pts[1:], 1):
        absx.append((absx[i - 1][0] + pt[0], pt[1]))
    return absx


def _skew_point(pt: tuple[float, float]) -> tuple[float, float]:
    """Skew move x coordinate -1 pt for each 3 y pts."""
    x, y = pt
    skewed = x - y / 3, y
    skewed = vec2.vscale(skewed, _SCALE_M)
    skewed = vec2.vadd(skewed, _new_m_tl)
    # skewed = vec2.vscale(skewed, _SCALE_M)
    # skewed = vec2.vadd(skewed, _REF_M_TL)
    return skewed


def _skew_points(pts: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Skew move x coordinate -1 pt for each 3 y pts."""
    return [_skew_point(pt) for pt in pts]


# ===============================================================================
#   Letter m subpaths
# ===============================================================================

# the top of an m curve all the way to the start of the next curve. There are two and
# a half of these in the letter m.
_curved_top = [
    (_STROKE_BOT - _BEVEL, _H_LINES[2]),
    (_BEVEL, _H_LINES[3]),
    (_M_VOID - _BEVEL * 2 + 1, _H_LINES[3]),
    (_BEVEL - 1, _H_LINES[2]),
]

dou = [4, 3, 2]

PUSH = 1.5
TOP_CURVE = (48 - PUSH - sum(dou) * 2) / 3
_curved_top = [
    (TOP_CURVE, _H_LINES[2]),
    (dou[0], _H_LINES[3]),
    (dou[1], _H_LINES[3]),
    (dou[2], _H_LINES[2])]


# breakpoint()



# just above the bottom serif on an m leg to just above the bottom serif on the next
# leg. There are two and a half of these in the letter m. This is also used as a
# transformation to get from a known point on the letter m to a new point on the stem
# of the letter i.
_bottom_leg = [
    (_BEVEL, _H_LINES[5]),
    (0, _H_LINES[6]),
    (-_STROKE_BOT, _H_LINES[6]),
    (0, _H_LINES[4]),
    (-_M_VOID, _H_LINES[4]),
    (0, _H_LINES[5]),
]

# ===============================================================================
#   Letter m full path
# ===============================================================================

letter_m_pts = [
    # topmost, leftmost point on top serif
    (0, _H_LINES[2]),
    (PUSH, _H_LINES[2]),
    # (_BEVEL, _H_LINES[2]),
    *_curved_top,
    *_curved_top,
    *_curved_top[:1],
    (_BEVEL, _H_LINES[3]),
    # rigth vertical line top to bottom
    (0, _H_LINES[5]),
    *_bottom_leg,
    *_bottom_leg,
    *_bottom_leg[:3],
    # left vertical line bottom to top
    (0, _H_LINES[3]),
    (-_BEVEL, _H_LINES[3]),
]


# aaa = sum(x[0] for x in _letter_m_pts[:11])
# bbb = sum(x[0] for x in _curved_top[:4])
# ccc = sum(x[0] for x in _curved_top[:2])
# breakpoint()

letter_m_pts = _relx_to_absx(letter_m_pts)

letter_m_mask_pts = [*letter_m_pts[:15], *letter_m_pts[26:]]


# ===============================================================================
#   Letter i stem path
# ===============================================================================


def _get_starting_point_of_letter_i() -> tuple[float, float]:
    """Get the point just above the bottom serif of the letter i.

    Treat the i as if it were another vertical bar on the letter m.
    """
    path = [letter_m_pts[-6], *_bottom_leg]
    return _relx_to_absx(path)[-1]


_letter_i_pts_stem = [
    # just above the bottom serif of the letter i
    _get_starting_point_of_letter_i(),
    *_bottom_leg[:3],
    (0, _H_LINES[3]),
    (-_BEVEL, _H_LINES[3]),
    (0, _H_LINES[2]),
    (_STROKE_BOT, _H_LINES[2]),
]

_letter_i_pts_stem = _relx_to_absx(_letter_i_pts_stem)

# ===============================================================================
#   Letter i dot path
# ===============================================================================


_side_length = (_H_LINES[1] - _H_LINES[0]) - _I_DOT_BEVEL * 2

_letter_i_pts_dot = [
    # clockwise, from top bevel of lower, right corner
    (_letter_i_pts_stem[-1][0], _H_LINES[1] - _I_DOT_BEVEL),
    (-_I_DOT_BEVEL, _H_LINES[1]),
    (-_side_length, _H_LINES[1]),
    (-_I_DOT_BEVEL, _H_LINES[1] - _I_DOT_BEVEL),
    (0, _H_LINES[0] + _I_DOT_BEVEL),
    (_I_DOT_BEVEL, _H_LINES[0]),
    (_side_length, _H_LINES[0]),
    (_I_DOT_BEVEL, _H_LINES[0] + _I_DOT_BEVEL),
]

_letter_i_pts_dot = _relx_to_absx(_letter_i_pts_dot)

# ===============================================================================
#   Create `g` elements for the letters i and m
# ===============================================================================

# _letter_m_pts = [(x + TX, y + TY) for x, y in _letter_m_pts]
# _letter_m_mask_pts = [(x + TX, y + TY) for x, y in _letter_m_mask_pts]
# _letter_i_pts_dot = [(x + TX, y + TY) for x, y in _letter_i_pts_dot]
# _letter_i_pts_stem = [(x + TX, y + TY) for x, y in _letter_i_pts_stem]


def _new_letter_m_mask() -> EtreeElement:
    """Create a `path` element of the letter m mask.

    :param ptss: list of lists of (x, y) points in a linear spline.
    :return: `g` svg element.
    """
    skewed = [[_skew_point(pt) for pt in letter_m_mask_pts]]
    data_string = " ".join([new_data_string(pts) for pts in skewed])
    return su.new_element("path", id="letter_m_hull", d=data_string)


MED_STROKE_WIDTH = (_M_VOID - _BEVEL) * 1/3 * _SCALE_M
IM_STROKE_WIDTH = MED_STROKE_WIDTH

IM_STROKE_WIDTH = (get_dims(ref_m_oline)[1] - get_dims(ref_m)[1]) / 2



letter_m_pts = _skew_points(letter_m_pts)
letter_m_pts_mask = _skew_points(letter_m_mask_pts)
_letter_i_pts_dot = _skew_points(_letter_i_pts_dot)
_letter_i_pts_stem = _skew_points(_letter_i_pts_stem)

def _new_letter(name: str, *ptss: list[tuple[float, float]]) -> EtreeElement:
    """Create a `g` svg element for a small letter.

    :param name: id of the `g` element.
    :param ptss: list of lists of (x, y) points in a linear spline.
    :return: `g` svg element.
    """
    # skewed = [[_skew_point(pt) for pt in pts] for pts in ptss]
    skewed = ptss
    data_string = new_data_string(*skewed)
    group = su.new_element("g", id_=f"letters_{name}")

    gapped = [gap_polygon(pts, IM_STROKE_WIDTH) for pts in skewed]
    gapped_paths = get_polygon_union(*gapped)
    # breakpoint()
    # gapped = sum([gap_polygon_with_validation(p, M_STROKE_WIDTH) for p in skewed], start=[])
    gapped_data_string = new_data_string(*gapped_paths)

    outline = su.new_sub_element(group, "path", id_=f"{name}_outline", d=gapped_data_string, fill=shared.MID_STROKE_COLOR)
    _ = su.new_sub_element(group, "path", id_=f"{name}_face", d=data_string, fill=shared.VIM_GRAY)
    return group


elem_m_mask = _new_letter_m_mask()
elem_im = _new_letter("im", letter_m_pts, _letter_i_pts_stem, _letter_i_pts_dot)
