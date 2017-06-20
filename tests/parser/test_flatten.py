#!/usr/bin/env python3

from aiospamc.parser import flatten


def test_single_string():
    result = flatten(['data'])

    assert result == ['data']


def test_multiple_strings():
    result = flatten([['one', 'two'], 'three'])

    assert result == ['one', 'two', 'three']
