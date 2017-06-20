#!/usr/bin/env python3

import pytest

from aiospamc.parser import Success, Failure, SetHeader
from aiospamc.headers import Set
from aiospamc.options import ActionOption


def test_instantiates():
    d = SetHeader()

    assert 'd' in locals()


@pytest.mark.parametrize('test_input,expected', [
    (b'Set : local\r\n',          ActionOption(local=True, remote=False)),
    (b'Set : remote\r\n',         ActionOption(local=False, remote=True)),
    (b'Set : local, remote\r\n',  ActionOption(local=True, remote=True)),
    (b'Set : remote, local\r\n',  ActionOption(local=True, remote=True))
])
def test_success(test_input, expected):
    d = SetHeader()

    result = d(test_input)

    assert isinstance(result, Success)
    assert isinstance(result.value, Set)
    assert result.value.action == expected


def test_failure():
    d = SetHeader()

    result = d(b'Invalid')

    assert isinstance(result, Failure)
