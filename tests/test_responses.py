#!/usr/bin/env python3

import pytest

from aiospamc.exceptions import (BadResponse,
                                 ExUsage, ExDataErr, ExNoInput, ExNoUser,
                                 ExNoHost, ExUnavailable, ExSoftware, ExOSErr,
                                 ExOSFile, ExCantCreat, ExIOErr, ExTempFail,
                                 ExProtocol, ExNoPerm, ExConfig, ExTimeout)
from aiospamc.responses import Response, Status


class TestResponse:
    def test_instantiates(self):
        response = Response('1.5', Status.EX_OK, 'EX_OK')
        assert 'response' in locals()

    def test_repr(self):
        response = Response('1.5', Status.EX_OK, 'EX_OK')
        assert repr(response) == 'Response(protocol_version=\'1.5\', status_code=Status.EX_OK, message=\'EX_OK\', headers=(), body=None)'

    def test_str(self):
        response = Response('1.5', Status.EX_OK, 'EX_OK')
        assert str(response) == 'SPAMD/1.5 0 EX_OK\r\n\r\n'

    def test_parse_valid(self):
        response = Response.parse('SPAMD/1.5 0 EX_OK\r\n\r\n')
        assert 'response' in locals()

    @pytest.mark.parametrize('test_input', [
        'SPAMD/1.5 0 EX_OK\r\nContent-length: 10\r\n\r\nTest body\n',
        'SPAMD/1.5 0 EX_OK\r\nContent-length: 0\r\n' # Lacking a newline
    ])
    def test_parse_has_content_length(self, test_input):
        response = Response.parse(test_input)
        assert response._headers['Content-length']

    def test_parse_valid_with_body(self):
        response = Response.parse('SPAMD/1.5 0 EX_OK\r\nContent-length: 10\r\n\r\nTest body\n')
        assert hasattr(response, 'body')

    def test_parse_invalid(self):
        with pytest.raises(BadResponse):
            response = Response.parse('Invalid response')

    @pytest.mark.parametrize('test_input,expected', [
        ('SPAMD/1.5 66 EX_NOINPUT', ExNoInput),
        ('SPAMD/1.5 67 EX_NOUSER', ExNoUser),
        ('SPAMD/1.5 68 EX_NOHOST', ExNoHost),
        ('SPAMD/1.5 69 EX_UNAVAILABLE', ExUnavailable),
        ('SPAMD/1.5 70 EX_SOFTWARE', ExSoftware),
        ('SPAMD/1.5 71 EX_OSERR', ExOSErr),
        ('SPAMD/1.5 72 EX_OSFILE', ExOSFile),
        ('SPAMD/1.5 73 EX_CANTCREAT', ExCantCreat),
        ('SPAMD/1.5 74 EX_IOERR', ExIOErr),
        ('SPAMD/1.5 75 EX_TEMPFAIL', ExTempFail),
        ('SPAMD/1.5 76 EX_PROTOCOL', ExProtocol),
        ('SPAMD/1.5 77 EX_NOPERM', ExNoPerm),
        ('SPAMD/1.5 78 EX_CONFIG', ExConfig),
        ('SPAMD/1.5 79 EX_TIMEOUT', ExTimeout),
    ])
    def test_response_exceptions(self, test_input, expected):
        with pytest.raises(expected):
            response = Response.parse(test_input)
