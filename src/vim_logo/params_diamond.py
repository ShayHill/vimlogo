"""Parameterization for diamond.py

These are in a separate file so the shared parameter can import them. The viewbox is
scaled by the diamond OD and the white stroke width around the entire shape is a
functioin of the diamond STROKE_WIDTH.

:author: Shay Hill
:created: 2024-01-10
"""

from vim_logo.reference_paths import (
    get_dims,
    ref_diamond_inner,
    ref_diamond_outer,
    ref_diamond_oline,
)

# ===============================================================================
#   dimensions and parameters hand-tuned
# ===============================================================================


# effects the calculated surface normal of the bevels and thus the illumination.
# Increase this to maked the bevels less colorful.
BEVEL_SLOPE = 1.5


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
STROKE_WIDTH = (_SD - OD) / pow(2, 1 / 2)
