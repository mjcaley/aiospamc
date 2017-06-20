#!/usr/bin/env python3

import pytest

from aiospamc.parser import Success, Failure, DidRemoveHeader
from aiospamc.headers import DidRemove
from aiospamc.options import ActionOption


def test_instantiates():
    d = DidRemoveHeader()

    assert 'd' in locals()


@pytest.mark.parametrize('test_input,expected', [
    (b'DidRemove : local\r\n',          ActionOption(local=True, remote=False)),
    (b'DidRemove : remote\r\n',         ActionOption(local=False, remote=True)),
    (b'DidRemove : local, remote\r\n',  ActionOption(local=True, remote=True)),
    (b'DidRemove : remote, local\r\n',  ActionOption(local=True, remote=True))
])
def test_success(test_input, expected):
    d = DidRemoveHeader()

    result = d(test_input)

    assert isinstance(result, Success)
    assert isinstance(result.value, DidRemove)
    assert result.value.action == expected


def test_failure():
    d = DidRemoveHeader()

    result = d(b'Invalid')

    assert isinstance(result, Failure)
