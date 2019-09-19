#!/usr/bin/env python3

import pytest

from aiospamc.headers import Header


def test_bytes():
    header = Header()
    with pytest.raises(NotImplementedError):
        bytes(header)


def test_len():
    header = Header()
    with pytest.raises(NotImplementedError):
        len(header)


def test_field_name():
    header = Header()
    with pytest.raises(NotImplementedError):
        header.field_name()
