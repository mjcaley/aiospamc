#!/usr/bin/env python3

import pytest

from aiospamc.parser import Success, Failure, TrueValue


def test_instantiates():
    t = TrueValue()

    assert 't' in locals()


@pytest.mark.parametrize('test_input', [
    b'True', b'true'
])
def test_success(test_input):
    t = TrueValue()

    result = t(test_input)

    assert isinstance(result, Success)


def test_failure():
    t = TrueValue()

    result = t(b'Invalid')

    assert isinstance(result, Failure)
