#!/usr/bin/env python3

import pytest

from aiospamc.exceptions import BadResponse
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

    def test_parse_with_headers(self):
        response = Response.parse('SPAMD/1.5 0 EX_OK\r\nContent-length: 10\r\n\r\nTest body\n')
        assert response._headers['Content-length']

    def test_parse_header_with_weird_newline(self):
        response = Response.parse('SPAMD/1.5 0 EX_OK\r\nContent-length: 0\r\n')
        assert response._headers['Content-length']

    def test_parse_valid_with_body(self):
        response = Response.parse('SPAMD/1.5 0 EX_OK\r\nContent-length: 10\r\n\r\nTest body\n')
        assert hasattr(response, 'body')

    def test_parse_invalid(self):
        with pytest.raises(BadResponse):
            response = Response.parse('Invalid response')
