#!/usr/bin/env python3

import zlib

import pytest
from fixtures import *

from aiospamc.common import RequestResponseBase
from aiospamc.headers import Compress, ContentLength


def test_common_instantiates():
    req_resp_base = RequestResponseBase()

    assert 'req_resp_base' in locals()

def test_common_instantiates_with_body():
    req_resp_base = RequestResponseBase(body='Test body\n')

    assert hasattr(req_resp_base, 'body')

def test_common_instantiates_with_headers():
    req_resp_base = RequestResponseBase(None, ContentLength(length=0))

    assert req_resp_base._headers['Content-length']

def test_common_parse():
    with pytest.raises(NotImplementedError):
        req_resp_base = RequestResponseBase.parse(b'')

@pytest.mark.parametrize('test_input,expected', [
    ([], ()),
    ([b'Content-length: 10'], (ContentLength,)),
    ([b'Content-length: 10', b''], (ContentLength,)),
    ([b'Content-length: 10', b'Compress: zlib'], (ContentLength, Compress)),
])
def test_common_parse_headers(test_input, expected):
    headers = RequestResponseBase._parse_headers(test_input)

    assert all(header.__class__ in expected for header in headers)

@pytest.mark.parametrize('test_input,headers,expected', [
    (b'Test body\n', [], 'Test body\n'),
    (b'', [], None),
    (zlib.compress('Test body\n'.encode()), [Compress()], 'Test body\n')
])
def test_common_parse_body(test_input, headers, expected):
    body = RequestResponseBase._parse_body(test_input, headers)

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
    req_resp_base = RequestResponseBase('Test body\n', Compress())
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
    req_resp_base = RequestResponseBase(None, ContentLength(length=0))
    req_resp_base.delete_header('Content-length')

    assert 'Content-length' not in req_resp_base._headers.keys()
