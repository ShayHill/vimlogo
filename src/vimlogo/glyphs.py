"""Simple, basic tools for building glyphs from linear paths.

:author: Shay Hill
:created: 2023-12-30
"""

# pyright: reportMissingTypeStubs=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false

from __future__ import annotations

from typing import Any

from cubic_bezier_spline import new_closed_linear_spline
from offset_poly import offset_polygon
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.validation import make_valid


def _get_poly_coords(polygon: Polygon) -> list[list[tuple[float, float]]]:
    """Get the coordinates of a polygon as a list of tuples."""
    rings = [[(x, y) for x, y in polygon.exterior.coords]]
    rings.extend([(x, y) for x, y in x.coords] for x in polygon.interiors)
    return rings


def new_data_string(*pts_lists: list[tuple[float, float]]) -> str:
    """Create a linear svg data string from multiple lists of points.

    :param pts: list of (x, y) points in a linear spline, multiple allowed.
    :return: svg data string. E.g., "M 3 4L 5 6L 7 8Z"

    `new_closed_linear_spline` will handle any of the mess (e.g., duplicate points)
    shapely throws at it.
    """
    svgds = (new_closed_linear_spline(x).svgd for x in pts_lists)
    return "".join(svgds)


def get_polygon_union(
    *pnt_lists: list[tuple[float, float]], negative: set[int] | None = None
) -> list[list[tuple[float, float]]]:
    """Get the union of a list of polygons.

    :param pnt_lists: list of lists of (x, y) points in a linear spline.
    :return: union of the polygons.
    """
    negative = negative or set()
    union: Any = unary_union([])
    for i, pts in enumerate(pnt_lists):
        if i in negative:
            union = union - make_valid(Polygon(pts))
        else:
            union = unary_union([union, make_valid(Polygon(pts))])
    if union.geom_type == "Polygon":
        return _get_poly_coords(union)
    polygons = [g for g in union.geoms if g.geom_type == "Polygon"]
    poly_coords_list = [_get_poly_coords(p) for p in polygons]
    return [x for y in poly_coords_list for x in y]


def gap_polygon(
    pts: list[tuple[float, float]], gap: float
) -> list[tuple[float, float]]:
    """Gap a polygon.

    :param pts: list of (x, y) points in a linear spline.
    :param gap: distance to gap the polygon.
    :return: list of lists of (x, y) points in a linear spline. Gapping a polygon can
        produce more than one polygon if you have bowties or holes.
    """
    return [x.xsect for x in offset_polygon(pts, -gap)]


