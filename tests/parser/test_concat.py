#!/usr/bin/env python3

from aiospamc.parser import concat


def test_single_string():
    result = concat('data')

    assert result == 'data'


def test_multiple_strings():
    result = concat(['one', 'two', 'three'])

    assert result == 'onetwothree'
