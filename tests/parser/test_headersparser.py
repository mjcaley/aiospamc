#!/usr/bin/env python3

import pytest

from aiospamc.parser import Success, Failure, Headers
from aiospamc.headers import (Compress, ContentLength, MessageClass, DidSet,
                              DidRemove, Set, Remove, Spam, User, XHeader)


def test_instantiates():
    h = Headers()

    assert 'h' in locals()


@pytest.mark.parametrize('test_input,expected', [
    [b'Compress: zlib\r\n', Compress],
    [b'Content-length: 42\r\n', ContentLength],
    [b'Message-class: ham\r\n', MessageClass],
    [b'DidSet: local, remote\r\n', DidSet],
    [b'DidRemove: local, remote\r\n', DidRemove],
    [b'Set: local, remote\r\n', Set],
    [b'Remove: local, remote\r\n', Remove],
    [b'Spam: True ; 1000.0 / 2000.0\r\n', Spam],
    [b'User: username\r\n', User],
    [b'XHeader: data\r\n', XHeader]
])
def test_success(test_input, expected):
    h = Headers()

    result = h(test_input)

    assert isinstance(result, Success)
    assert isinstance(result.value, expected)


def test_failure():
    h = Headers()

    result = h(b'Invalid')

    assert isinstance(result, Failure)
