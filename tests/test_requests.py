#!/usr/bin/env python3
#pylint: disable=no-self-use

import zlib

import pytest

from aiospamc.headers import Compress, ContentLength, XHeader
from aiospamc.requests import Request


def test_request_instantiates():
    request = Request('TEST')

    assert 'request' in locals()


@pytest.mark.parametrize('verb,body,headers', [
    ('TEST', None, []),
    ('TEST', None, [XHeader('X-Tests-Head', 'Tests value')]),
    ('TEST', 'Test body\n', [ContentLength(length=10)]),
    ('TEST', 'Test body\n', [ContentLength(length=10), Compress()]),
    ('TEST', b'Binary stuff\n', [ContentLength(length=13)]),
    ('TEST', b'Really \xbbinary stuff\n', [ContentLength(length=20)]),
])
def test_request_bytes(verb, body, headers):
    request = Request(verb=verb, body=body, headers=headers, encoding='latin-1')

    assert bytes(request).startswith(verb.encode('ascii'))
    assert bytes(b'SPAMC/1.5\r\n') in bytes(request)
    assert all(bytes(header) in bytes(request) for header in headers)
    if body:
        if isinstance(body, bytes):
            bodybytes = body
        else:
            bodybytes = body.encode()
        if any(isinstance(header, Compress) for header in headers):
            assert bytes(request).endswith(zlib.compress(bodybytes))
        else:
            assert bytes(request).endswith(bodybytes)
