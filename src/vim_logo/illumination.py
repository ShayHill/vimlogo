"""Illuminate bevels of objects.

A simple illumination model for the bevels of objects. This is the Uniform Shading
Model described
[here](https://www.clear.rice.edu/comp360/lectures/fall2008/slides/ShadingNew.pdf).
I've included some pointless renaming of variables to match the notation in the
slides. I've also included the shininess attribute, even though I've given no way of
setting it (it is meaningless for a beveled surface). It's there so I can borrow this
code later.

The idea is to weigh ambient, diffuse, and specular light sources to get a color for
a planar face. The ambient and specular colors will be the color of the material. The
specular color will be the color of the light source.

The reference image had some hue shift due to clipping. I wanted to add a little hue
shift the right way, not by accidentally getting there without clipping. To get a
create bevels for a shared.VIM_GREEN face, I used a slightly bluer material with
yellow lights. Where the bevels are in shadow (mostly ambient light), they are more
blue. Where the bevels are highlighted by bright yellow light, specular illumation
makes them more yellow. I did not use illumination code for the face. I just used an
explicit face color.

:author: Shay Hill
:created: 2023-12-31
"""

import dataclasses
import math
from typing import Annotated

import vec2_math as vec2
from basic_colormath import (
    float_tuple_to_8bit_int_tuple,
    hex_to_rgb,
    hsl_to_rgb,
    rgb_to_hex,
    rgb_to_hsl,
)

from vim_logo import shared, vec3
from vim_logo.vec3 import Vec3

RGB = Annotated[tuple[int, int, int], [0, 255]]


# hard-coded viewer location abouve the xy plane in a right-handed coordinate system.
_VIEWER = (0, 0, 1)

# shine is implemented here if I choose to reuse this code for smoother surfaces.
_SHINE_IS_MEANINGLESS_FOR_BEVELS = 1


def _intensity_to_rgb(color: Vec3) -> RGB:
    """Convert a color tuple in the float interval [0, 1] to the int interval [0, 255].

    :param color: a color tuple in the interval [0, 1]
    :return: a color tuple in the interval [0, 255]
    """
    r, g, b = (x * 255 for x in color)
    return float_tuple_to_8bit_int_tuple((r, g, b))


def _rgb_to_intensity(rgb: Vec3) -> Vec3:
    """Convert a color tuple in the int interval [0, 255] to the float interval [0, 1].

    :param rgb: a color tuple in the interval [0, 255]
    :return: a color tuple in the interval [0, 1]
    """
    r, g, b = (x / 255 for x in rgb)
    return (r, g, b)


def _intensity_to_hex(color: Vec3) -> str:
    """Convert a color tuple in the float interval [0, 1] to a hex string.

    :param color: a color tuple in the interval [0, 1]
    :return: a hex string
    """
    rgb = _intensity_to_rgb(color)
    return rgb_to_hex(rgb)


def _hex_to_intensity(hex_str: str) -> Vec3:
    """Convert a hex string to a color tuple in the float interval [0, 1].

    :param hex: a hex string
    :return: a color tuple in the interval [0, 1]
    """
    r, g, b = hex_to_rgb(hex_str)
    return _rgb_to_intensity((r, g, b))


def _intensity_to_hsl(color: Vec3) -> Vec3:
    """Convert a float tuple in the float interval [0, 1] to a hsl tuple.

    :param color: a color tuple in the interval [0, 1]
    :return: an hsl tuple
    """
    r, g, b = _intensity_to_rgb(color)
    return rgb_to_hsl((r, g, b))


def _hsl_to_intensity(hsl: Vec3) -> Vec3:
    """Convert a hsl tuple to a color tuple in the float interval [0, 1].

    :param hsl: an hsl tuple
    :return: a color tuple in the interval [0, 1]
    """
    r, g, b = hsl_to_rgb(hsl)
    return _rgb_to_intensity((r, g, b))


@dataclasses.dataclass
class _SetsColor:
    color: Vec3

    @property
    def hex_color(self) -> str:
        """Return the color of the light source as a hex string."""
        return _intensity_to_hex(self.color)

    @hex_color.setter
    def hex_color(self, hex_str: str) -> None:
        """Set the color of the light source from a hex string."""
        self.color = _hex_to_intensity(hex_str)

    @property
    def rgb_color(self) -> RGB:
        """Return the color of the light source as a tuple of ints in [0, 255]."""
        return _intensity_to_rgb(self.color)

    @rgb_color.setter
    def rgb_color(self, rgb: RGB) -> None:
        """Set the color of the light source from a tuple of ints in [0, 255]."""
        self.color = _rgb_to_intensity(rgb)

    @property
    def hsl_color(self) -> Vec3:
        """Return the color of the light source as a tuple of ints in [0, 255]."""
        return _intensity_to_hsl(self.color)

    @hsl_color.setter
    def hsl_color(self, hsl: Vec3) -> None:
        """Set the color of the light source from a tuple of ints in [0, 255]."""
        self.color = _hsl_to_intensity(hsl)


@dataclasses.dataclass
class LightSource(_SetsColor):
    """A light source defined by a color and a direction."""

    color: Vec3
    direction: Vec3

    def __init__(self, hex_color: str, direction: Vec3) -> None:
        """Initialize a light source.

        :param hex_color: the color of the light source. Provide this as a hex string
            (e.g., "#ffffff"). This will be converted to a tuple of floats in the
            interval [0, 1].
        :param location: the location of the light source. The light source will be,
            in effect, located infinitely far from the origin in the direction of
            this vector.

        Scale color to a tuple of floats in the interval [0, 1]. Normalize direction.
        """
        self.hex_color = hex_color
        self.direction = vec3.normalize(direction)


@dataclasses.dataclass
class Material(_SetsColor):
    """A material to simulate basic normal (phong model) illumination."""

    color: Vec3
    ambient: float
    diffuse: float
    specular: float
    shine: float = _SHINE_IS_MEANINGLESS_FOR_BEVELS

    def __init__(
        self,
        hex_color: str,
        ambient: float = 0.1,
        diffuse: float = 0.6,
        specular: float = 0.3,
    ) -> None:
        """Initialize a material.

        :param hex_color: the color of the material. Provide this as a hex string
            (e.g., "#cccccc").  Internally, this is stored as a tuple of floats in
            [0, 1]
        :param ambient: [0, 1] the ambient component of the material. This is the
            amount of light that is reflected from the material regardless of the
            direction of the light source.
        :param diffuse: [0, 1] the diffuse component of the material. This is normal
            illumination.
        :param specular: [0, 1] the specular component of the material. This is an
            approximation of the shine of the material. Specular reflection is why
            typical black materials can still be seen in a dark room.

        Convert material color to a tuple of floats in the interval [0, 1]. Scale
        ambient, diffuse, and specular to sum to 1.
        """
        self.hex_color = hex_color

        sum_illumination = ambient + diffuse + specular
        self.ambient = ambient / sum_illumination
        self.diffuse = diffuse / sum_illumination
        self.specular = specular / sum_illumination
        self.shine = 1


def uniform_shading_model(
    normal_vector: Vec3, material: Material, light_source: LightSource
) -> Vec3:
    """Compute the Uniform Shading Model to get the illuminated color of a face.

    :param normal_vector: a normalized vector perpendicular to the face
    :param material: the material of the face
    :param light_source: the light source
    :return: the color of the face

    WARNING: The return value is unbounded. You will probably want to clamp it to
    [0, 1] at some point, but it is not clamped here to allow for averaging of
    multiple light sources.
    """
    material.color = vec3.clamp(material.color)

    I_a = material.color
    I_d = material.color
    I_s = light_source.color

    # weights
    k_a = material.ambient
    k_d = material.diffuse
    k_s = material.specular

    N = normal_vector
    L = light_source.direction
    L_dot_N = vec3.dot(L, N)

    R = vec3.subtract(vec3.scale(N, 2 * L_dot_N), L)

    V = _VIEWER
    R_dot_V = vec3.dot(R, V)

    a_term = vec3.scale(I_a, k_a)
    d_term = vec3.scale(vec3.multiply(I_d, I_s), k_d * max(0, L_dot_N))
    s_term = vec3.scale(I_s, k_s * max(0, R_dot_V) ** material.shine)

    return vec3.vsum(a_term, d_term, s_term)


def illuminate(
    normal_vector: Vec3, material: Material, *light_sources: LightSource
) -> str:
    """Compute the Uniform Shading Model with multiple light sources.

    :param normal_vector: a normalized vector perpendicular to the face
    :param material: the material of the face
    :param light_sources: the light sources

    Unlike the function uniform_shading_model, this function will normalize the
    normal_vector for you.

    When using multiple light sources, the diffuse and specular animations will
    stack, the ambient will not.
    """
    material.ambient /= len(light_sources)
    normal_vector = vec3.normalize(normal_vector)
    colors = [
        uniform_shading_model(normal_vector, material, light_source)
        for light_source in light_sources
    ]
    sum_vector = vec3.clamp(vec3.vsum(*colors))
    material.ambient *= len(light_sources)
    return _intensity_to_hex(sum_vector)


# ===============================================================================
#   light sources for  the diamond bevels
# ===============================================================================

LIGHT_LOCATION = (-4, -6, 2)

# Because of the way I implemented light sources, a light source can only be 255
# bright, so intensity greater than 255 will require multiple light sources. If you
# change the light location or some other variable, you may have to adjust the light
# intensity. An error message will guide you. You will not be able to use fully
# desaturated colors, because some specular lighting is hard coded in.
LIGHT_COLOR = (1, 1, 1 / 16)
LIGHT_INTENSITY = 1000
LIGHTS = min(360, LIGHT_INTENSITY)

intensity_per_light = LIGHT_INTENSITY / LIGHTS


def _get_light_ring() -> list[LightSource]:
    """Use module-wide values to create a ring of light sources.

    Light sources near the specified LIGHT_LOCATION will be brighter.
    """
    pnt_x, pnt_y = LIGHT_LOCATION[:2]
    angles = [2 * math.pi * i / LIGHTS for i in range(LIGHTS)]
    locs = [vec2.vrotate((pnt_x, pnt_y), x) for x in angles]
    lits = [math.pi - abs(vec2.get_signed_angle((pnt_x, pnt_y), x)) for x in locs]
    lits = [pow(x, 3) for x in lits]
    lits = [x * LIGHT_INTENSITY / sum(lits) for x in lits]

    light_sources: list[LightSource] = []
    for loc, lit in zip(locs, lits):
        rgb = (lit * LIGHT_COLOR[0], lit * LIGHT_COLOR[1], lit * LIGHT_COLOR[2])
        if max(rgb) == 0:
            continue
        light_sources.append(LightSource(rgb_to_hex(rgb), (*loc, LIGHT_LOCATION[2])))
    return light_sources


LIGHT_SOURCES = _get_light_ring()


def _push_hsl(
    color: str, hue_shift: float = 0, sat_shift: float = 0, lit_shift: float = 0
) -> str:
    """Shift the hue, saturation, and lightness of a color.

    :param color: hex color str, e.g., "#ff3322"
    :param hue_shift: -365 to 365, maximum amount to change hue
    :param sat_shift: -100 to 100, maximum amount to change saturation
    :param lit_shift: -100 to 100, maximum amount to change lightness
    :return: (r, g, b)

    The intermediate hue, sat, and lit values are in the ranges
    [0, 365), [0, 100], and [0, 100].
    """
    hue, sat, lit = rgb_to_hsl(hex_to_rgb(color))
    hue = (hue + hue_shift) % 365
    sat = max(0, min(100, sat + sat_shift))
    lit = max(0, min(100, lit + lit_shift))
    return rgb_to_hex(hsl_to_rgb((hue, sat, lit)))


# ===============================================================================
#   material for the diamond bevels
# ===============================================================================

diamond_material = Material(
    _push_hsl(shared.VIM_GREEN, hue_shift=30, sat_shift=-30, lit_shift=16),
    ambient=3.5,
    diffuse=5,
    specular=1.5,
)
