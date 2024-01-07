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

:author: Shay Hill
:created: 2023-12-31
"""

import dataclasses
from typing import Annotated

from basic_colormath import (
    float_tuple_to_8bit_int_tuple,
    hex_to_rgb,
    hsl_to_rgb,
    rgb_to_hex,
    rgb_to_hsl,
)
from paragraphs import par

from vim_logo import vec3
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


def _rgb_to_intensity(rgb: RGB) -> Vec3:
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
    hue_shift: float
    sat_shift: float
    shine: float = _SHINE_IS_MEANINGLESS_FOR_BEVELS

    def __init__(
        self,
        hex_color: str,
        ambient: float = 0.1,
        diffuse: float = 0.6,
        specular: float = 0.3,
        hue_shift: float = 0.0,
        sat_shift: float = 50
        # TODO: implement hue_shift
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
        self.sat_shift = sat_shift
        self.shine = 1


def interp3(vec_a: Vec3, vec_b: Vec3, time: float) -> Vec3:
    time = min(max(time, 0), 1)
    contrib_a = vec3.scale(vec_a, 1 - time)
    contrib_b = vec3.scale(vec_b, time)
    return vec3.vsum(contrib_a, contrib_b)


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
    """
    normal_vector = vec3.normalize(normal_vector)
    colors = [
        uniform_shading_model(normal_vector, material, light_source)
        for light_source in light_sources
    ]
    sum_vector = vec3.clamp(vec3.vsum(*colors))
    return _intensity_to_hex(sum_vector)


def set_material_color(
    normal_vector: Vec3, material: Material, *light_sources: LightSource
) -> Material:
    """Set the color of the material to create a given color at a specific point.

    :param normal_vector: a normalized vector perpendicular to the face
    :param material: the material of the face
    :param light_sources: the light sources
    :return: None

    Reset the material color so that the output color in these lighting conditions is
    equal to the input material color.
    """
    goal_color = material.rgb_color

    material.color = (1, 1, 1)
    test_white = hex_to_rgb(illuminate(normal_vector, material, *light_sources))
    material.color = (0, 0, 0)
    test_black = hex_to_rgb(illuminate(normal_vector, material, *light_sources))
    is_too_dim = any(x < y for x, y in zip(test_white, goal_color))
    is_too_bright = any(x > y for x, y in zip(test_black, goal_color))

    if is_too_dim or is_too_bright:
        msg = par(
            f"""Material and LightSource parameters can only create colors in the
            range {test_black} to {test_white} at given normal vector. The goal color
            is {goal_color}"""
        )
        raise ValueError(msg)

    candidate: list[int] = [0, 0, 0]
    while True:
        material.rgb_color = (candidate[0], candidate[1], candidate[2])
        attempt = hex_to_rgb(illuminate(normal_vector, material, *light_sources))
        # if any(x > y for x, y in zip(attempt, goal_color)):
        #     msg = par(
        #         f"""Unexpected (floating-point?) error. Failed to duplicate
        #         {goal_color}. Reached {material.rgb_color}."""
        #     )
        #     raise RuntimeError(msg)
        if all(x >= y for x, y in zip(attempt, goal_color)):
            break
        for i in range(3):
            if attempt[i] < goal_color[i]:
                candidate[i] += 1
    return material
