#!/usr/bin/env python3

import pytest
from fixtures import *

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

    def test_str(self, response_ok):
        response = Response('1.5', Status.EX_OK, 'EX_OK')
        assert str(response) == response_ok.decode()

    def test_parse_valid(self, response_ok):
        response = Response.parse(response_ok.decode())
        assert 'response' in locals()

    @pytest.mark.parametrize('test_input', [
        response_with_body(),
        response_empty_body()
    ])
    def test_parse_has_content_length(self, test_input):
        response = Response.parse(test_input.decode())
        assert response._headers['Content-length']

    def test_parse_valid_with_body(self, response_with_body):
        response = Response.parse(response_with_body.decode())
        assert hasattr(response, 'body')

    def test_parse_invalid(self, response_invalid):
        with pytest.raises(BadResponse):
            response = Response.parse(response_invalid.decode())

    @pytest.mark.parametrize('test_input,expected', [
        (ex_no_input(), ExNoInput),
        (ex_no_user(), ExNoUser),
        (ex_no_host(), ExNoHost),
        (ex_unavailable(), ExUnavailable),
        (ex_software(), ExSoftware),
        (ex_os_err(), ExOSErr),
        (ex_os_file(), ExOSFile),
        (ex_cant_create(), ExCantCreat),
        (ex_io_err(), ExIOErr),
        (ex_temp_fail(), ExTempFail),
        (ex_protocol(), ExProtocol),
        (ex_no_perm(), ExNoPerm),
        (ex_config(), ExConfig),
        (ex_timeout(), ExTimeout),
    ])
    def test_response_exceptions(self, test_input, expected):
        with pytest.raises(expected):
            response = Response.parse(test_input.decode())
