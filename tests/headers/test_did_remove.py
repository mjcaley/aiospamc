#!/usr/bin/env python3

import pytest

from aiospamc.headers import DidRemove
from aiospamc.options import ActionOption


def test_repr():
    did_remove = DidRemove(ActionOption(local=True, remote=True))

    assert repr(did_remove) == 'DidRemove(action=ActionOption(local=True, remote=True))'


@pytest.mark.parametrize('test_input,expected', [
    (ActionOption(local=True, remote=False), b'DidRemove: local\r\n'),
    (ActionOption(local=False, remote=True), b'DidRemove: remote\r\n'),
    (ActionOption(local=True, remote=True), b'DidRemove: local, remote\r\n'),
    (ActionOption(local=False, remote=False), b''),
])
def test_bytes(test_input, expected):
    did_remove = DidRemove(test_input)

    assert bytes(did_remove) == expected
