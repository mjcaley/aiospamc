#!/usr/bin/env python3

import pytest

from aiospamc.parser import Success, Failure, SetRemoveValue
from aiospamc.options import ActionOption


def test_instantiates():
    s = SetRemoveValue()

    assert 's' in locals()


@pytest.mark.parametrize('test_input,expected', [
    (b'local\r\n',          ActionOption(local=True, remote=False)),
    (b'remote\r\n',         ActionOption(local=False, remote=True)),
    (b'local, remote\r\n',  ActionOption(local=True, remote=True)),
    (b'remote, local\r\n',  ActionOption(local=True, remote=True))
])
def test_success(test_input, expected):
    s = SetRemoveValue()

    result = s(test_input)

    assert isinstance(result, Success)
    assert isinstance(result.value, ActionOption)
    assert result.value == expected


def test_failure():
    s = SetRemoveValue()

    result = s(b'Invalid')

    assert isinstance(result, Failure)
