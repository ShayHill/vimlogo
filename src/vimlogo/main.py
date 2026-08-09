"""Construct the svg from parts.

:author: Shay Hill
:created: 2024-01-10
"""

import copy
import subprocess
import sys
import tomllib
from pathlib import Path

import svg_ultralight as su
from lxml.etree import _Element as EtreeElement  # pyright: ignore[reportPrivateUsage]
from svg_ultralight import new_metadata

from vimlogo import params_diamond, shared
from vimlogo.diamond import diamond_cpts, diamond_outer, illuminate_bevel
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
    ltr_m = gap_polygon(letter_m_mask, shared.FULL_OLINE_WIDTH + IM_STROKE_WIDTH)
    background = [
        gap_polygon(v_outer, shared.FULL_OLINE_WIDTH + V_STROKE_WIDTH),
        gap_polygon(
            diamond_outer, shared.FULL_OLINE_WIDTH + params_diamond.STROKE_WIDTH
        ),
    ]
    background_paths = get_polygon_union(*background, ltr_m)
    svgd = new_data_string(*background_paths)
    return su.new_element(
        "path", id_="background", d=svgd, fill=shared.FULL_OLINE_COLOR
    )


def _new_outlines() -> EtreeElement:
    """Build a black shape beneath all colored logo elements.

    What isn't covered later will be outlines around the colored areas.
    """
    outlines = [diamond_cpts.ol, *im_cpts.ols, v_cpts.ol]
    paths = get_polygon_union(*outlines)
    svgd = new_data_string(*paths)
    return su.new_element("path", id_="outlines", d=svgd, fill=shared.K_STROKE)


def sub_vim(cpts: list[tuple[float, float]]) -> list[list[tuple[float, float]]]:
    return get_polygon_union(
        cpts, im_cpts.mask_ol, *im_cpts.ols, v_cpts.ol, negative={1, 2, 3, 4, 5}
    )


def sub_im(cpts: list[tuple[float, float]]) -> list[list[tuple[float, float]]]:
    return get_polygon_union(cpts, im_cpts.mask_ol, *im_cpts.ols, negative={1, 2, 3, 4})


def _new_diamond_face() -> EtreeElement:
    paths = sub_vim(diamond_cpts.face)
    svgd = new_data_string(*paths)
    return su.new_element("path", id_="diamond_face", d=svgd, fill=shared.VIM_GREEN)


def _new_diamond_bevels() -> list[EtreeElement]:
    bevels = [diamond_cpts.q1, diamond_cpts.q2, diamond_cpts.q3, diamond_cpts.q4]
    paths = [sub_vim(x) for x in bevels]
    svgds = [new_data_string(*x) for x in paths]
    ids = [f"diamond_bevel_q{i}" for i in range(1, 5)]
    fills = [illuminate_bevel(x) for x in bevels]
    return [
        su.new_element("path", id_=ids[i], d=svgds[i], fill=fills[i]) for i in range(4)
    ]


def _new_v_face() -> EtreeElement:
    paths = sub_im(v_cpts.face)
    svgd = new_data_string(*paths, *im_cpts.faces)
    return su.new_element("path", id_="letter_faces", d=svgd, fill=shared.VIM_GRAY)


def _new_dim_bevels() -> EtreeElement:
    bevels = v_cpts.dim_bevels
    paths = [sub_im(x) for x in bevels]
    svgds = [new_data_string(*x) for x in paths]
    svgd = "".join(svgds)
    return su.new_element("path", id_="dim_bevels", d=svgd, fill=shared.GRAY_DIM)


def _new_lit_bevels() -> EtreeElement:
    bevels = v_cpts.lit_bevels
    paths = [sub_im(x) for x in bevels]
    svgds = [new_data_string(*x) for x in paths]
    svgd = "".join(svgds)
    return su.new_element("path", id_="lit_bevels", d=svgd, fill=shared.GRAY_LIT)


def write_vim_logo(output_path: Path | str = OUTPUT / "vimlogo.svg") -> None:
    """Write the vim logo to a file.

    :param output_path: path to write the svg to
    """
    root = su.new_svg_root(
        x_=shared.VIEWBOX[0],
        y_=shared.VIEWBOX[1],
        width_=shared.VIEWBOX[2],
        height_=shared.VIEWBOX[3],
        print_width_=shared.VIEWBOX[2],
    )

    root.append(_extract_metadata())
    root.append(_new_background())
    root.append(_new_outlines())
    root.append(_new_diamond_face())
    root.extend(_new_diamond_bevels())
    root.append(_new_v_face())
    root.append(_new_dim_bevels())
    root.append(_new_lit_bevels())
    _ = sys.stdout.write("Writing svg to " + str(output_path) + "\n")
    _ = su.write_svg(output_path, root)


if __name__ == "__main__":
    write_vim_logo()
