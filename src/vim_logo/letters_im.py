"""The lowercase letters i and m in Vim.

The top, right corner of the letter m is the origin. Letters i and m are two g
elements.

This mostly but not exactly follows the existing Vim logo. The m was inconsistent, so
I made it more consistent and a bit closer to the source Crillee font.

:author: Shay Hill
:created: 2023-12-30
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import svg_ultralight as su

if TYPE_CHECKING:
    from lxml.etree import _Element as EtreeElement  # type: ignore

# ===============================================================================
#   Configuration.
# ===============================================================================


_STROKE_WIDTH = 6
_STROKE_COLOR = "#ff0000"
_FILL_COLOR = "#cccccc"

# smaller bevels of the letter i dot
_I_DOT_BEVEL = 1

# larger bevels and height / width of the serifs
_BEVEL = 3

# The top or bottom of the vertical line of the letter i, including the serif. The
# width of the bottom of a vertical bar on the letter m, including the serif.
_STROKE_BOT = 12

# width of the top of a vertical space on the letter m
_M_VOID = 10.5

_H_LINES = [
    -(_M_VOID - _BEVEL) - (_STROKE_BOT - _BEVEL),  # top of i dot (same gap as m legs)
    -(_M_VOID - _BEVEL),  # bottom of i dot
    0,  # top of m and i stroke (x-height)
    _BEVEL,  # bottom of divets on the top of the m
    9,  # top of voids between legs of the letter m
    27,  # top of the lower serif on the m and i stroke
    30,  # baseline
]

# ===============================================================================
#   Path transformations
# ===============================================================================


def _relx_to_absx(pts: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Convert a list of points from relative to absolute coordinates.

    This is tricky, because only the x values will be relative. The y values will
    already be absolute. The x values are describing the shape of the letter, while
    the y values are representative of the font's baseline, x-height, cap height,
    etc.
    """
    absx = [pts[0]]
    for i, pt in enumerate(pts[1:], 1):
        absx.append((absx[i - 1][0] + pt[0], pt[1]))
    return absx


def _skew_point(pt: tuple[float, float]) -> tuple[float, float]:
    """Skew move x coordinate -1 pt for each 3 y pts."""
    x, y = pt
    return x - y / 3, y


# ===============================================================================
#   Letter m subpaths
# ===============================================================================

# the top of an m curve all the way to the start of the next curve. There are two and
# a half of these in the letter m.
curved_top = [
    (_STROKE_BOT - _BEVEL, _H_LINES[2]),
    (_BEVEL, _H_LINES[3]),
    (_M_VOID - _BEVEL * 2, _H_LINES[3]),
    (_BEVEL, _H_LINES[2]),
]

# just above the bottom serif on an m leg to just above the bottom serif on the next
# leg. There are two and a half of these in the letter m. This is also used as a
# transformation to get from a known point on the letter m to a new point on the stem
# of the letter i.
bottom_leg = [
    (_BEVEL, _H_LINES[5]),
    (0, _H_LINES[6]),
    (-_STROKE_BOT, _H_LINES[6]),
    (0, _H_LINES[4]),
    (-_M_VOID, _H_LINES[4]),
    (0, _H_LINES[5]),
]

# ===============================================================================
#   Letter m full path
# ===============================================================================

letter_m_pts = [
    # topmost, leftmost point on top serif
    (0, _H_LINES[2]),
    *curved_top,
    *curved_top,
    *curved_top[:2],
    # rigth vertical line top to bottom
    (0, _H_LINES[5]),
    *bottom_leg,
    *bottom_leg,
    *bottom_leg[:3],
    # left vertical line bottom to top
    (0, _H_LINES[3]),
    (-_BEVEL, _H_LINES[3]),
]

letter_m_pts = _relx_to_absx(letter_m_pts)

# ===============================================================================
#   Letter i stem path
# ===============================================================================


def get_starting_point_of_letter_i() -> tuple[float, float]:
    """Get the point just above the bottom serif of the letter i.

    Treat the i as if it were another vertical bar on the letter m.
    """
    path = [letter_m_pts[-6], *bottom_leg]
    return _relx_to_absx(path)[-1]


letter_i_pts_stem = [
    # just above the bottom serif of the letter i
    get_starting_point_of_letter_i(),
    *bottom_leg[:3],
    (0, _H_LINES[3]),
    (-_BEVEL, _H_LINES[3]),
    (0, _H_LINES[2]),
    (_STROKE_BOT, _H_LINES[2]),
]

letter_i_pts_stem = _relx_to_absx(letter_i_pts_stem)

# ===============================================================================
#   Letter i dot path
# ===============================================================================


side_length = (_H_LINES[1] - _H_LINES[0]) - _I_DOT_BEVEL * 2

letter_i_pts_dot = [
    # clockwise, from top bevel of lower, right corner
    (letter_i_pts_stem[-1][0], _H_LINES[1] - _I_DOT_BEVEL),
    (-_I_DOT_BEVEL, _H_LINES[1]),
    (-side_length, _H_LINES[1]),
    (-_I_DOT_BEVEL, _H_LINES[1] - _I_DOT_BEVEL),
    (0, _H_LINES[0] + _I_DOT_BEVEL),
    (_I_DOT_BEVEL, _H_LINES[0]),
    (side_length, _H_LINES[0]),
    (_I_DOT_BEVEL, _H_LINES[0] + _I_DOT_BEVEL),
]

letter_i_pts_dot = _relx_to_absx(letter_i_pts_dot)


class SvgCommand:
    """Create an svg command string from absolute coordinates.

    This only works for linear splines (commands, "M", "L", "H", and "V").
    """

    def __init__(self, prev: SvgCommand | None, *pts: tuple[float, float]) -> None:
        """Create an svg command string from absolute coordinates."""
        self._prev = prev
        self.xs = [su.format_number(x) for x, _ in pts]
        self.ys = [su.format_number(y) for _, y in pts]
        if len(pts) > 1:
            msg = "SvgCommand only supports linear spline commands."
            raise NotImplementedError(msg)
        if prev is None:
            self.command = "M"
        elif self.ys[0] == prev.ys[0]:
            self.command = "H"
        elif self.xs[0] == prev.xs[0]:
            self.command = "V"
        else:
            self.command = "L"

    def _get_command_representation(self) -> str:
        """Return the svg command ("M", "L", "H", ...) as displayed in `d` attribute.

        The command string will be empty for identical adjacent commands and "L"
        following "M".

        "M x1,y1 x2,y2 x3,y3" behaves like "M x1,y1 L x2,y2 L x3,y3".
        """
        if self._prev is None:
            return self.command
        if self.command == self._prev.command:
            return ""
        if f"{self._prev.command}{self.command}" == "ML":
            return ""
        return self.command

    def __str__(self) -> str:
        """Return the svg command string.

        One command in an svg path `d` attribute.

        E.g., "L 3,4"
        """
        command = self._get_command_representation()
        if command == "H":
            pnts = f"{self.xs [0]}"
        elif command == "V":
            pnts = f"{self.ys[0]}"
        else:
            pnts = " ".join(f"{x},{y}" for x, y in zip(self.xs, self.ys))
        if command:
            return f"{command} {pnts}"
        return pnts


def new_data_string(pts: list[tuple[float, float]]) -> str:
    """Create an svg data string from a list of points.

    :param pts: list of (x, y) points in a linear spline.
    :return: svg data string. E.g., "M 3,4 L 5,6 L 7,8 Z"
    """
    commands = [SvgCommand(None, pts[0])]
    for pt in pts[1:]:
        commands.append(SvgCommand(commands[-1], pt))
    return " ".join(str(x) for x in commands) + " Z"


def _new_letter(name: str, *ptss: list[tuple[float, float]]) -> EtreeElement:
    """Create a `g` svg element for a small letter.

    :param name: id of the `g` element.
    :param ptss: list of lists of (x, y) points in a linear spline.
    :return: `g` svg element.
    """
    skewed = [[_skew_point(pt) for pt in pts] for pts in ptss]
    data_string = " ".join([new_data_string(pts) for pts in skewed])
    group = su.new_element("g", id=name)
    outline = su.new_sub_element(group, "path", d=data_string)
    _ = su.update_element(outline, stroke=_STROKE_COLOR, stroke_width=_STROKE_WIDTH)
    _ = su.new_sub_element(group, "path", d=data_string, fill=_FILL_COLOR)
    return group


letter_m = _new_letter("letter_m", letter_m_pts)
letter_i = _new_letter("letter_i", letter_i_pts_stem, letter_i_pts_dot)
