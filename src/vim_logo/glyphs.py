"""Simple, basic tools for building glyphs from linear paths.

:author: Shay Hill
:created: 2023-12-30
"""

from __future__ import annotations

import svg_ultralight as su


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
