#!/usr/bin/env python3

import pytest

from aiospamc.parser import Success, Failure, MessageClassHeader
from aiospamc.headers import MessageClass
from aiospamc.options import MessageClassOption


def test_instantiates():
    m = MessageClassHeader()

    assert 'm' in locals()


@pytest.mark.parametrize('test_input,value', [
    (b'Message-class : spam\r\n', MessageClassOption.spam),
    (b'Message-class : ham\r\n', MessageClassOption.ham)
])
def test_success(test_input, value):
    m = MessageClassHeader()

    result = m(test_input)

    assert isinstance(result, Success)
    assert isinstance(result.value, MessageClass)
    assert result.value.value == value


def test_failure():
    m = MessageClassHeader()

    result = m(b'Invalid')

    assert isinstance(result, Failure)
