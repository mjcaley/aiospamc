#!/usr/bin/env python3
#pylint: disable=no-self-use

import pytest

from aiospamc.headers import XHeader
from aiospamc.requests import (SPAMCRequest, Check, Headers, Ping, Process,
                               Report, ReportIfSpam, Symbols, Tell)


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

class TestCheck:
    def test_instantiates(self):
        check = Check('Test body\n')
        assert 'check' in locals()

class TestHeaders:
    def test_instantiates(self):
        headers = Headers('Test body\n')
        assert 'headers' in locals()

class TestPing:
    def test_instantiates(self):
        ping = Ping()
        assert 'ping' in locals()

class TestProcess:
    def test_instantiates(self):
        process = Process('Test body\n')
        assert 'process' in locals()

class TestReport:
    def test_instantiates(self):
        report = Report('Test body\n')
        assert 'report' in locals()

class TestReportIfSpam:
    def test_instantiates(self):
        report_if_spam = ReportIfSpam('Test body\n')
        assert 'report_if_spam' in locals()

class TestSymbols:
    def test_instantiates(self):
        symbols = Symbols('Test body\n')
        assert 'symbols' in locals()

class TestTell:
    def test_instantiates(self):
        tell = Tell('Test body\n')
        assert 'tell' in locals()
