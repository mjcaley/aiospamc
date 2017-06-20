#!/usr/bin/env python3

from aiospamc.parser import Success, Body


def test_instantiates():
    b = Body()

    assert 'b' in locals()


def test_success():
    b = Body()

    result = b(b'123abc')

    assert isinstance(result, Success)
    assert result.value == b'123abc'
