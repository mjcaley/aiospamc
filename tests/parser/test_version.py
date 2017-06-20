#!/usr/bin/env python3

from aiospamc.parser import Success, Failure, Version


def test_instantiates():
    v = Version()


def test_success():
    v = Version()

    result = v(b'123.123')

    assert isinstance(result, Success)
    assert result.value == '123.123'


def test_failure():
    v = Version()

    result = v(b'Invalid')

    assert isinstance(result, Failure)
