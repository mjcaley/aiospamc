#!/usr/bin/env python3

import pytest

from aiospamc.parser import Success, Failure, RequestMethod


def test_instantiates():
    r = RequestMethod()

    assert 'r' in locals()


@pytest.mark.parametrize('test_input,expected',
    [(b'CHECK', 'CHECK'),
     (b'HEADERS', 'HEADERS'),
     (b'PING', 'PING'),
     (b'PROCESS', 'PROCESS'),
     (b'REPORT', 'REPORT'),
     (b'REPORT_IFSPAM', 'REPORT_IFSPAM'),
     (b'SKIP', 'SKIP'),
     (b'SYMBOLS', 'SYMBOLS'),
     (b'TELL', 'TELL')])
def test_success(test_input, expected):
    r = RequestMethod()

    result = r(test_input)

    assert isinstance(result, Success)
    assert result.value == expected
    assert result.remaining.index == len(test_input)


def test_failure():
    r = RequestMethod()

    result = r(b'INVALID')

    assert isinstance(result, Failure)
