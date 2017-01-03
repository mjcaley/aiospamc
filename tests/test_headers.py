#!/usr/bin/env python3

import pytest

from aiospamc.exceptions import HeaderCantParse
from aiospamc.headers import Compress, ContentLength, MessageClass
from aiospamc.options import MessageClassOption


class TestCompressHeader:
    def test_instantiates(self):
        compress = Compress()
        assert compress

    def test_value(self):
        compress = Compress()
        assert compress.zlib == True

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
        with pytest.raises(HeaderCantParse):
            compress = Compress.parse('invalid')

class TestContentLength:
    def test_instantiates(self):
        content_length = ContentLength()
        assert content_length

    def test_default_value(self):
        content_length = ContentLength()
        assert content_length.length == 0

    def test_user_value(self):
        content_length = ContentLength(42)
        assert content_length.length == 42

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

class TestMessageClass:
    def test_instantiates(self):
        message_class = MessageClass()
        assert message_class

    def test_default_value(self):
        message_class = MessageClass()
        assert message_class.value == MessageClassOption.ham

    def test_user_value(self):
        message_class = MessageClass(MessageClassOption.spam)
        assert message_class.value == MessageClassOption.spam

    def test_header_field_name(self):
        message_class = MessageClass()
        assert message_class.header_field_name() == 'Message-class'

    def test_compose(self):
        message_class = MessageClass()
        assert message_class.compose() == 'Message-class: ham\r\n'

    def test_parse_valid(self):
        message_class = MessageClass.parse('spam')
        assert message_class

    def test_parse_invalid(self):
        with pytest.raises(HeaderCantParse):
            message_class = MessageClass.parse('invalid')