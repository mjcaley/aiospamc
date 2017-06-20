#!/usr/bin/env python3

import pytest

from aiospamc.parser import Success, Failure, Integer


def test_instantiates():
    i = Integer()

    assert 'i' in locals()


@pytest.mark.parametrize('test_input,expected', [
    (b'0', 0), (b'1', 1), (b'2', 2), (b'3', 3), (b'4', 4),
    (b'5', 5), (b'6', 6), (b'7', 7), (b'8', 8), (b'9', 9),
    (b'10', 10)
])
def test_success(test_input, expected):
    i = Integer()

    result = i(test_input)

    assert isinstance(result, Success)
    assert isinstance(result.value, int)
    assert result.value == expected


def test_failure():
    i = Integer()

    result = i(b'Invalid')

    assert isinstance(result, Failure)
