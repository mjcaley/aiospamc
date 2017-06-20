#!/usr/bin/env python3

from unittest.mock import patch

import pytest

from aiospamc.parser import Success, Failure, Parser, Or, Sequence, Xor


class TestSuccess:
    def test_instantiates(self):
        value = 'value'
        remaining = b'remaining'
        s = Success(value=value, remaining=remaining)

        assert 's' in locals()
        assert hasattr(s, 'value')
        assert hasattr(s, 'remaining')
        assert s.value is value
        assert s.remaining is remaining

    def test_true(self):
        value = 'value'
        remaining= b'remaining'
        s = Success(value=value, remaining=remaining)

        if s:
            assert True
        else:
            assert False

    def test_repr(self):
        value = 'value'
        remaining= b'remaining'
        s = Success(value=value, remaining=remaining)

        assert repr(s) == 'Success(value={}, remaining={})'.format(repr(value),
                                                                   repr(remaining))

    def test_str(self):
        value = 'value'
        remaining = b'remaining'
        s = Success(value=value, remaining=remaining)

        assert str(s) == 'Found {}'.format(value)


class TestFailure:
    def test_instantiates(self):
        error = 'error'
        f = Failure(error=error, remaining=b'')

        assert 'f' in locals()
        assert hasattr(f, 'error')

    def test_false(self):
        error = 'error'
        f = Failure(error=error, remaining=b'')

        if not f:
            assert True
        else:
            assert False

    @patch('aiospamc.parser.Stream')
    def test_repr(self, stream):
        error = 'error'
        stream.index.return_value = 0
        f = Failure(error=error, remaining=stream)

        assert repr(f) == 'Failure(error={}, remaining={})'.format(repr(error),
                                                                   repr(stream))

    @patch('aiospamc.parser.Stream')
    def test_str(self, stream):
        error = 'error'
        stream.index.return_value = 0
        f = Failure(error=error, remaining=stream)

        assert str(f) == 'Failure: {}, index={}'.format(error, stream.index)


class TestParser:
    def test_call_not_implemented(self):
        p = Parser()

        with pytest.raises(NotImplementedError):
            p(b'data')

    def test_or(self):
        or_ = Parser().__or__('value')

        assert isinstance(or_, Or)

    def test_sequence(self):
        seq = Parser().__rshift__('value')

        assert isinstance(seq, Sequence)

    def test_xor(self):
        xor = Parser().__xor__('value')

        assert isinstance(xor, Xor)


