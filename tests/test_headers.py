#!/usr/bin/env python3

import pytest

from aiospamc.headers import *


def test_compress_instantiates():
    compress = Compress()
    assert compress

def test_compress_value():
    compress = Compress()
    assert compress.zlib

def test_compress_header_field_name():
    compress = Compress()
    assert compress.header_field_name() == 'Compress'

def test_compress_compose():
    compress = Compress()
    assert compress.compose() == 'Compress: zlib\r\n'