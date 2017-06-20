#!/usr/bin/env python3

from unittest.mock import MagicMock

from aiospamc.parser import Success, Failure, CustomHeader
from aiospamc.headers import XHeader


def test_instantiates():
    c = CustomHeader()

    assert 'c' in locals()


def test_success():
    c = CustomHeader()

    result = c(b'Custom : Header value\r\n')

    assert isinstance(result, Success)
    assert isinstance(result.value, XHeader)
    assert result.value.name == 'Custom'
    assert result.value.value == 'Header value'


def test_failure():
    c = CustomHeader()

    result = c(b'Invalid')

    assert isinstance(result, Failure)
