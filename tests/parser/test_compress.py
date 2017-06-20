#!/usr/bin/env python3

from aiospamc.parser import Success, Failure, CompressHeader
import aiospamc.headers


def test_instantiates():
    c = CompressHeader()

    assert 'c' in locals()


def test_success():
    c = CompressHeader()

    result = c(b'Compress : zlib\r\n')

    assert isinstance(result, Success)
    assert isinstance(result.value, aiospamc.headers.Compress)


def test_failure():
    c = CompressHeader()

    result = c(b'Invalid')

    assert isinstance(result, Failure)
