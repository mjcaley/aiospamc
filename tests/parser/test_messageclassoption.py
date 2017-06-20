#!/usr/bin/env python3

import pytest

from aiospamc.parser import Success, Failure, MessageClassOption
import aiospamc.options


def test_instantiates():
    m = MessageClassOption()


@pytest.mark.parametrize('test_input,expected', [
    (b'ham', aiospamc.options.MessageClassOption.ham),
    (b'spam', aiospamc.options.MessageClassOption.spam)
])
def test_success(test_input, expected):
    m = MessageClassOption()

    result = m(test_input)

    assert isinstance(result, Success)
    assert isinstance(result.value, aiospamc.options.MessageClassOption)
    assert result.value == expected


def test_failure():
    m = MessageClassOption()

    result = m(b'Invalid')

    assert isinstance(result, Failure)
