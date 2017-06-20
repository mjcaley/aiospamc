#!/usr/bin/env python3

import pytest

from aiospamc.parser import Success, Failure, Whitespace


def test_instantiates():
    w = Whitespace()

    assert 'w' in locals()


@pytest.mark.parametrize('test_input,expected',
    [(b' ', ' '),
     (b'\t', '\t'),
     (b'\x0b', '\x0b'),
     (b'\x0c', '\x0c')
     ])
def test_success(test_input, expected):
    w = Whitespace()

    result = w(test_input)

    assert isinstance(result, Success)
    assert result.remaining.index == len(test_input)


def test_failure():
    w = Whitespace()

    result = w(b'a')

    assert isinstance(result, Failure)
