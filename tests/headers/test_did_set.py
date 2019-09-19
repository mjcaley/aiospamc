#!/usr/bin/env python3

import pytest

from aiospamc.headers import DidSet
from aiospamc.options import ActionOption


def test_repr():
    did_set = DidSet(ActionOption(local=True, remote=True))

    assert repr(did_set) == 'DidSet(action=ActionOption(local=True, remote=True))'


@pytest.mark.parametrize('test_input,expected', [
    (ActionOption(local=True, remote=False), b'DidSet: local\r\n'),
    (ActionOption(local=False, remote=True), b'DidSet: remote\r\n'),
    (ActionOption(local=True, remote=True), b'DidSet: local, remote\r\n'),
    (ActionOption(local=False, remote=False), b''),
])
def test_bytes(test_input, expected):
    did_set = DidSet(test_input)

    assert bytes(did_set) == expected
