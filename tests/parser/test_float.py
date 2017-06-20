#!/usr/bin/env python3

from pytest import approx

from aiospamc.parser import Success, Failure, Float


def test_instantiates():
    f = Float()

    assert 'f' in locals()


def test_success():
    f = Float()

    result = f(b'4.2')

    assert isinstance(result, Success)
    assert result.value == approx(4.2)


def test_failure():
    f = Float()

    result = f(b'Invalid')

    assert isinstance(result, Failure)
