"""Constants and shared elements.

:author: Shay Hill
:created: 2024-01-03
"""

from vim_logo import vec3
import vec2_math as vec2
from basic_colormath import rgb_to_hex

VIEWBOX = (0, 0, 293.57495, 293.80619)
VIEW_CENTER = vec2.vscale(vec2.vadd(VIEWBOX[:2], VIEWBOX[2:]), 0.5)

# the fat black outlines around the V and diamond
FAT_STROKE_COLOR = "#000000"
FAT_STROKE_WIDTH = 11.5
FAT_STROKE = {"stroke": FAT_STROKE_COLOR, "stroke-width": FAT_STROKE_WIDTH}

# the medium black outlines around the m and i
MID_STROKE_COLOR = "#000000"
MID_STROKE_WIDTH = 6
MID_STROKE = {"stroke": MID_STROKE_COLOR, "stroke-width": MID_STROKE_WIDTH}

# the tiny pinstripes on the bevels of the V and diamond
PIN_STROKE_COLOR = "#000000"
PIN_STROKE_WIDTH = 0.216 # copied from reference svg. Consistently used there.
PIN_STROKE = {"stroke": PIN_STROKE_COLOR, "stroke-width": PIN_STROKE_WIDTH}

# colors for V, im, and diamond
VIM_GRAY = "#cccccc"
GRAY_LIT = "#ffffff"
GRAY_DIM = "#7f7f7f"
VIM_GREEN = "#009933"

