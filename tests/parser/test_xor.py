#!/usr/bin/env python3

from unittest.mock import MagicMock, patch

from aiospamc.parser import Success, Failure, Xor


@patch('aiospamc.parser.Parser')
def test_instantiates(parser):
    left = parser()
    right = parser()
    x = Xor(left=left, right=right)

    assert 'x' in locals()
    assert hasattr(x, 'left')
    assert hasattr(x, 'right')
    assert x.left == left
    assert x.right == right


def test_left_returns_succeeds():
    left = MagicMock('aiospamc.parser.Parser')
    right = MagicMock('aiospamc.parser.Parser')
    left.return_value = Success(value='found', remaining=b'remaining')
    right.return_value = Failure(error='Right failed', remaining=b'')

    x = Xor(left=left, right=right)
    result = x(b'data')

    assert isinstance(result, Success)
    assert result == left.return_value
    assert left.call_args[0][0] == b'data'


def test_right_returns_succeeds():
    left = MagicMock('aiospamc.parser.Parser')
    right = MagicMock('aiospamc.parser.Parser')
    left.return_value = Failure(error='Left failed', remaining=b'')
    right.return_value = Success(value='found', remaining=b'remaining')

    x = Xor(left=left, right=right)
    result = x(b'data')

    assert isinstance(result, Success)
    assert result == right.return_value
    assert left.call_args[0][0] == b'data'
    assert right.call_args[0][0] == b'data'


def test_both_returns_failure():
    left = MagicMock('aiospamc.parser.Parser')
    right = MagicMock('aiospamc.parser.Parser')
    left.return_value = Success(value='found', remaining=b'remaining')
    right.return_value = Success(value='found', remaining=b'remaining')

    x = Xor(left=left, right=right)
    result = x(b'data')

    assert isinstance(result, Failure)
    assert left.call_args[0][0] == b'data'
    assert right.call_args[0][0] == b'data'


def test_neither_returns_failure():
    left = MagicMock('aiospamc.parser.Parser')
    right = MagicMock('aiospamc.parser.Parser')
    left.return_value = Failure(error='Left failed', remaining=b'data')
    right.return_value = Failure(error='Right failed', remaining=b'data')

    x = Xor(left=left, right=right)
    result = x(b'data')

    assert isinstance(result, Failure)
    assert left.call_args[0][0] == b'data'
    assert right.call_args[0][0] == b'data'
