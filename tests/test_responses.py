#!/usr/bin/env python3

import zlib

from aiospamc.headers import Compress
from aiospamc.responses import Response, Status


def test_init_version():
    r = Response(version='4.2', status_code=Status.EX_OK, message='EX_OK')
    result = bytes(r).split(b' ')[0]

    assert result == b'SPAMD/4.2'


def test_init_status_code():
    r = Response(version='1.5', status_code=Status.EX_OK, message='EX_OK')
    result = bytes(r).split(b' ')[1]

    assert result == str(Status.EX_OK.value).encode()


def test_init_message():
    r = Response(version='1.5', status_code=Status.EX_OK, message='EX_OK')
    result = bytes(r).split(b'\r\n')[0]

    assert result.endswith(Status.EX_OK.name.encode())


def test_bytes_headers(x_headers):
    r = Response(version='1.5', status_code=Status.EX_OK, message='EX_OK')
    result = bytes(r).split(b'\r\n')[1:-2]      # strip end of headers, body and first line
    expected = [bytes(header).rstrip(b'\r\n') for header in x_headers]

    for header_bytes in result:
        assert header_bytes in expected


def test_bytes_body():
    test_input = b'Test body\n'
    r = Response(version='1.5', status_code=Status.EX_OK, message='EX_OK', body=test_input)
    result = bytes(r).split(b'\r\n', 3)[-1]

    assert result == test_input


def test_bytes_body_compressed():
    test_input = b'Test body\n'
    r = Response(version='1.5', status_code=Status.EX_OK, message='EX_OK', headers=[Compress()], body=test_input)
    result = bytes(r).split(b'\r\n', 3)[-1]

    assert result == zlib.compress(test_input)
