"""Constants shared between diamond.py and letters plus specific to letters.

:author: Shay Hill
:created: 2024-01-03
"""

import vec2_math as vec2

from vimlogo import params_diamond
from vimlogo.reference_paths import (
    get_dims,
    ref_background,
    ref_background_stroke_width,
    ref_diamond_oline,
)

BACKGROUND_COLOR = "#ffffff"
OUTLINE_COLOR = "#000000"

# Read the width of the white background stripe around the logo from the reference
# svg.
bg_w = get_dims(ref_background)[0]
di_w = get_dims(ref_diamond_oline)[0]
stroke = ref_background_stroke_width
BG_OUTLINE_WIDTH = (bg_w - di_w) / 2 / pow(2, 1 / 2) + stroke / 2

# the viewbox around the entire logo. The diamond is centered in the viewbox.
PAD = 1
_geometry_width = (
    params_diamond.OD
    + 2 * params_diamond.STROKE_WIDTH * pow(2, 1 / 2)
    + 2 * BG_OUTLINE_WIDTH * pow(2, 1 / 2)
)
VIEWBOX = (0, 0, _geometry_width + PAD, _geometry_width + PAD)
VIEW_CENTER = vec2.vscale(vec2.vadd(VIEWBOX[:2], VIEWBOX[2:]), 0.5)

# the tiny pinstripes on the bevels of the V and diamond.
PIN_STROKE_WIDTH = 0.216 # copied from reference svg. Consistently used there.

# colors for Vim
VIM_GRAY = "#cccccc"
GRAY_LIT = "#ffffff"
GRAY_DIM = "#7f7f7f"

