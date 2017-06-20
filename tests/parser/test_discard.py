#!/usr/bin/env python3

from unittest.mock import patch

from aiospamc.parser import Success, Failure, Discard


@patch('aiospamc.parser.Parser')
def test_instantiates(parser):
    d = Discard(parser)

    assert 'd' in locals()


@patch('aiospamc.parser.Parser')
def test_success(parser):
    parser.return_value = Success(value='data', remaining=b'')

    d = Discard(parser)

    result = d(b'data')

    assert isinstance(result, Success)
    assert result.value is None
    assert result.remaining == b''


@patch('aiospamc.parser.Parser')
def test_failure(parser):
    parser.return_value = Failure(error='not found', remaining=b'data')

    d = Discard(parser)

    result = d(b'data')

    assert isinstance(result, Failure)
