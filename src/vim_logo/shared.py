"""Constants and shared elements.

:author: Shay Hill
:created: 2024-01-03
"""

from vim_logo.illumination import LightSource

# the fat black outlines around the V and diamond
FAT_STROKE_COLOR = "#000000"
FAT_STROKE_WIDTH = 12

# the medium black outlines around the m and i
MID_STROKE_COLOR = "#000000"
MID_STROKE_WIDTH = 6

# the tiny pinstripes on the bevels of the V and diamond
PIN_STROKE_COLOR = "#000000"
PIN_STROKE_WIDTH = 1 / 6

# colors for V, im, and diamond
VIM_GRAY = "#aaaaaa"
VIM_GREEN = "#009933"

# the light source for V and diamond bevels
LIGHT_SOURCES = [
    LightSource("#ffffff", (-9, -12, 24)),
    LightSource("#ffffff", (-9, -12, 24)),
]
