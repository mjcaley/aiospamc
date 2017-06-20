#!/usr/bin/env python3

from unittest.mock import patch

from aiospamc.parser import Success, Failure, Stream, Optional


@patch('aiospamc.parser.Parser')
def test_instantiates(parser):
    o = Optional(parser)

    assert 'o' in locals()
    assert o.parser is parser


@patch('aiospamc.parser.Parser')
def test_success(parser):
    parser.return_value = Success(value='data', remaining=b'')

    o = Optional(parser)

    result = o(b'data')

    assert isinstance(result, Success)
    assert result.value == 'data'
    assert result.remaining == b''


@patch('aiospamc.parser.Parser')
def test_failure(parser):
    stream = b'data'
    parser.return_value = Failure(error='error', remaining=Stream(stream, 4))

    o = Optional(parser)

    result = o(stream)

    assert isinstance(result, Success)
    assert result.value is None
    assert result.remaining.index == 0
