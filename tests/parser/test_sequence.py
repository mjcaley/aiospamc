#!/usr/bin/env python3

from unittest.mock import MagicMock, patch

from aiospamc.parser import Success, Failure, Stream, Sequence


@patch('aiospamc.parser.Parser')
def test_instantiates(parser):
    left = parser()
    right = parser()
    s = Sequence(left=left, right=right)

    assert 's' in locals()
    assert hasattr(s, 'left')
    assert hasattr(s, 'right')
    assert s.left == left
    assert s.right == right


def test_left_returns_failure():
    stream = b'data'
    left = MagicMock('aiospamc.parser.Parser')
    right = MagicMock('aiospamc.parser.Parser')
    left.return_value = Failure(error='Left failed', remaining=Stream(stream, 0))
    right.return_value = Success(value='found', remaining=Stream(stream, 4))

    s = Sequence(left=left, right=right)
    result = s(stream)

    assert isinstance(result, Failure)


def test_right_returns_failure():
    stream = b'data'
    left = MagicMock('aiospamc.parser.Parser')
    right = MagicMock('aiospamc.parser.Parser')
    left.return_value = Success(value='found', remaining=Stream(stream, 4))
    right.return_value = Failure(error='Right failed', remaining=Stream(stream, 0))

    s = Sequence(left=left, right=right)
    result = s(stream)

    assert isinstance(result, Failure)


def test_returns_success():
    stream = b'data, data'
    left = MagicMock('aiospamc.parser.Parser')
    right = MagicMock('aiospamc.parser.Parser')
    left.return_value = Success(value='left', remaining=Stream(stream, 4))
    right.return_value = Success(value='right', remaining=Stream(stream, 10))

    s = Sequence(left=left, right=right)
    result = s(stream)

    assert isinstance(result, Success)
    assert result.value == ['left', 'right']
    assert result.remaining.index == 10
