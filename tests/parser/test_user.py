#!/usr/bin/env python3

from aiospamc.parser import Success, Failure, UserHeader
from aiospamc.headers import User


def test_instantiates():
    u = UserHeader()

    assert 'u' in locals()


def test_success():
    u = UserHeader()

    result = u(b'User : username\r\n')

    assert isinstance(result, Success)
    assert isinstance(result.value, User)
    assert result.value.name == 'username'


def test_failure():
    u = UserHeader()

    result = u(b'Invalid')

    assert isinstance(result, Failure)
