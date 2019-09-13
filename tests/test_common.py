#!/usr/bin/env python3

import zlib

import pytest

from aiospamc.common import RequestResponseBase, SpamcBody, SpamcHeaders
from aiospamc.headers import Compress, ContentLength, XHeader


def test_common_instantiates():
    req_resp_base = RequestResponseBase()

    assert 'req_resp_base' in locals()


def test_common_instantiates_with_body():
    req_resp_base = RequestResponseBase(body='Test body\n')

    assert hasattr(req_resp_base, 'body')


def test_instantiates_with_body_bytes():
    req_resp_base = RequestResponseBase(body=b'Test body\n')

    assert hasattr(req_resp_base, 'body')


def test_common_instantiates_with_headers():
    req_resp_base = RequestResponseBase(body=None,
                                        headers=(ContentLength(length=0),))

    assert isinstance(req_resp_base._headers['Content-length'],
                      ContentLength)


@pytest.mark.parametrize('test_input,headers,expected', [
    (b'Test body\n', [], 'Test body\n'),
    (b'', [], None),
    (zlib.compress('Test body\n'.encode()), [Compress()], 'Test body\n')
])
def test_common_parse_body(test_input, headers, expected):
    body = RequestResponseBase._decode_body(test_input, headers)

    assert body == expected


def test_common_content_length_added():
    req_resp_base = RequestResponseBase()
    req_resp_base.body = 'Test body\n'

    assert req_resp_base._headers['Content-length']


def test_common_compressed_when_header_added():
    req_resp_base = RequestResponseBase('Test body\n')
    req_resp_base.add_header(Compress())

    assert zlib.decompress(req_resp_base._compressed_body) == b'Test body\n'


def test_common_decompress_when_header_removed():
    req_resp_base = RequestResponseBase(body='Test body\n',
                                        headers=(Compress(),))
    req_resp_base.delete_header('Compress')

    assert req_resp_base._compressed_body is None


def test_common_delete_body_deleted_content_length():
    req_resp_base = RequestResponseBase(body='Test body\n')
    del req_resp_base.body

    assert 'Content-length' not in req_resp_base._headers


def test_common_add_header():
    req_resp_base = RequestResponseBase()
    req_resp_base.add_header(ContentLength(length=0))

    assert req_resp_base._headers['Content-length']


def test_common_get_header():
    req_resp_base = RequestResponseBase()
    req_resp_base.add_header(ContentLength(length=0))

    assert isinstance(req_resp_base.get_header('Content-length'), ContentLength)


def test_common_get_header_doesnt_exist():
    req_resp_base = RequestResponseBase()
    with pytest.raises(KeyError):
        req_resp_base.get_header('FakeHeader')


def test_common_delete_header():
    req_resp_base = RequestResponseBase(body=None,
                                        headers=(ContentLength(length=0),))
    req_resp_base.delete_header('Content-length')

    assert 'Content-length' not in req_resp_base._headers.keys()


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
