"""Test functions in glyph.py

:author: Shay Hill
:created: 2024-01-05
"""


from vim_logo.glyphs import _remove_identical_adjacent_values  # type: ignore

from vim_logo import glyphs
from typing import TypeVar

_T = TypeVar("_T")


def key_func(x: _T) -> _T:
    return x

class TestRemoveIdenticalAdjacentValues:
    def test_remove_identical_adjacent_values(self):
        values = [1, 2, 2, 3, 4, 4, 4, 5, 5]
        expected = [1, 2, 3, 4, 5]
        assert _remove_identical_adjacent_values(values) == expected

    def test_all_identical_values(self):
        values = [1, 1, 1, 1]
        expected = [1]
        assert _remove_identical_adjacent_values(values) == expected

    def test_one_value(self):
        values = [1]
        expected = [1]
        assert _remove_identical_adjacent_values(values) == expected

    def test_zero_values(self):
        values: tuple[int, ...] = tuple()
        expected: list[int] = []
        assert _remove_identical_adjacent_values(values) == expected

    def test_equal_endpoints(self):
        values = [1, 1, 2, 2, 3, 3, 1, 1]
        expected = [1, 2, 3]
        assert  _remove_identical_adjacent_values(values) == expected

    def text_string_values(self):
        values = ['apple', 'apple', 'banana', 'banana', 'carrot']
        expected = ['apple', 'banana', 'carrot']
        assert _remove_identical_adjacent_values(values) == expected

    def test_remove_identical_adjacent_values_with_key_function(self):
        values = ['apple', 'APPLE', 'banana', 'BANANA', 'carrot']
        expected = ['APPLE', 'BANANA', 'carrot']
        def key_func(x: str) -> str:
            return x.lower()
        assert _remove_identical_adjacent_values(values, key=key_func) == expected

    def test_remove_identical_adjacent_values_with_meaningless_key_function(self):
        values = ['Apple', 'apple', 'apple', 'apple']
        expected = ['Apple', 'apple']
        def key_func(x: str) -> str:
            return x
        assert _remove_identical_adjacent_values(values, key=key_func) == expected

