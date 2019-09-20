#!/usr/bin/env python3

from aiospamc.headers import XHeader


def test_bytes():
    x_header = XHeader('XHeader', 'head-value')

    assert bytes(x_header) == b'XHeader: head-value\r\n'


def test_repr():
    x_header = XHeader('head-name', 'head-value')

    assert repr(x_header) == 'XHeader(name=\'head-name\', value=\'head-value\')'


def test_user_value():
    x_header = XHeader('head-name', 'head-value')

    assert x_header.name == 'head-name'
    assert x_header.value == 'head-value'


def test_field_name():
    x_header = XHeader('head-name', 'head-value')

    assert x_header.field_name() == 'head-name'
