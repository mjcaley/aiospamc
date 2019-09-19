#!/usr/bin/env python3

from aiospamc.headers import Compress


def test_bytes():
    compress = Compress()

    assert bytes(compress) == b'Compress: zlib\r\n'


def test_repr():
    compress = Compress()

    assert repr(compress) == 'Compress()'


def test_value():
    compress = Compress()

    assert compress.zlib is True


def test_field_name():
    compress = Compress()

    assert compress.field_name() == 'Compress'
