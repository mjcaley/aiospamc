#!/usr/bin/env python3

import pytest

from aiospamc.parser import Success, Failure, Boolean


def test_instantiates():
    b = Boolean()

    assert 'b' in locals()


@pytest.mark.parametrize('test_input', [
    b'True', b'true', b'False', b'false'
])
def test_success(test_input):
    b = Boolean()

    result = b(test_input)

    assert isinstance(result, Success)


def test_failure():
    b = Boolean()

    result = b(b'Invalid')

    assert isinstance(result, Failure)
