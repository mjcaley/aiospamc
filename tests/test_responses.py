#!/usr/bin/env python3

import pytest

import zlib

from aiospamc.exceptions import ResponseException
from aiospamc.incremental_parser import ResponseParser
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


def test_bytes_status():
    r = Response(status_code=999, message='Test message')
    result = bytes(r).partition(b'\r\n')[0]

    assert b'999 Test message' in result


def test_bytes_headers(x_headers):
    r = Response(version='1.5', status_code=Status.EX_OK, message='EX_OK', headers=x_headers)
    result = bytes(r).partition(b'\r\n')[2]
    expected = bytes(r.headers)

    assert result.startswith(expected)
    assert result.endswith(b'\r\n\r\n')


def test_bytes_body():
    test_input = b'Test body\n'
    r = Response(version='1.5', status_code=Status.EX_OK, message='EX_OK', body=test_input)
    result = bytes(r).rpartition(b'\r\n')[2]

    assert result == test_input


def test_bytes_body_compressed():
    test_input = b'Test body\n'
    r = Response(version='1.5', status_code=Status.EX_OK, message='EX_OK', headers={'Compress': 'zlib'}, body=test_input)
    result = bytes(r).rpartition(b'\r\n')[2]

    assert result == zlib.compress(test_input)


def test_raise_for_status_ok():
    r = Response(version='1.5', status_code=Status.EX_OK, message='')

    assert r.raise_for_status() is None


@pytest.mark.parametrize('test_input', [
    Status.EX_USAGE,
    Status.EX_DATAERR,
    Status.EX_NOINPUT,
    Status.EX_NOUSER,
    Status.EX_NOHOST,
    Status.EX_UNAVAILABLE,
    Status.EX_SOFTWARE,
    Status.EX_OSERR,
    Status.EX_OSFILE,
    Status.EX_CANTCREAT,
    Status.EX_IOERR,
    Status.EX_TEMPFAIL,
    Status.EX_PROTOCOL,
    Status.EX_NOPERM,
    Status.EX_CONFIG,
    Status.EX_TIMEOUT,
])
def test_raise_for_status(test_input):
    r = Response(version='1.5', status_code=test_input, message='')

    with pytest.raises(test_input.exception):
        r.raise_for_status()


def test_raise_for_undefined_status():
    r = Response(version='1.5', status_code=999, message='')

    with pytest.raises(ResponseException):
        r.raise_for_status()


def test_response_from_parser_result(response_with_body):
    p = ResponseParser().parse(response_with_body)
    r = Response(**p)

    assert r is not None
