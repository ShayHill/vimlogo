"""Simple, basic tools for building glyphs from linear paths.

:author: Shay Hill
:created: 2023-12-30
"""

from __future__ import annotations

from typing import Any, TypeVar

from collections.abc import Callable, Sequence

import shapely
import svg_ultralight as su
from offset_poly import offset_poly_per_edge, offset_polygon
from offset_poly.offset import PolyType
from shapely.geometry import GeometryCollection, MultiPolygon, Polygon
from shapely.ops import unary_union
from shapely.validation import make_valid

_T = TypeVar("_T")


def _remove_identical_adjacent_values(
    values: Sequence[_T], *, key: Callable[[_T], Any] | None = None
) -> list[_T]:
    """Remove any adjacent identical values, including identical endpoints.

    :param values: sequence of values.
    :param key_func: optional function to apply to each value before comparison.
    :return: list of values where no values[i] == values[i + 1 % len(values)].
    """
    if len(values) < 2:
        return list(values)

    keys = list(values) if key is None else [key(pt) for pt in values]
    keep_ixs = [i for i, (x, y) in enumerate(zip(keys, keys[1:] + keys[:1])) if x != y]
    if keep_ixs:
        return [values[i] for i in keep_ixs]
    return [values[0]]


def _get_poly_coords(polygon: Polygon) -> list[list[tuple[float, float]]]:
    """Get the coordinates of a polygon as a list of tuples."""
    rings = [[(x, y) for x, y in polygon.exterior.coords._coords]]
    for interior in polygon.interiors:
        rings.append([(x, y) for x, y in interior.coords._coords])
    return rings


def _make_valid_polygons_single(
    pts: list[tuple[float, float]]
) -> list[list[tuple[float, float]]]:
    """Make a polygon valid by removing self intersections.

    :param pts: list of (x, y) points in a linear spline.
    :return: list of lists of (x, y) points in a linear spline. Validating a polygon
        can produce more than one polygon if you have bowties or holes.
    """
    polygon = shapely.geometry.Polygon(pts)
    if polygon.is_valid:
        return polygon
    return make_valid(polygon)
    # valid_polygons = make_valid(polygon).geoms
    # all_polygons: list[list[tuple[float, float]]] = []
    # for valid_polygon in list(valid_polygons)[:-1]:
    #     all_polygons.append(valid_polygon)
    # return all_polygons


def make_valid_polygons(
    *pts_lists: list[tuple[float, float]]
) -> list[list[tuple[float, float]]]:
    all_polygons: list[list[tuple[float, float]]] = []
    for pts in pts_lists:
        all_polygons.append(_make_valid_polygons_single(pts))
    return all_polygons


def _new_data_string_single(pts: list[tuple[float, float]]) -> str:
    """Create a linear svg data string from a list of points.

    :param pts: list of (x, y) points in a linear spline.
    :return: svg data string. E.g., "M 3,4 L 5,6 L 7,8 Z"

    This can handle adjacent M->L, L->L, H->H, and V->V commands.
    "L 3,4 L 5,6" is equivalent to "L 3,4 5,6".

    Will also remove intermediate points in adjavent H or V commands. My browser
    (Edge) does not like "L 3,4 H 5 H 6" and will produce rendering errors. This
    function will produce "L 3,4 H 6" instead.

    This function does not handle duplicate identical points. Handling the case of
    duplicates at the end points makes that a bit messy to include here. That first
    call to `_remove_identical_adjacent_values(pts)` is important because duplicate
    adjacent points will cause WILD strokes.

    All the paths in this project are linear and closed, so this function makes that
    assumption.
    """
    str_tuples = [(su.format_number(x), su.format_number(y)) for x, y in pts]
    str_tuples = _remove_identical_adjacent_values(str_tuples)
    commands = [f"M{str_tuples[0][0]},{str_tuples[0][1]}"]
    for (x1, y1), (x2, y2) in zip(str_tuples, str_tuples[1:]):
        if x1 == x2:
            if commands[-1][0] == "V":
                commands[-1] = f"V{y2}"
            else:
                commands.append(f"V{y2}")
        elif y1 == y2:
            if commands[-1][0] == "H":
                commands[-1] = f"H{x2}"
            else:
                commands.append(f"H{x2}")
        elif commands[-1][0] in {"M", "L"}:
            commands[-1] = commands[-1] + f" {x2},{y2}"
        else:
            commands.append(f"L{x2},{y2}")
    return " ".join(commands) + "Z"


def new_data_string(*pts_lists: list[tuple[float, float]]) -> str:
    """Create a linear svg data string from a list of points.

    :param pts: list of (x, y) points in a linear spline.
    :return: svg data string. E.g., "M 3,4 L 5,6 L 7,8 Z"

    This can handle adjacent M->L, L->L, H->H, and V->V commands.
    "L 3,4 L 5,6" is equivalent to "L 3,4 5,6".

    Will also remove intermediate points in adjavent H or V commands. My browser
    (Edge) does not like "L 3,4 H 5 H 6" and will produce rendering errors. This
    function will produce "L 3,4 H 6" instead.

    This function does not handle duplicate identical points. Handling the case of
    duplicates at the end points makes that a bit messy to include here. That first
    call to `_remove_identical_adjacent_values(pts)` is important because duplicate
    adjacent points will cause WILD strokes.

    All the paths in this project are linear and closed, so this function makes that
    assumption.
    """
    return " ".join([_new_data_string_single(pts) for pts in pts_lists])


# def gap_polygon_with_validation(pts: list[tuple[float, float]], gap: float) -> Polygon | MultiPolygon | GeometryCollection:
#     """Gap a polygon then remove self intersections.
#     """
#     gapped = [x.xsect for x in offset_polygon(pts, -gap)]
#     polygon = Polygon(gapped)
#     aaa = make_valid_polygons(polygon)
#     if aaa.type == "Polygon":
#         bbb = _get_poly_coords(aaa)

#     breakpoint()
#     return


def get_polygon_union(
    *pnt_lists: list[tuple[float, float]], negative: set[int] | None = None
) -> list[list[tuple[float, float]]]:
    """Get the union of a list of polygons.

    :param pnt_lists: list of lists of (x, y) points in a linear spline.
    :return: union of the polygons.
    """
    negative = negative or set()
    union = unary_union([])
    for i, pts in enumerate(pnt_lists):
        if i in negative:
            union = union - make_valid(Polygon(pts))
        else:
            union = unary_union([union, make_valid(Polygon(pts))])
    # polygons = [Polygon(pts) for pts in pnt_lists]
    # union = unary_union([make_valid(p) for p in polygons])
    # if negative is not None:
    #     union = union - Polygon(negative)
    if union.geom_type == "Polygon":
        return _get_poly_coords(union)
    polygons = [g for g in union.geoms if g.geom_type == "Polygon"]
    return sum([_get_poly_coords(p) for p in polygons], [])


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
