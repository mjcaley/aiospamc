#!/usr/bin/env python3

import pytest

from aiospamc.parser import Success, Failure, DidSetHeader
from aiospamc.headers import DidSet
from aiospamc.options import ActionOption


def test_instantiates():
    d = DidSetHeader()

    assert 'd' in locals()


@pytest.mark.parametrize('test_input,expected', [
    (b'DidSet : local\r\n',          ActionOption(local=True, remote=False)),
    (b'DidSet : remote\r\n',         ActionOption(local=False, remote=True)),
    (b'DidSet : local, remote\r\n',  ActionOption(local=True, remote=True)),
    (b'DidSet : remote, local\r\n',  ActionOption(local=True, remote=True))
])
def test_success(test_input, expected):
    d = DidSetHeader()

    result = d(test_input)

    assert isinstance(result, Success)
    assert isinstance(result.value, DidSet)
    assert result.value.action == expected


def test_failure():
    d = DidSetHeader()

    result = d(b'Invalid')

    assert isinstance(result, Failure)
