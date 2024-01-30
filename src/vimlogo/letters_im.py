"""The lowercase letters i and m in Vim.

These are in better shape than anything else in the reference svg. They appear to
have been distorted with non-uniform scaling with a mouse, but most of that can be
fixed by snapping back the reference SVG points to the grid on which I believe they
were originally drawn.

They are a *very* good fit on a 60-unit x-height grid.

:author: Shay Hill
:created: 2023-12-30
"""

from __future__ import annotations

import functools as ft
from typing import TYPE_CHECKING

import svg_ultralight as su
import vec2_math as vec2

from vimlogo import shared
from vimlogo.glyphs import gap_polygon, get_polygon_union, new_data_string
from vimlogo.reference_paths import (
    get_dims,
    ref_i_dot,
    ref_m,
    ref_m_oline,
    ref_view_center,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

    from lxml.etree import _Element as EtreeElement  # type: ignore


# ===============================================================================
#   Letters can for the most part be cleaned up by snapping to a 60-unit-high grid
# ===============================================================================


_REF_HEIGHT = get_dims(ref_m)[1]
_UNIT = _REF_HEIGHT / 60


def _snap_to_grid(pt: tuple[float, float]) -> tuple[float, float]:
    relative = vec2.vsub(pt, ref_m[0])
    return round(relative[0] / _UNIT), round(relative[1] / _UNIT)


def _snap_pts(pts: list[tuple[float, float]]) -> list[tuple[float, float]]:
    return [_snap_to_grid(pt) for pt in pts]


# ===============================================================================
#   Make adjustments where snapping to the grid doesn't work
# ===============================================================================


# Adjust point 13 to make all vertical lines parallel while best matching slope of
# that corner in the reference. The resulting point isn't exactly on the grid, but no
# grid point maintains parallel vertical lines while remotely resembling the reference.
letter_m_pts = _snap_pts(ref_m)
letter_m_pts[13] = (113.5, -52.5)

# The reference i stem is a mess. Build a new one from leg points in the m
letter_i_pts_stem = letter_m_pts[:5] + letter_m_pts[26:]

# everything is good except point 4. Make the top as wide as the bottom
bottom_vec = vec2.vsub(letter_i_pts_stem[-1], letter_i_pts_stem[0])
letter_i_pts_stem[4] = vec2.vadd(letter_i_pts_stem[3], bottom_vec)

# move the i stem to the left of the m (where a 4th leg would be)
one_leg_to_the_left = vec2.vsub(letter_m_pts[22], letter_m_pts[16])
letter_i_pts_stem = [vec2.vadd(x, one_leg_to_the_left) for x in letter_i_pts_stem]

# the dots are fine
letter_i_pts_dot = _snap_pts(ref_i_dot)


# ===============================================================================
#   Scale and translate the letters back to the reference i and m elements
# ===============================================================================


def _get_scale() -> float:
    """Average the width and height proportions of the reference m and the letter m.

    This number will be close to 1.0
    """
    ref_w, ref_h = get_dims(ref_m)
    new_w, new_h = get_dims(letter_m_pts)
    return (ref_w / new_w + ref_h / new_h) / 2


def _get_translation() -> tuple[float, float]:
    """Translate the first point of the letter m to the reference m.

    Take into account the potentially different viewbox of the reference image.
    """
    ref_camera_to_m0 = vec2.vsub(ref_m[0], ref_view_center)
    return vec2.vadd(shared.VIEW_CENTER, ref_camera_to_m0)


_IM_SCALE = _get_scale()
_IM_TRANSLATION = _get_translation()
IM_STROKE_WIDTH = (get_dims(ref_m_oline)[1] - get_dims(ref_m)[1]) / 2


def _transform_point(pt: tuple[float, float]) -> tuple[float, float]:
    """Scale and translate a point to fit the reference m."""
    pt = vec2.vscale(pt, _IM_SCALE)
    return vec2.vadd(pt, _IM_TRANSLATION)


def _transform_points(pts: Iterable[tuple[float, float]]) -> list[tuple[float, float]]:
    """Scale and translate a list of points to fit the reference m."""
    return [_transform_point(pt) for pt in pts]


letter_m_pts = _transform_points(letter_m_pts)
letter_m_pts_mask = letter_m_pts[:17]
letter_i_pts_stem = _transform_points(letter_i_pts_stem)
letter_i_pts_dot = _transform_points(letter_i_pts_dot)


# ===============================================================================
#   Create a `g` element for the letters i and m
# ===============================================================================


def _new_elem_im() -> EtreeElement:
    """Create a `g` svg element for the combined letters i and m.

    :return: `g` svg element with an outline and a face for each of i_stem, i_dot,
        and m. There may be fewer than 3 outline paths if the outlines overlap.
    """
    point_lists = [letter_i_pts_stem, letter_i_pts_dot, letter_m_pts]
    face_d = new_data_string(*point_lists)

    im_oline = [gap_polygon(pts, IM_STROKE_WIDTH) for pts in point_lists]
    im_oline_paths = get_polygon_union(*im_oline)
    oline_d = new_data_string(*im_oline_paths)

    group = su.new_element("g", id_="letters_im")
    add_path = ft.partial(su.new_sub_element, group, "path")
    _ = add_path(id_="im_outline", d=oline_d, fill=shared.K_STROKE)
    _ = add_path(id_="im_face", d=face_d, fill=shared.VIM_GRAY)
    return group


elem_im = _new_elem_im()
