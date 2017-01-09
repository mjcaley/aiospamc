#!/usr/bin/env python3
#pylint: disable=no-self-use

import pytest

from aiospamc.headers import XHeader
from aiospamc.requests import SPAMCRequest


class TestSPAMCRequest:
    def test_instantiates(self):
        request = SPAMCRequest('TEST')
        assert 'request' in locals()

    def test_compose(self):
        request = SPAMCRequest('TEST')
        assert request.compose() == b'TEST SPAMC/1.5\r\n\r\n'

    def test_compose_with_header(self):
        request = SPAMCRequest('TEST', None, XHeader('X-Tests-Head', 'Tests value'))
        assert request.compose() == b'TEST SPAMC/1.5\r\nX-Tests-Head: Tests value\r\n\r\n'

    def test_compose_with_body(self):
        request = SPAMCRequest('TEST', 'Test body\n')
        assert request.compose() == b'TEST SPAMC/1.5\r\nContent-length: 10\r\n\r\nTest body\n'

    def test_bytes(self):
        request = SPAMCRequest('TEST')
        assert bytes(request) == b'TEST SPAMC/1.5\r\n\r\n'

    def test_repr(self):
        request = SPAMCRequest('TEST')
        assert repr(request) == 'SPAMCRequest(verb=\'TEST\', body=None, headers=())'
