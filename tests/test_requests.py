#!/usr/bin/env python3
#pylint: disable=no-self-use

import zlib

import pytest

from aiospamc.headers import Compress, ContentLength, XHeader
from aiospamc.requests import Request


def test_init_verb():
    r = Request(verb='TEST')

    assert r.verb == 'TEST'


def test_init_version():
    r = Request(verb='TEST', version='4.2')

    assert r.version == '4.2'


def test_init_headers():
    r = Request(verb='TEST')

    assert hasattr(r, 'headers')


def test_bytes_starts_with_verb():
    r = Request(verb='TEST')
    result = bytes(r)

    assert result.startswith(b'TEST')


def test_bytes_protocol():
    r = Request(verb='TEST', version='4.2')
    result = bytes(r).split(b'\r\n', 1)[0]

    assert result.endswith(b' SPAMC/4.2')


def test_bytes_headers(x_headers):
    r = Request(verb='TEST', headers=x_headers)
    result = bytes(r).split(b'\r\n')[1:-2]      # strip end of headers, body and first line
    expected = [bytes(header).rstrip(b'\r\n') for header in x_headers]

    for header_bytes in result:
        assert header_bytes in expected


def test_bytes_body():
    test_input = b'Test body\n'
    r = Request(verb='TEST', body=test_input)
    result = bytes(r).split(b'\r\n', 3)[-1]

    assert result == test_input


def test_bytes_body_compressed():
    test_input = b'Test body\n'
    r = Request(verb='TEST', headers=[Compress()], body=test_input)
    result = bytes(r).split(b'\r\n', 3)[-1]

    assert result == zlib.compress(test_input)
