#!/usr/bin/env python3

import pytest

from aiospamc.headers import Remove
from aiospamc.options import ActionOption


def test_repr():
    did_remove = Remove(ActionOption(local=True, remote=True))

    assert repr(did_remove) == 'Remove(action=ActionOption(local=True, remote=True))'


@pytest.mark.parametrize('test_input,expected', [
    (ActionOption(local=True, remote=False), b'Remove: local\r\n'),
    (ActionOption(local=False, remote=True), b'Remove: remote\r\n'),
    (ActionOption(local=True, remote=True), b'Remove: local, remote\r\n'),
    (ActionOption(local=False, remote=False), b''),
])
def test_bytes(test_input, expected):
    did_remove = Remove(test_input)

    assert bytes(did_remove) == expected
