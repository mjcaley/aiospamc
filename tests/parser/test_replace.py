#!/usr/bin/env python3

from unittest.mock import patch

from aiospamc.parser import Success, Failure, Replace


@patch('aiospamc.parser.Parser')
def test_instantiates(parser):
    r = Replace(parser, 'replacement')

    assert 'r' in locals()


@patch('aiospamc.parser.Parser')
def test_success(parser):
    parser.return_value = Success(value='data', remaining=b'')

    r = Replace(parser, 'replacement')

    result = r(b'data')

    assert isinstance(result, Success)
    assert result.value == 'replacement'


@patch('aiospamc.parser.Parser')
def test_failure(parser):
    parser.return_value = Failure(error='no match', remaining=b'data')

    r = Replace(parser, 'replacement')

    result = r(b'data')

    assert isinstance(result, Failure)
