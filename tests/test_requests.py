#!/usr/bin/env python3
#pylint: disable=no-self-use

import pytest

from aiospamc.headers import XHeader
from aiospamc.requests import Request


class TestRequest:
    def test_instantiates(self):
        request = Request('TEST')
        assert 'request' in locals()

    def test_compose(self):
        request = Request('TEST')
        assert request.compose() == b'TEST SPAMC/1.5\r\n\r\n'

    def test_compose_with_header(self):
        request = Request('TEST', None, XHeader('X-Tests-Head', 'Tests value'))
        assert request.compose() == b'TEST SPAMC/1.5\r\nX-Tests-Head: Tests value\r\n\r\n'

    def test_compose_with_body(self):
        request = Request('TEST', 'Test body\n')
        assert request.compose() == b'TEST SPAMC/1.5\r\nContent-length: 10\r\n\r\nTest body\n'

    def test_bytes(self):
        request = Request('TEST')
        assert bytes(request) == b'TEST SPAMC/1.5\r\n\r\n'

    def test_repr(self):
        request = Request('TEST')
        assert repr(request) == 'Request(verb=\'TEST\', body=None, headers=())'
