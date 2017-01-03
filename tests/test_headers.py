#!/usr/bin/env python3

import pytest

from aiospamc.exceptions import HeaderCantParse
from aiospamc.headers import Compress, ContentLength


class TestCompressHeader:
    def test_instantiates(self):
        compress = Compress()
        assert compress

    def test_value(self):
        compress = Compress()
        assert compress.zlib is not False

    def test_header_field_name(self):
        compress = Compress()
        assert compress.header_field_name() == 'Compress'

    def test_compose(self):
        compress = Compress()
        assert compress.compose() == 'Compress: zlib\r\n'

    def test_parse_valid(self):
        compress = Compress()
        assert compress.parse('zlib')

    def test_parse_invalid(self):
        compress = Compress()
        with pytest.raises(HeaderCantParse):
            compress.parse('invalid')

class TestContentLength:
    def test_instantiates(self):
        content_length = ContentLength()
        assert content_length

    def test_value(self):
        content_length = ContentLength()
        assert content_length.length is not False

    def test_header_field_name(self):
        content_length = ContentLength()
        assert content_length.header_field_name() == 'Content-length'

    def test_compose(self):
        content_length = ContentLength()
        assert content_length.compose() == 'Content-length: 0\r\n'

    def test_parse_valid(self):
        content_length = ContentLength.parse('42')
        assert content_length

    def test_parse_invalid(self):
        with pytest.raises(HeaderCantParse):
            content_length = ContentLength.parse('invalid')
