#!/usr/bin/env python3
#pylint: disable=no-self-use

import zlib

import pytest

from aiospamc.exceptions import BadRequest
from aiospamc.headers import Compress, ContentLength, XHeader
from aiospamc.requests import Request


def test_request_instantiates():
    request = Request('TEST')

    assert 'request' in locals()

@pytest.mark.parametrize('verb,body,headers', [
    ('TEST', None, []),
    ('TEST', None, [XHeader('X-Tests-Head', 'Tests value')]),
    ('TEST', 'Test body\n', [ContentLength(length=10)]),
    ('TEST', 'Test body\n', [ContentLength(length=10), Compress()])
])
def test_request_bytes(verb, body, headers):
    request = Request(verb, body, *headers)

    assert bytes(request).startswith(verb.encode())
    assert bytes(b'SPAMC/1.5\r\n') in bytes(request)
    assert all(repr(header) in repr(request) for header in headers)
    if body:
        if any(isinstance(header, Compress) for header in headers):
            assert bytes(request).endswith(zlib.compress(body.encode()))
        else:
            assert bytes(request).endswith(body.encode())

@pytest.mark.parametrize('verb,body,headers', [
    ('TEST', None, []),
    ('TEST', None, [XHeader('X-Tests-Head', 'Tests value')]),
    ('TEST', 'Test body\n', [ContentLength(length=10)])
])
def test_request_repr(verb, body, headers):
    request = Request(verb, body, *headers)

    assert repr(request).startswith('Request(')
    assert 'verb={},'.format(repr(verb)) in repr(request)
    assert "version='1.5'," in repr(request)
    assert 'body={}'.format(repr(body)) in repr(request)
    assert 'headers=' in repr(request)
    assert all(repr(header) in repr(request) for header in headers)
    assert repr(request).endswith(')')

@pytest.mark.parametrize('test_input', [
    (b'TEST SPAMC/1.5\r\n\r\n'),
    (b'TEST SPAMC/1.5\r\n'),
    (b'TEST SPAMC/1.5\r\nContent-length: 10\r\n\r\nTest body\n')
])
def test_request_parse_valid(test_input):
    request = Request.parse(test_input)

    assert 'request' in locals()

def test_request_parse_invalid():
    with pytest.raises(BadRequest):
        request = Request.parse(b'Invalid')
