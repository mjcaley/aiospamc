#!/usr/bin/env python3

import zlib

import pytest

from aiospamc.common import SpamcBody, SpamcHeaders
from aiospamc.headers import Compress, ContentLength, XHeader


def test_body_get_set_value(mocker):
    class Stub:
        body = SpamcBody()
    stub = Stub()
    bytes_mock = mocker.MagicMock()
    stub.body = bytes_mock

    assert stub.body == bytes(bytes_mock)


def test_headers_instantiates_none():
    h = SpamcHeaders()

    assert 'h' in locals()


def test_headers_instantiates_list():
    h = SpamcHeaders(headers=[])

    assert 'h' in locals()


def test_headers_instantiate_list():
    h = SpamcHeaders(headers=[Compress(), ContentLength(length=42)])

    assert 'h' in locals()


def test_headers_get_item():
    header1 = Compress()
    h = SpamcHeaders(headers=[header1])
    result = h[header1.field_name()]

    assert result is header1


def test_headers_set_item():
    header1 = Compress()
    h = SpamcHeaders()
    h[header1.field_name()] = header1

    assert h[header1.field_name()] is header1


def test_headers_iter():
    headers = [XHeader(name='A', value='a'), XHeader(name='B', value='b')]
    h = SpamcHeaders(headers=headers)
    header_fields = [header.field_name() for header in headers]

    for test_result in iter(h):
        assert test_result in header_fields


def test_headers_keys():
    headers = [XHeader(name='A', value='a'), XHeader(name='B', value='b')]
    h = SpamcHeaders(headers=headers)
    header_fields = [header.field_name() for header in headers]

    for test_result in h.keys():
        assert test_result in header_fields


def test_headers_items():
    headers = [XHeader(name='A', value='a'), XHeader(name='B', value='b')]
    h = SpamcHeaders(headers=headers)
    header_tuples = [(header.field_name(), header) for header in headers]

    for test_result in h.items():
        assert test_result in header_tuples


def test_headers_values():
    headers = [XHeader(name='A', value='a'), XHeader(name='B', value='b')]
    h = SpamcHeaders(headers=headers)

    for test_result in h.values():
        assert test_result in headers


def test_headers_len():
    headers = [Compress(), ContentLength(length=10)]
    h = SpamcHeaders(headers=headers)

    assert len(h) == 2


def test_headers_bytes():
    headers = [XHeader(name='A', value='a'), XHeader(name='B', value='b')]
    h = SpamcHeaders(headers=headers)
    result = bytes(h)

    header_bytes = [bytes(header) for header in headers]
    for header in header_bytes:
        assert header in result
