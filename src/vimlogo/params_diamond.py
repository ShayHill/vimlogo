"""Parameterization for diamond.py.

Diamond parameters only are in a separate file so the "shared" module can import
them. The diamond ID and stroke width are used to calculate the viewbox. The elements
themselves cannot be examined for max extent because they have the m-mask removed
from them.

:author: Shay Hill
:created: 2024-01-10
"""

from vimlogo.reference_paths import (
    get_dims,
    ref_diamond_inner,
    ref_diamond_oline,
    ref_diamond_outer,
)

# ===============================================================================
#   dimensions and parameters inferred from reference image
# ===============================================================================

# outside (of bevels) diameter (point to point through the center) of the diamond
OD = sum(get_dims(ref_diamond_outer)) / 2

# inside (of bevels) diameter (point to point through the center) of the diamond face
ID = sum(get_dims(ref_diamond_inner)) / 2

# stroke width diameter (point to point through the center) of the diamond. In the
# reference image, the fat, black stroke around the diamond is a black polygon
# itself, not a stroke of a polygon.
_SD = sum(get_dims(ref_diamond_oline)) / 2
STROKE_WIDTH = (_SD - OD) / pow(2, 1 / 2) / 2

LIGHT_LOCATION = (-1, -2, 0)

VIM_GREEN = "#009933"

DIAMOND_MATERIAL_BASE = VIM_GREEN
DIAMOND_MATERIAL_COOL = "#0000ff"
DIAMOND_MATERIAL_WARM = "#ffff00"
DIAMOND_MATERIAL_COOL_COLOR_RATIO = 0.25
DIAMOND_MATERIAL_WARM_COLOR_RATIO = 0.75
DIAMOND_MATERIAL_COOL_LUM_SCALAR = 3 / 4
DIAMOND_MATERIAL_WARM_LUM_SCALAR = 5 / 3
