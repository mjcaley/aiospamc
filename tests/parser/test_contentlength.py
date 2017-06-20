#!/usr/bin/env python3

from aiospamc.headers import ContentLength
from aiospamc.parser import Success, Failure, ContentLengthHeader


def test_instantiates():
    c = ContentLengthHeader()

    assert 'c' in locals()


def test_success():
    c = ContentLengthHeader()

    result = c(b'Content-length : 42\r\n')

    assert isinstance(result, Success)
    assert isinstance(result.value, ContentLength)


def test_failure():
    c = ContentLengthHeader()

    result = c(b'Invalid')

    assert isinstance(result, Failure)
