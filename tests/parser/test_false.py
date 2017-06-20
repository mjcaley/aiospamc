#!/usr/bin/env python3

import pytest

from aiospamc.parser import Success, Failure, FalseValue


def test_instantiates():
    f = FalseValue()

    assert 'f' in locals()


@pytest.mark.parametrize('test_input', [
    b'False', b'false'
])
def test_success(test_input):
    f = FalseValue()

    result = f(test_input)

    assert isinstance(result, Success)


def test_failure():
    f = FalseValue()

    result = f(b'Invalid')

    assert isinstance(result, Failure)
