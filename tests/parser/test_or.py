#!/usr/bin/env python3

from unittest.mock import MagicMock, patch

from aiospamc.parser import Success, Failure, Or


class TestOr:
    @patch('aiospamc.parser.Parser')
    def test_instantiates(self, parser):
        left = parser()
        right = parser()
        o = Or(left=left, right=right)

        assert 'o' in locals()
        assert hasattr(o, 'left')
        assert hasattr(o, 'right')
        assert o.left == left
        assert o.right == right

    def test_left_returns_succeeds(self):
        left = MagicMock('aiospamc.parser.Parser')
        right = MagicMock('aiospamc.parser.Parser')
        left.return_value = Success(value='found', remaining=b'remaining')
        right.return_value = Failure(error='Right failed', remaining=b'')

        o = Or(left=left, right=right)
        result = o(b'data')

        assert isinstance(result, Success)
        assert result == left.return_value
        assert left.call_args[0][0] == b'data'
        assert not right.called

    def test_right_returns_succeeds(self):
        left = MagicMock('aiospamc.parser.Parser')
        right = MagicMock('aiospamc.parser.Parser')
        left.return_value = Failure(error='Right failed', remaining=b'')
        right.return_value = Success(value='found', remaining=b'remaining')

        o = Or(left=left, right=right)
        result = o(b'data')

        assert isinstance(result, Success)
        assert result == right.return_value
        assert left.call_args[0][0] == b'data'
        assert right.call_args[0][0] == b'data'

    def test_both_returns_succeeds(self):
        left = MagicMock('aiospamc.parser.Parser')
        right = MagicMock('aiospamc.parser.Parser')
        left.return_value = Success(value='found', remaining=b'remaining')
        right.return_value = Success(value='found', remaining=b'remaining')

        o = Or(left=left, right=right)
        result = o(b'data')

        assert isinstance(result, Success)
        assert result == left.return_value
        assert left.call_args[0][0] == b'data'
        assert not right.called

    def test_neither_returns_failure(self):
        left = MagicMock('aiospamc.parser.Parser')
        right = MagicMock('aiospamc.parser.Parser')
        left.return_value = Failure(error='Left failed', remaining=b'data')
        right.return_value = Failure(error='Right failed', remaining=b'data')

        o = Or(left=left, right=right)
        result = o(b'data')

        assert isinstance(result, Failure)
        assert left.call_args[0][0] == b'data'
        assert right.call_args[0][0] == b'data'
