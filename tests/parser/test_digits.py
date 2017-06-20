#!/usr/bin/env python3

from aiospamc.parser import Success, Failure, Digits


def test_instantiates():
    d = Digits()

    assert 'd' in locals()


def test_success():
    d = Digits()

    result = d(b'123')

    assert isinstance(result, Success)
    assert result.value == '123'
    assert result.remaining.index == 3


def test_success_mixed():
    d = Digits()

    result = d(b'123a')

    assert isinstance(result, Success)
    assert result.value == '123'
    assert result.remaining.index == 3


def test_failure():
    d = Digits()

    result = d(b'a')

    assert isinstance(result, Failure)
