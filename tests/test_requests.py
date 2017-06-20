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
    ('TEST', 'Test body\n', [ContentLength(length=10), Compress()])
])
def test_request_bytes(verb, body, headers):
    request = Request(verb=verb, body=body, headers=headers)

    assert bytes(request).startswith(verb.encode())
    assert bytes(b'SPAMC/1.5\r\n') in bytes(request)
    assert all(bytes(header) in bytes(request) for header in headers)
    if body:
        if any(isinstance(header, Compress) for header in headers):
            assert bytes(request).endswith(zlib.compress(body.encode()))
        else:
            assert bytes(request).endswith(body.encode())
