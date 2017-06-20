#!/usr/bin/env python3

from aiospamc.parser import Success, Failure, Newline


def test_instantiates():
    n = Newline()

    assert 'n' in locals()


def test_success():
    n = Newline()

    result = n(b'\r\n')

    assert isinstance(result, Success)


def test_failure():
    n = Newline()

    result = n(b'a')

    assert isinstance(result, Failure)
