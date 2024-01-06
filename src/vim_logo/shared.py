"""Constants and shared elements.

:author: Shay Hill
:created: 2024-01-03
"""

from vim_logo.illumination import LightSource
from vim_logo import vec3
import vec2_math as vec2
from basic_colormath import rgb_to_hex

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
PIN_STROKE_WIDTH = 1 / 4
PIN_STROKE = {"stroke": PIN_STROKE_COLOR, "stroke-width": PIN_STROKE_WIDTH}

# colors for V, im, and diamond
VIM_GRAY = "#cccccc"
GRAY_LIT = "#ffffff"
GRAY_DIM = "#7f7f7f"
VIM_GREEN = "#009933"

# the light source for V and diamond bevels

_total_intensity = 24
_light_sources = 24

LIGHT_SOURCES: list[LightSource] = []
intensity = 255 * _total_intensity / _light_sources
color = rgb_to_hex((intensity, intensity, intensity))
pnt_a = (-24, 0, 4)
pnt_b = (0, -24, 4)
for i in range(_light_sources):
    time = i / (_light_sources - 1)
    contrib_a = vec3.scale(pnt_a, 1 - time)
    contrib_b = vec3.scale(pnt_b, time)
    pnt = vec3.add(contrib_a, contrib_b)
    print(pnt)
    LIGHT_SOURCES.append(LightSource(color, pnt))

    # LightSource(color, (-9, -12, 9)),
    # LightSource("#ffffff", (-9, -12, 9)),
    # # LightSource("#ffffff", (-9, -12, 24)),
# ]

