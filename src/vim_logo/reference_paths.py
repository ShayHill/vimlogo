from paragraphs import par
from vim_logo.paths import REFERENCE_IMAGE_PATH
from lxml import etree
from lxml.etree import _Element as EtreeElement  # type: ignore
import vec2_math as vec2
from typing import Iterable


reference_svg = etree.parse(REFERENCE_IMAGE_PATH)
reference_root = reference_svg.getroot()


def _find_elem_by_id(id_: str) -> EtreeElement:
    """Find an element by its id."""
    elem = reference_root.find(f".//*[@id='{id_}']")
    if elem is None:
        msg = f"Element with id '{id_}' not found."
        raise ValueError(msg)
    return elem


_nickname2elem = {
    "background": _find_elem_by_id("path493"),
    "diamond_bevel_ne": _find_elem_by_id("path18"),
    "diamond_bevel_nw": _find_elem_by_id("path14"),
    "diamond_bevel_se": _find_elem_by_id("path6"),
    "diamond_bevel_sw": _find_elem_by_id("path10"),
    "diamond_face": _find_elem_by_id("path22"),
    "diamond_outline": _find_elem_by_id("path2"),
    "m_face": _find_elem_by_id("path74"),
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


def _get_elem_attrib(nickname: str, attrib: str) -> str:
    """Get an attribute from an element.

    """
    elem = _nickname2elem[nickname]
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


def _get_pts(nickname: str) -> list[tuple[float, float]]:
    return _get_pts_from_datastring(_nickname2elem[nickname].attrib["d"])


def _get_pts_multi(nickname_startswith: str) -> list[tuple[float, float]]:
    """Return points from several elements in one list.

    :param nickname_startswith: gather all points with
        k.startswith(nickname_startswith)
    :returns: a list of all points for which the key starts with nickname_startswith

    The points will not contain any information about where one path ends and the
    next begins. The points will only be good for inferring dimensions.
    """
    result: list[tuple[float, float]] = []
    return sum(
        (
            _get_pts(k)
            for k in _nickname2elem.keys()
            if k.startswith(nickname_startswith)
        ),
        start=result,
    )


def get_dims(pts: Iterable[tuple[float, float]]) -> tuple[float, float]:
    """Get the dimensions of a group of points."""
    (min_x, min_y), (max_x, max_y) = _get_bounds(list(pts))
    return max_x - min_x, max_y - min_y



ref_viewbox = tuple(float(x) for x in reference_root.attrib["viewBox"].split())
ref_view_center = vec2.vscale(vec2.vadd(ref_viewbox[:2], ref_viewbox[2:]), 0.5)

# start from first lexigraphically sorted point
ref_m = _get_pts("m_face")
ref_m = ref_m[20:] + ref_m[:20]

# start from first lexigraphically sorted point and reverst to make it clockwise
ref_v = _get_pts("v_face")
ref_v = [*ref_v[8:], *ref_v[:8]][::-1]

ref_v_oline = _get_pts("v_outline")
ref_v_bevels = _get_pts_multi("v_bevel")

ref_diamond_inner = _get_pts("diamond_face")
ref_diamond_outer = _get_pts_multi("diamond_bevel")
ref_diamond_oline = _get_pts("diamond_outline")

ref_background = _get_pts("background")
ref_background_stroke_width = float(_get_elem_attrib("background", "stroke-width"))
