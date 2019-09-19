#!/usr/bin/env python3

import pytest

from aiospamc.headers import Set
from aiospamc.options import ActionOption


def test_repr():
    did_set = Set(ActionOption(local=True, remote=True))

    assert repr(did_set) == 'Set(action=ActionOption(local=True, remote=True))'


@pytest.mark.parametrize('test_input,expected', [
    (ActionOption(local=True, remote=False), b'Set: local\r\n'),
    (ActionOption(local=False, remote=True), b'Set: remote\r\n'),
    (ActionOption(local=True, remote=True), b'Set: local, remote\r\n'),
    (ActionOption(local=False, remote=False), b''),
])
def test_bytes(test_input, expected):
    did_set = Set(test_input)

    assert bytes(did_set) == expected
