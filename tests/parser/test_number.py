#!/usr/bin/env python3

import pytest
from pytest import approx

from aiospamc.parser import Success, Failure, Number


def test_instantiates():
    n = Number()

    assert 'n' in locals()


@pytest.mark.parametrize('test_input,expected', [
    (b'1', 1),
    (b'4.2', 4.2)
])
def test_success(test_input, expected):
    n = Number()

    result = n(test_input)

    assert isinstance(result, Success)
    assert result.value == approx(expected)


def test_failure():
    n = Number()

    result = n(b'Invalid')

    assert isinstance(result, Failure)
