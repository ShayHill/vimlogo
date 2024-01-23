"""Examine the vim.org reference svg to get dimensions.

The values are toward the bottom of the file and all start with `ref_`.

In addition, there is one public function, `get_dims`, which takes a list of points
and gives a (width, height) tuple.

:author: Shay Hill
:created: 2024-01-11
"""

from collections.abc import Iterable

import vec2_math as vec2
from lxml import etree
from lxml.etree import _Element as EtreeElement  # type: ignore

from vim_logo.paths import REFERENCE_IMAGE_PATH


def _get_reference_root() -> EtreeElement:
    """Get the root of the reference svg."""
    return etree.parse(REFERENCE_IMAGE_PATH).getroot()


_reference_root = _get_reference_root()


def _find_elem_by_id(id_: str) -> EtreeElement:
    """Find an element by its id."""
    elem = _reference_root.find(f".//*[@id='{id_}']")
    if elem is None:
        msg = f"Element with id '{id_}' not found."
        raise ValueError(msg)
    return elem


# Map arbitrarily selected names to hand-selected elements in the reference image.
_name2elem = {
    "background": _find_elem_by_id("path493"),
    "diamond_bevel_ne": _find_elem_by_id("path18"),
    "diamond_bevel_nw": _find_elem_by_id("path14"),
    "diamond_bevel_se": _find_elem_by_id("path6"),
    "diamond_bevel_sw": _find_elem_by_id("path10"),
    "diamond_face": _find_elem_by_id("path22"),
    "diamond_outline": _find_elem_by_id("path2"),
    "i_face_dot": _find_elem_by_id("path86"),
    "i_face_stem": _find_elem_by_id("path82"),
    "m_face": _find_elem_by_id("path74"),
    "m_outline": _find_elem_by_id("path70"),
    "v_face": _find_elem_by_id("path62"),
    "v_bevel_dim_0": _find_elem_by_id("path42"),
    "v_bevel_dim_1": _find_elem_by_id("path46"),
    "v_bevel_dim_2": _find_elem_by_id("path54"),
    "v_bevel_dim_3": _find_elem_by_id("path58"),
    "v_bevel_lit_0": _find_elem_by_id("path30"),
    "v_bevel_lit_1": _find_elem_by_id("path34"),
    "v_bevel_lit_2": _find_elem_by_id("path38"),
    "v_bevel_lit_3": _find_elem_by_id("path50"),
    "v_outline": _find_elem_by_id("path26"),
}


def _get_elem_attrib(name: str, attrib: str) -> str:
    """Get an attribute from an element.

    :param name: the nickname of the element
    :param attrib: the attribute to retrieve
    :return: the value of the attribute

    Check in the element's attrib dictionary first. If the attribute is not found,
    check for a `style` key in `elem.attrib` and try to infer the attribute from the
    style string.
    """
    elem = _name2elem[name]
    if attrib in elem.attrib:
        return elem.attrib[attrib]
    if "style" in elem.attrib:
        style = elem.attrib["style"]
        for style_attrib in style.split(";"):
            if style_attrib.startswith(attrib + ":"):
                return style_attrib.split(":")[1]
    msg = f"Attribute '{attrib}' not found in element '{elem}'."
    raise ValueError(msg)


def _get_pts_from_datastring(datastring: str) -> list[tuple[float, float]]:
    """Get a list of points from the datastring of an absolute, linear path."""
    words = datastring.split()
    command = "M"
    pts: list[tuple[float, float]] = []
    for word in words:
        if word in "MLHVZ":
            command = word
            continue
        if command in "ML":
            x, y = word.split(",")
            pts.append((float(x), float(y)))
        if command == "H":
            x = word
            pts.append((float(x), pts[-1][1]))
        if command == "V":
            y = word
            pts.append((pts[-1][0], float(y)))
    if pts[0] == pts[-1]:
        _ = pts.pop()
    return pts


def _get_bounds(
    pts: Iterable[tuple[float, float]]
) -> tuple[tuple[float, float], tuple[float, float]]:
    """Get the footprint of a list of points."""
    min_x = min(pt[0] for pt in pts)
    min_y = min(pt[1] for pt in pts)
    max_x = max(pt[0] for pt in pts)
    max_y = max(pt[1] for pt in pts)
    return (min_x, min_y), (max_x, max_y)


def _get_pts(name: str) -> list[tuple[float, float]]:
    """Get points from an element as a list of xy tuples.

    :param name: the nickname of the element
    :return: a list of xy tuples
    """
    return _get_pts_from_datastring(_name2elem[name].attrib["d"])


def _get_pts_multi(name_startswith: str) -> list[tuple[float, float]]:
    """Return points from several elements in one list.

    :param name_startswith: gather all points with
        k.startswith(name_startswith)
    :returns: a list of all points for which the key starts with name_startswith

    The points will not contain any information about where one path ends and the
    next begins. The points will only be good for inferring dimensions.
    """
    result: list[tuple[float, float]] = []
    return sum(
        (_get_pts(k) for k in _name2elem if k.startswith(name_startswith)), start=result
    )


def start_from_first_lexigraphically_sorted_point(
    pts: list[tuple[float, float]]
) -> list[tuple[float, float]]:
    """Start the list of points from the first lexigraphically sorted point.

    :param pts: a list of points
    :return: the same list of points, but starting from the first lexigraphically
        sorted point

    This is a hack to make the reference image match the logo image. The reference
    image is not drawn in a clockwise fashion, so the first point is not the first
    point in the logo image. This function is used to make the reference image match
    the logo image.
    """
    first_point = min(pts)
    first_point_index = pts.index(first_point)
    return pts[first_point_index:] + pts[:first_point_index]


def get_dims(pts: Iterable[tuple[float, float]]) -> tuple[float, float]:
    """Get the dimensions of a group of points."""
    (min_x, min_y), (max_x, max_y) = _get_bounds(list(pts))
    return max_x - min_x, max_y - min_y


ref_viewbox = tuple(float(x) for x in _reference_root.attrib["viewBox"].split())
ref_view_center = vec2.vscale(vec2.vadd(ref_viewbox[:2], ref_viewbox[2:]), 0.5)

ref_i_stem = start_from_first_lexigraphically_sorted_point(_get_pts("i_face_stem"))
ref_i_stem = [ref_i_stem[0], *reversed(ref_i_stem[1:])]

ref_i_dot = start_from_first_lexigraphically_sorted_point(_get_pts("i_face_dot"))
ref_i_dot = [ref_i_dot[0], *reversed(ref_i_dot[1:])]


ref_m = start_from_first_lexigraphically_sorted_point(_get_pts("m_face"))
ref_m_oline = _get_pts("m_outline")


# start from first lexigraphically sorted point and reverst to make it clockwise
ref_v = start_from_first_lexigraphically_sorted_point(_get_pts("v_face"))
ref_v = [ref_v[0], *reversed(ref_v[1:])]

ref_v_oline = _get_pts("v_outline")
ref_v_bevels = _get_pts_multi("v_bevel")

ref_diamond_inner = _get_pts("diamond_face")
ref_diamond_outer = _get_pts_multi("diamond_bevel")
ref_diamond_oline = _get_pts("diamond_outline")

# Other elements use a polygon for the surrounding wide stroke. The background is a
# polygon around the elements *with* a wide stroke-width.
ref_background = _get_pts("background")
ref_background_stroke_width = float(_get_elem_attrib("background", "stroke-width"))


ref_v_dim_bevels = [
    _get_pts("v_bevel_dim_0"),
    _get_pts("v_bevel_dim_1"),
    _get_pts("v_bevel_dim_2"),
    _get_pts("v_bevel_dim_3"),
]

ref_v_lit_bevels = [
    _get_pts("v_bevel_lit_0"),
    _get_pts("v_bevel_lit_1"),
    _get_pts("v_bevel_lit_2"),
    _get_pts("v_bevel_lit_3"),
]
