#!/usr/bin/env python3

from unittest.mock import patch

from aiospamc.parser import Success, Failure, Stream, OneOrMore


@patch('aiospamc.parser.Parser')
def test_instantiates(parser):
    o = OneOrMore(parser=parser)

    assert 'o' in locals()
    assert hasattr(o, 'parser')
    assert o.parser is parser


@patch('aiospamc.parser.Parser')
def test_zero_matches(parser):
    stream = b'data'
    parser.return_value = Failure(error='error', remaining=Stream(stream, 0))

    o = OneOrMore(parser=parser)
    result = o(b'data')

    assert isinstance(result, Failure)
    assert parser.call_args[0][0] == stream


@patch('aiospamc.parser.Parser')
def test_one_match(parser):
    stream = b'data'
    parser.side_effect = [Success(value='data', remaining=Stream(stream, 4)),
                          Failure(error='error', remaining=Stream(stream, 4))]

    o = OneOrMore(parser)
    result = o(b'data')

    assert isinstance(result, Success)
    assert parser.call_args_list == [
        ((stream, 0),),
        ((stream, 4),)
    ]
    assert result.remaining.index == 4


@patch('aiospamc.parser.Parser')
def test_multiple_matches(parser):
    stream = b'data, data'
    parser.side_effect = [Success(value='data', remaining=Stream(stream, 6)),
                          Success(value='data', remaining=Stream(stream, 10)),
                          Failure(error='error', remaining=Stream(stream, 10))]

    o = OneOrMore(parser)
    result = o(stream)

    assert isinstance(result, Success)
    assert parser.call_args_list == [
        ((stream, 0),),
        ((stream, 6),),
        ((stream, 10),)
    ]
    assert result.remaining.index == 10
