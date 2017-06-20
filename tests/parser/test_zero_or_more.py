#!/usr/bin/env python3

from unittest.mock import MagicMock

from aiospamc.parser import Success, Failure, Stream, ZeroOrMore


def test_instantiates():
    parser = MagicMock('aiospamc.parser.Parser')
    z = ZeroOrMore(parser)

    assert 'z' in locals()


def test_zero_matches():
    stream = b'data'
    parser = MagicMock('aiospamc.parser.Parser')
    parser.return_value = Failure(error='error', remaining=Stream(stream, 0))
    z = ZeroOrMore(parser)

    result = z(stream)

    assert isinstance(result, Success)
    assert len(result.value) == 0
    assert result.remaining.index == 0


def test_one_match():
    stream = b'data, data'
    parser = MagicMock('aiospamc.parser.Parser')
    parser.side_effect = [Success(value='data', remaining=Stream(stream, 4)),
                          Failure(error='error', remaining=Stream(stream, 4))]
    z = ZeroOrMore(parser)

    result = z(stream)

    assert isinstance(result, Success)
    assert len(result.value) == 1
    assert result.remaining.index == 4


def test_multiple_matches():
    stream = b'data, data, data'
    parser = MagicMock('aiospamc.parser.Parser')
    parser.side_effect = [Success(value='data', remaining=Stream(stream, 6)),
                          Success(value='data', remaining=Stream(stream, 12)),
                          Failure(error='error', remaining=Stream(stream, 12))]
    z = ZeroOrMore(parser)

    result = z(stream)

    assert isinstance(result, Success)
    assert len(result.value) == 2
    assert result.remaining.index == 12
