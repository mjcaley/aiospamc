#!/usr/bin/env python3

import pytest

from aiospamc.parser import Success, Failure, Request
import aiospamc.requests


def test_instantiates():
    r = Request()

    assert 'r' in locals()


@pytest.mark.parametrize('test_input', [
    b'CHECK SPAMC/1.5\r\n\r\n',
    b'SYMBOLS SPAMC/1.5\r\n\r\n',
    b'REPORT SPAMC/1.5\r\n\r\n',
    b'REPORT_IFSPAM SPAMC/1.5\r\n\r\n',
    b'SKIP SPAMC/1.5\r\n\r\n',
    b'PING SPAMC/1.5\r\n\r\n',
    b'PROCESS SPAMC/1.5\r\n\r\n',
    b'TELL SPAMC/1.5\r\n\r\n',
    b'HEADERS SPAMC/1.5\r\n\r\n',
])
def test_success(test_input):
    r = Request()

    result = r(test_input)

    assert isinstance(result, Success)
    assert isinstance(result.value, aiospamc.requests.Request)


@pytest.mark.parametrize('test_input', [
    b'CHECK SPAMC/1.5\r\nContent-length: 42\r\n\r\n',
    b'SYMBOLS SPAMC/1.5\r\nContent-length: 42\r\n\r\n',
    b'REPORT SPAMC/1.5\r\nContent-length: 42\r\n\r\n',
    b'REPORT_IFSPAM SPAMC/1.5\r\nContent-length: 42\r\n\r\n',
    b'SKIP SPAMC/1.5\r\nContent-length: 42\r\n\r\n',
    b'PING SPAMC/1.5\r\nContent-length: 42\r\n\r\n',
    b'PROCESS SPAMC/1.5\r\nContent-length: 42\r\n\r\n',
    b'TELL SPAMC/1.5\r\nContent-length: 42\r\n\r\n',
    b'HEADERS SPAMC/1.5\r\nContent-length: 42\r\n\r\n',
])
def test_success_with_header(test_input):
    r = Request()

    result = r(test_input)

    assert isinstance(result, Success)
    assert isinstance(result.value, aiospamc.requests.Request)


@pytest.mark.parametrize('test_input', [
    b'CHECK SPAMC/1.5\r\nContent-length: 42\r\nUser: username\r\n\r\n',
    b'SYMBOLS SPAMC/1.5\r\nContent-length: 42\r\nUser: username\r\n\r\n',
    b'REPORT SPAMC/1.5\r\nContent-length: 42\r\nUser: username\r\n\r\n',
    b'REPORT_IFSPAM SPAMC/1.5\r\nContent-length: 42\r\nUser: username\r\n\r\n',
    b'SKIP SPAMC/1.5\r\nContent-length: 42\r\nUser: username\r\n\r\n',
    b'PING SPAMC/1.5\r\nContent-length: 42\r\nUser: username\r\n\r\n',
    b'PROCESS SPAMC/1.5\r\nContent-length: 42\r\nUser: username\r\n\r\n',
    b'TELL SPAMC/1.5\r\nContent-length: 42\r\nUser: username\r\n\r\n',
    b'HEADERS SPAMC/1.5\r\nContent-length: 42\r\nUser: username\r\n\r\n',
])
def test_success_with_headers(test_input):
    r = Request()

    result = r(test_input)

    assert isinstance(result, Success)
    assert isinstance(result.value, aiospamc.requests.Request)


@pytest.mark.parametrize('test_input', [
    b'CHECK SPAMC/1.5\r\nContent-length: 12\r\nUser: username\r\n\r\nMessage body',
    b'SYMBOLS SPAMC/1.5\r\nContent-length: 12\r\n\r\nMessage body',
    b'REPORT SPAMC/1.5\r\nContent-length: 12\r\n\r\nMessage body',
    b'REPORT_IFSPAM SPAMC/1.5\r\nContent-length: 12\r\n\r\nMessage body',
    b'SKIP SPAMC/1.5\r\nContent-length: 12\r\n\r\nMessage body',
    b'PING SPAMC/1.5\r\nContent-length: 12\r\n\r\nMessage body',
    b'PROCESS SPAMC/1.5\r\nContent-length: 12\r\n\r\nMessage body',
    b'TELL SPAMC/1.5\r\nContent-length: 12\r\n\r\nMessage body',
    b'HEADERS SPAMC/1.5\r\nContent-length: 12\r\n\r\nMessage body',
])
def test_success_with_body(test_input):
    r = Request()

    result = r(test_input)

    assert isinstance(result, Success)
    assert isinstance(result.value, aiospamc.requests.Request)


def test_failure():
    r = Request()

    result = r(b'Invalid')

    assert isinstance(result, Failure)
