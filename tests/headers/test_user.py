#!/usr/bin/env python3

import getpass

from aiospamc.headers import User


def test_bytes():
    user = User('test-user')

    assert bytes(user) == b'User: test-user\r\n'


def test_repr():
    user = User('test-user')

    assert repr(user) == 'User(name=\'test-user\')'


def test_default_value():
    import getpass
    user = User()

    assert user.name == getpass.getuser()


def test_user_value():
    fake_user = 'fake_user_name_for_aiospamc_test'
    user = User(fake_user)

    assert user.name == fake_user


def test_field_name():
    user = User()

    assert user.field_name() == 'User'
