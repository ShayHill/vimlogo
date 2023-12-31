"""The green diamond behind the letters.

:author: Shay Hill
:created: 2023-12-30
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import svg_ultralight as su
from offset_poly import offset_polygon

from vim_logo.glyphs import new_data_string

if TYPE_CHECKING:
    from lxml.etree import _Element as EtreeElement  # type: ignore


_BEVEL = 3


def _get_diamond_points(rad: float) -> list[tuple[float, float]]:
    return [(rad, 0), (0, -rad), (-rad, 0), (0, rad)]


def _get_diamond_data_string(rad: float) -> str:
    pts = _get_diamond_points(rad)
    return new_data_string(pts)


def _new_diamond(rad: float) -> EtreeElement:
    """Return a diamond element."""
    outer = _get_diamond_points(rad)
    inner = [x.xsect for x in offset_polygon(outer, -_BEVEL)]
    diamond = su.new_element("g")
    _ = su.new_sub_element(diamond, "path", d=new_data_string(inner), fill="yellow")
    return diamond


diamond = _new_diamond(71)
