#!/usr/bin/env python3

from aiospamc.headers import Spam


def test_bytes():
    spam = Spam(value=True, score=4.0, threshold=2.0)

    assert bytes(spam) == b'Spam: True ; 4.0 / 2.0\r\n'


def test_repr():
    spam = Spam(value=True, score=4.0, threshold=2.0)
    assert repr(spam) == 'Spam(value=True, score=4.0, threshold=2.0)'


def test_default_value():
    spam = Spam()

    assert spam.value is False
    assert spam.score == 0.0
    assert spam.threshold == 0.0


def test_user_value():
    spam = Spam(value=True, score=4.0, threshold=2.0)

    assert spam.value is True
    assert spam.score == 4.0
    assert spam.threshold == 2.0


def test_field_name():
    spam = Spam()
    assert spam.field_name() == 'Spam'
