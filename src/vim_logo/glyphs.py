"""Simple, basic tools for building glyphs from linear paths.

:author: Shay Hill
:created: 2023-12-30
"""

from __future__ import annotations

from typing import Any, Callable, Sequence, TypeVar
import shapely
from shapely.validation import make_valid
from shapely.geometry import Polygon

import svg_ultralight as su

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


def _get_poly_coords(polygon: Polygon) -> list[tuple[float, float]]:
    """Get the coordinates of a polygon as a list of tuples."""
    return [(x, y) for x, y in polygon.exterior.coords._coords]


def make_valid_polygons(
    pts: list[tuple[float, float]]
) -> list[list[tuple[float, float]]]:
    """Make a polygon valid by removing self intersections.

    :param pts: list of (x, y) points in a linear spline.
    :return: list of lists of (x, y) points in a linear spline. Validating a polygon
        can produce more than one polygon if you have bowties or holes.
    """
    polygon = shapely.geometry.Polygon(pts)
    if polygon.is_valid:
        return _get_poly_coords(polygon)
    valid_polygons = make_valid(polygon).geoms
    return [_get_poly_coords(p) for p in list(valid_polygons)[:-1]]


def new_data_string(pts: list[tuple[float, float]]) -> str:
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
                commands.append(f"H {x2}")
        elif commands[-1][0] in {"M", "L"}:
            commands[-1] = commands[-1] + f" {x2},{y2}"
        else:
            commands.append(f"L{x2},{y2}")
    return " ".join(commands) + "Z"
