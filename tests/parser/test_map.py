#!/usr/bin/env python3

from unittest.mock import patch, MagicMock

from aiospamc.parser import Success, Failure, Map


@patch('aiospamc.parser.Parser')
def test_instantiates(parser):
    func = MagicMock()

    m = Map(parser=parser, func=func)

    assert 'm' in locals()


@patch('aiospamc.parser.Parser')
def test_success(parser):
    func = MagicMock(return_value='modified data')
    parser.return_value = Success(value='original data', remaining=b'')

    m = Map(parser=parser, func=func)

    result = m(b'data')

    assert isinstance(result, Success)
    assert func.call_args[0][0] == 'original data'
    assert result.value == 'modified data'


@patch('aiospamc.parser.Parser')
def test_failure(parser):
    func = MagicMock()
    parser.return_value = Failure(error='error', remaining=b'data')

    m = Map(parser=parser, func=func)

    result = m(b'data')

    assert isinstance(result, Failure)
