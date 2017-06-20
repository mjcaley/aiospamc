#!/usr/bin/env python3

import pytest
from pytest import approx

from aiospamc.parser import Success, Failure, SpamHeader
from aiospamc.headers import Spam


def test_instantiates():
    s = SpamHeader()

    assert 's' in locals()


@pytest.mark.parametrize('test_input,value,score,threshold', [
    (b'Spam : True ; 4.0 / 2.0\r\n', True, 4.0, 2.0),
    (b'Spam : False ; 4 / 2\r\n', False, 4, 2)
])
def test_success(test_input, value, score, threshold):
    s = SpamHeader()

    result = s(test_input)

    assert isinstance(result, Success)
    assert isinstance(result.value, Spam)
    assert result.value.value == value
    assert result.value.score == approx(score)
    assert result.value.threshold == approx(threshold)


def test_failure():
    s = SpamHeader()

    result = s(b'Invalid')

    assert isinstance(result, Failure)
