"""Construct the svg from parts.

:author: Shay Hill
:created: 2024-01-10
"""

import copy
import sys
from pathlib import Path

from lxml.etree import _Element as EtreeElement # type: ignore
import svg_ultralight as su

from vim_logo import params_diamond, shared
from vim_logo.diamond import diamond, diamond_outer
from vim_logo.glyphs import gap_polygon, get_polygon_union, new_data_string
from vim_logo.letter_v import V_STROKE_WIDTH, elem_v, v_outer
from vim_logo.paths import PYPROJECT_TOML
from vim_logo.letters_im import (
    IM_STROKE_WIDTH,
    elem_im,
    letter_m_pts,
    letter_m_pts_mask,
)
import subprocess
from vim_logo.paths import OUTPUT, PROJECT_DIR
from svg_ultralight import new_metadata


import tomllib


def _get_git_remote_url():
    command = ['git', 'remote', '-v']
    result = subprocess.run(command, cwd=PROJECT_DIR, capture_output=True, text=True)
    if result.returncode == 0:
        output = result.stdout.strip()
        lines = output.split('\n')
        if lines:
            # Extract remote URL from the first line
            first_line = lines[0]
            remote_url = first_line.split()[1]
            return remote_url
    # Return None if the command fails or no remote URL was found
    return None


def _extract_metadata() -> EtreeElement:
    """Extract metadata from pyproject.toml and git.
    """
    with open(PYPROJECT_TOML, 'rb') as toml_file:
        toml_data = tomllib.load(toml_file)
    project_data = toml_data['project']

    remote_url = _get_git_remote_url()
    assert remote_url

    return new_metadata(
        title = f"{project_data['name']} {project_data['version']}",
        creator = ",".join([x['name'] for x in project_data['authors']]),
        description = project_data['description'],
        source = remote_url,
        relation = "https://github.com/vim/vim",
        rights = "https://github.com/vim/vim/blob/master/LICENSE"
    )



def write_vim_logo(output_path: Path | str = OUTPUT / "vim_logo.svg"):
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

    if shared.FULL_OLINE_WIDTH > IM_STROKE_WIDTH / 2:
        ltr_m = gap_polygon(
            letter_m_pts_mask, shared.FULL_OLINE_WIDTH + IM_STROKE_WIDTH
        )
    else:
        ltr_m = gap_polygon(letter_m_pts, shared.FULL_OLINE_WIDTH + IM_STROKE_WIDTH)
    background = [
        gap_polygon(v_outer, shared.FULL_OLINE_WIDTH + V_STROKE_WIDTH),
        gap_polygon(
            diamond_outer, shared.FULL_OLINE_WIDTH + params_diamond.STROKE_WIDTH
        ),
    ]
    background_paths = get_polygon_union(
        *background, letter_m_pts_mask, ltr_m, negative={2}
    )
    d_background = new_data_string(*background_paths)
    root.append(
        su.new_sub_element(
            root,
            "path",
            id_ = "background",
            d=d_background,
            fill=shared.FULL_OLINE_COLOR,
        )
    )

    root.append(diamond)

    for element in [elem_v, elem_im]:
        root.append(copy.deepcopy(element))

    _ = sys.stdout.write("Writing svg to " + str(output_path) + "\n")
    _ = su.write_svg(output_path, root)


if __name__ == "__main__":
    write_vim_logo()
