"""Construct the svg from parts.

:author: Shay Hill
:created: 2024-01-10
"""

import subprocess
import sys
import tomllib
from pathlib import Path

import svg_ultralight as su
from basic_colormath import rgb_to_hex
from lxml.etree import _Element as EtreeElement  # pyright: ignore[reportPrivateUsage]
from svg_path_data import get_cpts_from_svgd
from svg_ultralight import new_metadata

from vimlogo import params_diamond, shared
from vimlogo.diamond import (
    diamond_cpts,
    diamond_outer,
    diamond_shader,
    illuminate_bevel,
)
from vimlogo.glyphs import gap_polygon, get_polygon_union, new_data_string
from vimlogo.letter_v import V_STROKE_WIDTH, v_cpts, v_outer
from vimlogo.letters_im import IM_STROKE_WIDTH, im_cpts, letter_m_mask
from vimlogo.paths import OUTPUT, PROJECT_DIR, PYPROJECT_TOML


def _get_git_remote_url() -> str:
    """Get the remote URL of the git repository.

    :return: the remote URL
    :raises RuntimeError: if the git command fails
    """
    command = ["git", "remote", "-v"]
    result = subprocess.run(  # noqa: S603
        command, cwd=PROJECT_DIR, capture_output=True, text=True, check=True
    )
    if result.returncode == 0:
        output = result.stdout.strip()
        lines = output.split("\n")
        if lines:
            return lines[0].split()[1]

    msg = f"Error: git remote -v returned {result.returncode}"
    raise RuntimeError(msg)


def _extract_metadata() -> EtreeElement:
    """Extract metadata from pyproject.toml and git."""
    with PYPROJECT_TOML.open("rb") as toml_file:
        toml_data = tomllib.load(toml_file)
    project_data = toml_data["project"]

    remote_url = _get_git_remote_url()

    return new_metadata(
        title=f"{project_data['name']} {project_data['version']}",
        creator=",".join([x["name"] for x in project_data["authors"]]),
        description=project_data["description"],
        source=remote_url,
        relation="https://github.com/vim/vim",
        rights="https://github.com/vim/vim/blob/master/LICENSE",
    )


def _new_background() -> EtreeElement:
    """Build the white background beneath the entire logo."""
    ltr_m = gap_polygon(letter_m_mask, shared.BG_OUTLINE_WIDTH + IM_STROKE_WIDTH)
    background = [
        gap_polygon(v_outer, shared.BG_OUTLINE_WIDTH + V_STROKE_WIDTH),
        gap_polygon(
            diamond_outer, shared.BG_OUTLINE_WIDTH + params_diamond.STROKE_WIDTH
        ),
    ]
    background_paths = get_polygon_union(*background, ltr_m)
    svgd = new_data_string(*background_paths)
    fill: dict[str, str | float] = {"fill": shared.BACKGROUND_COLOR}
    if shared.BACKGROUND_OPACITY != 1:
        fill["opacity"] = shared.BACKGROUND_OPACITY
    return su.new_element("path", id_="background", d=svgd, **fill)


def _new_outlines() -> EtreeElement:
    """Build a black shape beneath all colored logo elements.

    What isn't covered later will be outlines around the colored areas.
    """
    outlines = [diamond_cpts.ol, *im_cpts.outlines, v_cpts.ol]
    paths = get_polygon_union(*outlines)
    svgd = new_data_string(*paths)
    return su.new_element("path", id_="outlines", d=svgd, fill=shared.OUTLINE_COLOR)


def _sub_vim(cpts: list[tuple[float, float]]) -> list[list[tuple[float, float]]]:
    """Subtract the V and im mask from the given polygon points."""
    return get_polygon_union(
        cpts,
        im_cpts.mask_outline,
        *im_cpts.outlines,
        v_cpts.ol,
        negative={1, 2, 3, 4, 5},
    )


def _sub_im(cpts: list[tuple[float, float]]) -> list[list[tuple[float, float]]]:
    """Subtract the im mask from the given polygon points."""
    return get_polygon_union(
        cpts, im_cpts.mask_outline, *im_cpts.outlines, negative={1, 2, 3, 4}
    )


def _new_diamond_face() -> EtreeElement:
    paths = _sub_vim(diamond_cpts.face)
    svgd = new_data_string(*paths)
    fill = rgb_to_hex(diamond_shader((0, 0, 1)))
    return su.new_element("path", id_="diamond_face", d=svgd, fill=fill)


def _new_diamond_bevels() -> list[EtreeElement]:
    bevels = [diamond_cpts.q1, diamond_cpts.q2, diamond_cpts.q3, diamond_cpts.q4]
    paths = [_sub_vim(x) for x in bevels]
    svgds = [new_data_string(*x) for x in paths]
    ids = [f"diamond_bevel_q{i}" for i in range(1, 5)]
    fills = [illuminate_bevel(x) for x in bevels]
    return [
        su.new_element("path", id_=ids[i], d=svgds[i], fill=fills[i]) for i in range(4)
    ]


def _new_v_face() -> EtreeElement:
    paths = _sub_im(v_cpts.face)
    svgd = new_data_string(*paths, *im_cpts.faces)
    return su.new_element("path", id_="letter_faces", d=svgd, fill=shared.VIM_GRAY)


def _new_dim_bevels() -> EtreeElement:
    bevels = v_cpts.dim_bevels
    paths = [_sub_im(x) for x in bevels]
    svgds = [new_data_string(*x) for x in paths]
    svgd = "".join(svgds)
    return su.new_element("path", id_="dim_bevels", d=svgd, fill=shared.GRAY_DIM)


def _new_lit_bevels() -> EtreeElement:
    bevels = v_cpts.lit_bevels
    paths = [_sub_im(x) for x in bevels]
    svgds = [new_data_string(*x) for x in paths]
    svgd = "".join(svgds)
    return su.new_element("path", id_="lit_bevels", d=svgd, fill=shared.GRAY_LIT)


def _get_logo_bounds(*elems: EtreeElement) -> su.BoundingBox:
    """Return a square bounding box centered on the diamond.

    :param elems: the all elements in the svg (will be flat in this project).
    :return: bounding box around the entire logo

    As long as the logo is built the way it's always been built, the diamond will be
    the max extent of the logo on all sides, but the `im` is close, and this function
    allows for broader parameterization.
    """
    all_cpts: list[tuple[float, float]] = []
    for elem in elems:
        cpts = get_cpts_from_svgd(elem.attrib.get("d", ""))
        all_cpts.extend((x, y) for p in cpts for x, y in p)
    xs: tuple[float, ...]
    ys: tuple[float, ...]
    xs, ys = zip(*all_cpts, strict=True)
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    max_ext = max(
        max_x - shared.VIEW_CENTER[0],
        max_y - shared.VIEW_CENTER[1],
        shared.VIEW_CENTER[0] - min_x,
        shared.VIEW_CENTER[1] - min_y,
    )
    return su.BoundingBox(
        shared.VIEW_CENTER[0] - max_ext,
        shared.VIEW_CENTER[1] - max_ext,
        max_ext * 2,
        max_ext * 2,
    )


def write_vim_logo(output_path: Path | str = OUTPUT / "vimlogo.svg") -> None:
    """Write the vim logo to a file.

    :param output_path: path to write the svg to
    """
    elems = [
        _extract_metadata(),
        _new_background(),
        _new_outlines(),
        _new_diamond_face(),
        *_new_diamond_bevels(),
        _new_v_face(),
        _new_dim_bevels(),
        _new_lit_bevels(),
    ]
    bbox = su.pad_bbox(_get_logo_bounds(*elems), shared.PAD)
    root = su.new_svg_root_around_bounds(bbox, *elems)
    _ = sys.stdout.write("Writing svg to " + str(output_path) + "\n")
    _ = su.write_svg(output_path, root)


if __name__ == "__main__":
    write_vim_logo()
