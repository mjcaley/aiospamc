#!/usr/bin/env python3

import pytest

from aiospamc.parser import Success, Failure, Response
import aiospamc.responses


def test_instantiates():
    r = Response()

    assert 'r' in locals()


@pytest.mark.parametrize('test_input', [
    b'SPAMD/1.5 0 EX_OK\r\n\r\n',
    b'SPAMD/1.5 64 EX_USAGE\r\n\r\n',
    b'SPAMD/1.5 65 EX_DATAERR\r\n\r\n',
    b'SPAMD/1.5 66 EX_NOINPUT\r\n\r\n',
    b'SPAMD/1.5 67 EX_NOUSER\r\n\r\n',
    b'SPAMD/1.5 68 EX_NOHOST\r\n\r\n',
    b'SPAMD/1.5 69 EX_UNAVAILABLE\r\n\r\n',
    b'SPAMD/1.5 70 EX_SOFTWARE\r\n\r\n',
    b'SPAMD/1.5 71 EX_OSERR\r\n\r\n',
    b'SPAMD/1.5 72 EX_OSFILE\r\n\r\n',
    b'SPAMD/1.5 73 EX_CANTCREAT\r\n\r\n',
    b'SPAMD/1.5 74 EX_IOERR\r\n\r\n',
    b'SPAMD/1.5 75 EX_TEMPFAIL\r\n\r\n',
    b'SPAMD/1.5 76 EX_PROTOCOL\r\n\r\n',
    b'SPAMD/1.5 77 EX_NOPERM\r\n\r\n',
    b'SPAMD/1.5 78 EX_CONFIG\r\n\r\n',
    b'SPAMD/1.5 79 EX_TIMEOUT\r\n\r\n',
])
def test_success(test_input):
    r = Response()

    result = r(test_input)

    assert isinstance(result, Success)
    assert isinstance(result.value, aiospamc.responses.Response)


@pytest.mark.parametrize('test_input', [
    b'SPAMD/1.5 0 EX_OK\r\nSpam: True ; 1000.0 / 2000.0\r\n\r\n',
    b'SPAMD/1.5 64 EX_USAGE\r\nSpam: True ; 1000.0 / 2000.0\r\n\r\n',
    b'SPAMD/1.5 65 EX_DATAERR\r\nSpam: True ; 1000.0 / 2000.0\r\n\r\n',
    b'SPAMD/1.5 66 EX_NOINPUT\r\nSpam: True ; 1000.0 / 2000.0\r\n\r\n',
    b'SPAMD/1.5 67 EX_NOUSER\r\nSpam: True ; 1000.0 / 2000.0\r\n\r\n',
    b'SPAMD/1.5 68 EX_NOHOST\r\nSpam: True ; 1000.0 / 2000.0\r\n\r\n',
    b'SPAMD/1.5 69 EX_UNAVAILABLE\r\nSpam: True ; 1000.0 / 2000.0\r\n\r\n',
    b'SPAMD/1.5 70 EX_SOFTWARE\r\nSpam: True ; 1000.0 / 2000.0\r\n\r\n',
    b'SPAMD/1.5 71 EX_OSERR\r\nSpam: True ; 1000.0 / 2000.0\r\n\r\n',
    b'SPAMD/1.5 72 EX_OSFILE\r\nSpam: True ; 1000.0 / 2000.0\r\n\r\n',
    b'SPAMD/1.5 73 EX_CANTCREAT\r\nSpam: True ; 1000.0 / 2000.0\r\n\r\n',
    b'SPAMD/1.5 74 EX_IOERR\r\nSpam: True ; 1000.0 / 2000.0\r\n\r\n',
    b'SPAMD/1.5 75 EX_TEMPFAIL\r\nSpam: True ; 1000.0 / 2000.0\r\n\r\n',
    b'SPAMD/1.5 76 EX_PROTOCOL\r\nSpam: True ; 1000.0 / 2000.0\r\n\r\n',
    b'SPAMD/1.5 77 EX_NOPERM\r\nSpam: True ; 1000.0 / 2000.0\r\n\r\n',
    b'SPAMD/1.5 78 EX_CONFIG\r\nSpam: True ; 1000.0 / 2000.0\r\n\r\n',
    b'SPAMD/1.5 79 EX_TIMEOUT\r\nSpam: True ; 1000.0 / 2000.0\r\n\r\n',
])
def test_success_with_header(test_input):
    r = Response()

    result = r(test_input)

    assert isinstance(result, Success)
    assert isinstance(result.value, aiospamc.responses.Response)


@pytest.mark.parametrize('test_input', [
    b'SPAMD/1.5 0 EX_OK\r\nSpam: True ; 1000.0 / 2000.0\r\nCompress: zlib\r\n\r\n',
    b'SPAMD/1.5 64 EX_USAGE\r\nSpam: True ; 1000.0 / 2000.0\r\nCompress: zlib\r\n\r\n',
    b'SPAMD/1.5 65 EX_DATAERR\r\nSpam: True ; 1000.0 / 2000.0\r\nCompress: zlib\r\n\r\n',
    b'SPAMD/1.5 66 EX_NOINPUT\r\nSpam: True ; 1000.0 / 2000.0\r\nCompress: zlib\r\n\r\n',
    b'SPAMD/1.5 67 EX_NOUSER\r\nSpam: True ; 1000.0 / 2000.0\r\nCompress: zlib\r\n\r\n',
    b'SPAMD/1.5 68 EX_NOHOST\r\nSpam: True ; 1000.0 / 2000.0\r\nCompress: zlib\r\n\r\n',
    b'SPAMD/1.5 69 EX_UNAVAILABLE\r\nSpam: True ; 1000.0 / 2000.0\r\nCompress: zlib\r\n\r\n',
    b'SPAMD/1.5 70 EX_SOFTWARE\r\nSpam: True ; 1000.0 / 2000.0\r\nCompress: zlib\r\n\r\n',
    b'SPAMD/1.5 71 EX_OSERR\r\nSpam: True ; 1000.0 / 2000.0\r\nCompress: zlib\r\n\r\n',
    b'SPAMD/1.5 72 EX_OSFILE\r\nSpam: True ; 1000.0 / 2000.0\r\nCompress: zlib\r\n\r\n',
    b'SPAMD/1.5 73 EX_CANTCREAT\r\nSpam: True ; 1000.0 / 2000.0\r\nCompress: zlib\r\n\r\n',
    b'SPAMD/1.5 74 EX_IOERR\r\nSpam: True ; 1000.0 / 2000.0\r\nCompress: zlib\r\n\r\n',
    b'SPAMD/1.5 75 EX_TEMPFAIL\r\nSpam: True ; 1000.0 / 2000.0\r\nCompress: zlib\r\n\r\n',
    b'SPAMD/1.5 76 EX_PROTOCOL\r\nSpam: True ; 1000.0 / 2000.0\r\nCompress: zlib\r\n\r\n',
    b'SPAMD/1.5 77 EX_NOPERM\r\nSpam: True ; 1000.0 / 2000.0\r\nCompress: zlib\r\n\r\n',
    b'SPAMD/1.5 78 EX_CONFIG\r\nSpam: True ; 1000.0 / 2000.0\r\nCompress: zlib\r\n\r\n',
    b'SPAMD/1.5 79 EX_TIMEOUT\r\nSpam: True ; 1000.0 / 2000.0\r\nCompress: zlib\r\n\r\n',
])
def test_success_with_headers(test_input):
    r = Response()

    result = r(test_input)

    assert isinstance(result, Success)
    assert isinstance(result.value, aiospamc.responses.Response)


@pytest.mark.parametrize('test_input', [
    b'SPAMD/1.5 0 EX_OK\r\nContent-length: 14\r\n\r\nThis is a body',
    b'SPAMD/1.5 64 EX_USAGE\r\nContent-length: 14\r\n\r\nThis is a body',
    b'SPAMD/1.5 65 EX_DATAERR\r\nContent-length: 14\r\n\r\nThis is a body',
    b'SPAMD/1.5 66 EX_NOINPUT\r\nContent-length: 14\r\n\r\nThis is a body',
    b'SPAMD/1.5 67 EX_NOUSER\r\nContent-length: 14\r\n\r\nThis is a body',
    b'SPAMD/1.5 68 EX_NOHOST\r\nContent-length: 14\r\n\r\nThis is a body',
    b'SPAMD/1.5 69 EX_UNAVAILABLE\r\nContent-length: 14\r\n\r\nThis is a body',
    b'SPAMD/1.5 70 EX_SOFTWARE\r\nContent-length: 14\r\n\r\nThis is a body',
    b'SPAMD/1.5 71 EX_OSERR\r\nContent-length: 14\r\n\r\nThis is a body',
    b'SPAMD/1.5 72 EX_OSFILE\r\nContent-length: 14\r\n\r\nThis is a body',
    b'SPAMD/1.5 73 EX_CANTCREAT\r\nContent-length: 14\r\n\r\nThis is a body',
    b'SPAMD/1.5 74 EX_IOERR\r\nContent-length: 14\r\n\r\nThis is a body',
    b'SPAMD/1.5 75 EX_TEMPFAIL\r\nContent-length: 14\r\n\r\nThis is a body',
    b'SPAMD/1.5 76 EX_PROTOCOL\r\nContent-length: 14\r\n\r\nThis is a body',
    b'SPAMD/1.5 77 EX_NOPERM\r\nContent-length: 14\r\n\r\nThis is a body',
    b'SPAMD/1.5 78 EX_CONFIG\r\nContent-length: 14\r\n\r\nThis is a body',
    b'SPAMD/1.5 79 EX_TIMEOUT\r\nContent-length: 14\r\n\r\nThis is a body',
])
def test_success_with_body(test_input):
    r = Response()

    result = r(test_input)

    assert isinstance(result, Success)
    assert isinstance(result.value, aiospamc.responses.Response)


def test_failure():
    r = Response()

    result = r(b'Invalid')

    assert isinstance(result, Failure)
