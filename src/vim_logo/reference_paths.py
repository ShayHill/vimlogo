from paragraphs import par
from vim_logo.paths import REFERENCE_IMAGE_PATH
from lxml import etree
from lxml.etree import _Element as EtreeElement  # type: ignore
import vec2_math as vec2


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
    "v": _find_elem_by_id("path62"),
    "m": _find_elem_by_id("path74"),
    "v_outline": _find_elem_by_id("path26"),
    "diamond_outline": _find_elem_by_id("path2"),
    "diamond_face": _find_elem_by_id("path22"),
    "diamond_bevel_se": _find_elem_by_id("path6"),
    "diamond_bevel_sw": _find_elem_by_id("path10"),
    "diamond_bevel_nw": _find_elem_by_id("path14"),
    "diamond_bevel_ne": _find_elem_by_id("path18"),
    "v_bevel_lit_0": _find_elem_by_id("path30"),
    "v_bevel_lit_1": _find_elem_by_id("path34"),
    "v_bevel_lit_2": _find_elem_by_id("path38"),
    "v_bevel_lit_3": _find_elem_by_id("path50"),
    "v_bevel_dim_0": _find_elem_by_id("path42"),
    "v_bevel_dim_1": _find_elem_by_id("path46"),
    "v_bevel_dim_2": _find_elem_by_id("path54"),
    "v_bevel_dim_3": _find_elem_by_id("path58"),
}

def _get_pts_from_datastring(datastring: str) -> list[tuple[float, float]]:
    """Get a list of points from the datastring of an absolute, linear path."""
    words = datastring.split()
    command = "M"
    pts: list[tuple[float, float]] = []
    for word in words:
        if word in "MLHV":
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


def get_footprint(
    pts: list[tuple[float, float]]
) -> tuple[tuple[float, float], tuple[float, float]]:
    """Get the footprint of a list of points."""
    min_x = min(pt[0] for pt in pts)
    min_y = min(pt[1] for pt in pts)
    max_x = max(pt[0] for pt in pts)
    max_y = max(pt[1] for pt in pts)
    return (min_x, min_y), (max_x, max_y)


def get_dims(pts: list[tuple[float, float]]) -> tuple[float, float]:
    """Get the dimensions of a list of points."""
    (min_x, min_y), (max_x, max_y) = get_footprint(pts)
    return max_x - min_x, max_y - min_y


def _get_pts(nickname: str):
    return _get_pts_from_datastring(_nickname2elem[nickname].attrib["d"])

ref_viewbox = tuple(float(x) for x in reference_root.attrib["viewBox"].split())
ref_view_center = vec2.vscale(vec2.vadd(ref_viewbox[:2], ref_viewbox[2:]), 0.5)

ref_v = _get_pts("v")
ref_m = _get_pts("m")

# start from first lexigraphically sorted point
ref_m = ref_m[20:] + ref_m[:20]

# start from first lexigraphically sorted point and reverst to make it clockwise
ref_v = [*ref_v[8:], *ref_v[:8]][::-1]

ref_v_oline = _get_pts("v_outline")
ref_v_bevels = sum(
    (_get_pts(k) for k in _nickname2elem.keys() if k.startswith("v_bevel")),
    start=[],
)

ref_diamond_inner = _get_pts("diamond_face")
ref_diamond_outer = sum(
    (_get_pts(k) for k in _nickname2elem.keys() if k.startswith("diamond_bevel")),
    start=[],
)
ref_diamond_oline = _get_pts("diamond_outline")
