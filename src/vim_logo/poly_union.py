"""Create a union of polygons and remove self intersections from single polygons.

:author: Shay Hill
:created: 2024-01-10
"""

from typing import Any, TypeVar, Sequence, Callable
import vec2_math as vec2

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


def _get_min_index(values: Sequence[Any]) -> int:
    """Return the index of the minimum value in a sequence.

    :param values: sequence of values.
    :return: index of the minimum value.
    """
    return min(enumerate(values), key=lambda x: x[1])[0]

aaa = vec2.get_segment_intersection(((0, 0), (10, 0)), ((5, 0), (15, 0)))
aaa = vec2.project_to_segment(((0, 0), (10, 0)), (15, 0))
bbb = vec2.get_standard_form(((0, 0), (10, 0)))
ccc = vec2.get_standard_form(((0, 0), (1, 0)))
ddd = vec2.get_standard_form(((1, 0), (0, 0)))
eee = vec2.__annotations__
breakpoint()

# def _remove_self_intersections(
#     polygon: Sequence[vec2.Vec2], *, key: Callable[[vec2.Vec2], Any] | None = None
# ) -> list[vec2.Vec2]:
#     """Remove any self intersections from a polygon.

#     :param polygon: sequence of points.
#     :param key_func: optional function to apply to each point before comparison.
#     :return: list of points where no points[i] == points[i + 1 % len(points)].
#     """
#     polygon = _remove_identical_adjacent_values(polygon)
#     min_index = _get_min_index(polygon)
#     polygon = polygon[min_index:] + polygon[:min_index]
#     if len(polygon) < 3:
#         return polygon

#     legs = list(zip(polygon, polygon[1:] + polygon[:1]))
#     for i, leg_a in enumerate(legs):
#         for leg_b in legs[i+1:]


