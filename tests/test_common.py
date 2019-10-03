#!/usr/bin/env python3

from aiospamc.common import SpamcBody, SpamcHeaders
from aiospamc.header_values import CompressValue, ContentLengthValue, HeaderValue


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


def test_headers_instantiates_dict():
    h = SpamcHeaders(headers={})

    assert 'h' in locals()


def test_headers_instantiate_dict_headers():
    h = SpamcHeaders(headers={'Compress': CompressValue(), 'Content-length': ContentLengthValue(length=42)})

    assert 'h' in locals()


def test_headers_instantiates_dict_str_and_int():
    h = SpamcHeaders(headers={'Compress': 'zlib', 'Content-length': 42})

    assert 'h' in locals()


def test_headers_get_item():
    header1 = CompressValue()
    h = SpamcHeaders(headers={'Compress': header1})
    result = h['Compress']

    assert result is header1


def test_headers_set_item():
    header1 = CompressValue()
    h = SpamcHeaders()
    h['Compress'] = header1

    assert h['Compress'] is header1


def test_headers_iter():
    h = SpamcHeaders(headers={'A': HeaderValue(value='a'), 'B': HeaderValue(value='b')})

    for test_result in iter(h):
        assert test_result in ['A', 'B']


def test_headers_keys():
    h = SpamcHeaders(headers={'A': HeaderValue(value='a'), 'B': HeaderValue(value='b')})

    for test_result in h.keys():
        assert test_result in ['A', 'B']


def test_headers_items():
    headers = {'A': HeaderValue(value='a'), 'B': HeaderValue(value='b')}
    h = SpamcHeaders(headers=headers)

    for test_key, test_value in h.items():
        assert test_key in headers
        assert headers[test_key] is test_value


def test_headers_values():
    values = [HeaderValue(value='a'), HeaderValue(value='b')]
    h = SpamcHeaders(headers={'A': values[0], 'B': values[1]})

    for test_result in h.values():
        assert test_result in values


def test_headers_len():
    h = SpamcHeaders(headers={'A': HeaderValue(value='a'), 'B': HeaderValue(value='b')})

    assert len(h) == 2


def test_headers_bytes():
    h = SpamcHeaders(headers={'A': HeaderValue(value='a'), 'B': HeaderValue(value='b')})
    result = bytes(h)

    header_bytes = [b': '.join([name.encode('ascii'), bytes(value), b'\r\n']) for name, value in h.items()]
    for header in header_bytes:
        assert header in result
