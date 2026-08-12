"""Implement a Gooch-ish shading algorithm.

The original Gooch model is a linear interpolation between a cooled and a warmed base
color: https://dl.acm.org/doi/epdf/10.1145/280814.280950

This is a similar idea, but the parameters are different, and the model is guaranteed
to give you the base color when the light is perpendicular to the viewing angle. So,
for the Vim logo diamond, the face of the diamond will always be the true color as
long as your light source lies on the xy plane.

The interpolation gives you all of your specular, diffuse, and ambient. There is no
other lighting model applied.

Each shade (cool and warm) is cool or warm color mixed with the base at
name_color_ratio. A color from the spline (warm_mix -> base -> cool_mix) is selected
based on the dot product of the light vector and the surface normal (the specular
reflection).

AFTER the color is selected, the luminance is adjusted. This is so a warm color that
gets "blown out" (must lose saturation to match luminance) won't be "blown out" along
the entire spline, only in the brightest parts where it's necessary.

:author: Shay Hill
:created: 2026-08-11
"""

import dataclasses
from collections.abc import Callable, Iterable
from typing import Annotated, TypeAlias

import numpy as np
from basic_colormath import hex_to_rgb
from cubic_bezier_spline import new_open_interpolating_spline
from numpy import typing as npt

_RGB: TypeAlias = Annotated[npt.NDArray[np.floating], "([0..255], [0..255], [0..255])"]
_RGBArg: TypeAlias = tuple[float, float, float] | _RGB | Iterable[float]

_WHITE = np.array([255, 255, 255], dtype=np.float64)
COOL = (0, 0, 255)
WARM = (255, 255, 0)
COOL_LUM_BOOST = 3 / 4
WARM_LUM_BOOST = 1 + 2 / 3
COOL_COLOR_RAT = 0.25
WARM_COLOR_RAT = 0.75

# standard luminance coefficients for RGB to luminance conversion
_RLUM = 0.2126
_GLUM = 0.7152
_BLUM = 0.0722


@dataclasses.dataclass
class Material:
    """Define a Gooch-like shader."""

    base: str
    cool: str
    warm: str
    cool_color_ratio: float
    warm_color_ratio: float
    cool_lum_scalar: float
    warm_lum_scalar: float
    _lums: Callable[[float], float] = dataclasses.field(
        init=False, compare=False, repr=False
    )
    _cols: Callable[[float], _RGB] = dataclasses.field(
        init=False, compare=False, repr=False
    )

    def __post_init__(self) -> None:
        """Initialize the material."""
        cool = self._get_cool()
        base = np.array(hex_to_rgb(self.base))
        warm = self._get_warm()
        self._lums = self._get_lums()
        self._cols = new_open_interpolating_spline(np.array([warm, base, cool]))

    def _get_cool(self) -> _RGB:
        """Get the cool color as an RGB array."""
        base = np.array(hex_to_rgb(self.base), dtype=np.float64)
        cool = np.array(hex_to_rgb(self.cool), dtype=np.float64)
        cool *= 255 / max(cool)
        return cool * self.cool_color_ratio + base * (1 - self.cool_color_ratio)

    def _get_warm(self) -> _RGB:
        """Get the warm color as an RGB array."""
        base = np.array(hex_to_rgb(self.base), dtype=np.float64)
        warm = np.array(hex_to_rgb(self.warm), dtype=np.float64)
        warm *= 255 / max(warm)
        return warm * self.warm_color_ratio + base * (1 - self.warm_color_ratio)

    def _get_lums(self) -> Callable[[float], float]:
        """Get the luminance spline function."""
        base_lum = _get_luminance(np.array(hex_to_rgb(self.base)))
        cool_lum = base_lum * self.cool_lum_scalar
        warm_lum = base_lum * self.warm_lum_scalar
        spline = new_open_interpolating_spline([[warm_lum], [base_lum], [cool_lum]])

        def get_singleton_item_from_spline(t: float) -> float:
            return spline(t)[0]

        return get_singleton_item_from_spline

    def new_shader(self, light_location: _RGBArg) -> Callable[[_RGBArg | float], _RGB]:
        """Create a shader function for this material.

        :return: a function that takes a surface normal or diffuse reflection between
            0 and 1 and returns a color.
        """
        norm_ls = np.array(light_location) / np.linalg.norm(list(light_location))

        def shader(normal_or_diffuse: _RGBArg | float) -> _RGB:
            if isinstance(normal_or_diffuse, (float, int)):
                t = normal_or_diffuse * 2  # [0, 2]
            else:
                normal_or_diffuse = np.array(normal_or_diffuse) / np.linalg.norm(
                    list(normal_or_diffuse)
                )
                t = 1.0 + np.dot(normal_or_diffuse, norm_ls)  # [0, 2]
            color = self._cols(t)
            return _set_luminance(color, self._lums(t))

        return shader


def _get_luminance(color: _RGB) -> float:
    """Get the luminance from 0-255 of a color ([0..255, 0..255, 0..255])."""
    return sum(c * x for c, x in zip(color, (_RLUM, _GLUM, _BLUM), strict=True))


def _set_luminance(color: _RGB, lum: float) -> _RGB:
    """Set the luminance of a color ([0..255, 0..255, 0..255]) to a new value.

    :param color: the color to set the luminance of ([0..255, 0..255, 0..255])
    :param lum: the new luminance value (0-255)
    :return: a color with the same hue as color but with luminance set to lum
    """
    lum_b = _get_luminance(color)
    if lum in {255, 0} or lum_b == 0:
        return np.array([lum, lum, lum])
    scale = lum / lum_b
    max_scale = 255 / max(color)
    if scale <= max_scale:
        return color * scale
    color = color * max_scale
    lum_b = _get_luminance(color)
    ratio = (lum - lum_b) / (255 - lum_b)
    return _WHITE * ratio + color * (1 - ratio)
