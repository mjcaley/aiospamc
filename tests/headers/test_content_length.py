#!/usr/bin/env python3

from aiospamc.headers import ContentLength


def test_bytes():
    content_length = ContentLength()

    assert bytes(content_length) == b'Content-length: 0\r\n'


def test_repr():
    content_length = ContentLength()

    assert repr(content_length) == 'ContentLength(length=0)'


def test_default_value():
    content_length = ContentLength()

    assert content_length.length == 0


def test_user_value():
    content_length = ContentLength(42)

    assert content_length.length == 42


def test_field_name():
    content_length = ContentLength()

    assert content_length.field_name() == 'Content-length'
