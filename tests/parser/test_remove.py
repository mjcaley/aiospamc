#!/usr/bin/env python3

import pytest

from aiospamc.parser import Success, Failure, RemoveHeader
from aiospamc.headers import Remove
from aiospamc.options import ActionOption


def test_instantiates():
    d = RemoveHeader()

    assert 'd' in locals()


@pytest.mark.parametrize('test_input,expected', [
    (b'Remove : local\r\n',          ActionOption(local=True, remote=False)),
    (b'Remove : remote\r\n',         ActionOption(local=False, remote=True)),
    (b'Remove : local, remote\r\n',  ActionOption(local=True, remote=True)),
    (b'Remove : remote, local\r\n',  ActionOption(local=True, remote=True))
])
def test_success(test_input, expected):
    d = RemoveHeader()

    result = d(test_input)

    assert isinstance(result, Success)
    assert isinstance(result.value, Remove)
    assert result.value.action == expected


def test_failure():
    d = RemoveHeader()

    result = d(b'Invalid')

    assert isinstance(result, Failure)
