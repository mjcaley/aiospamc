#!/usr/bin/env python3
#pylint: disable=no-self-use

import pytest

from aiospamc.headers import XHeader
from aiospamc.requests import Request


class TestRequest:
    def test_instantiates(self):
        request = Request('TEST')
        assert 'request' in locals()

    @pytest.mark.parametrize('test_input,expected', [
        (Request('TEST'), b'TEST SPAMC/1.5\r\n\r\n'),
        (Request('TEST', None, XHeader('X-Tests-Head', 'Tests value')), b'TEST SPAMC/1.5\r\nX-Tests-Head: Tests value\r\n\r\n'),
        (Request('TEST', 'Test body\n'), b'TEST SPAMC/1.5\r\nContent-length: 10\r\n\r\nTest body\n'),
    ])
    def test_compose(self, test_input, expected):
        request = test_input
        assert request.compose() == expected

    def test_bytes(self):
        request = Request('TEST')
        assert bytes(request) == b'TEST SPAMC/1.5\r\n\r\n'

    def test_repr(self):
        request = Request('TEST')
        assert repr(request) == 'Request(verb=\'TEST\', body=None, headers=())'
