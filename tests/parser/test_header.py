#!/usr/bin/env python3

from aiospamc.parser import Success, Failure, Str, Header


def test_instantiates():
    h = Header(Str(b'name'), Str(b'value'))

    assert 'h' in locals()


def test_success():
    h = Header(Str(b'name'), Str(b'value'))

    result = h(b'name : value\r\n')

    assert isinstance(result, Success)


def test_failure():
    h = Header(Str(b'name'), Str(b'value'))

    result = h(b'Invalid')

    assert isinstance(result, Failure)
