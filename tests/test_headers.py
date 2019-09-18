#!/usr/bin/env python3

import pytest

from aiospamc.headers import (Header, Compress, ContentLength, MessageClass,
                              _SetRemoveBase, DidRemove, DidSet, Remove, Set,
                              Spam, User, XHeader)
from aiospamc.options import ActionOption, MessageClassOption


class TestHeader:
    def test_bytes(self):
        header = Header()
        with pytest.raises(NotImplementedError):
            bytes(header)

    def test_len(self):
        header = Header()
        with pytest.raises(NotImplementedError):
            len(header)

    def test_field_name(self):
        header = Header()
        with pytest.raises(NotImplementedError):
            header.field_name()


class TestCompressHeader:
    def test_instantiates(self):
        compress = Compress()

        assert 'compress' in locals()

    def test_bytes(self):
        compress = Compress()

        assert bytes(compress) == b'Compress: zlib\r\n'

    def test_repr(self):
        compress = Compress()

        assert repr(compress) == 'Compress()'

    def test_value(self):
        compress = Compress()

        assert compress.zlib == True

    def test_field_name(self):
        compress = Compress()

        assert compress.field_name() == 'Compress'


class TestContentLength:
    def test_instantiates(self):
        content_length = ContentLength()

        assert 'content_length' in locals()

    def test_bytes(self):
        content_length = ContentLength()

        assert bytes(content_length) == b'Content-length: 0\r\n'

    def test_repr(self):
        content_length = ContentLength()

        assert repr(content_length) == 'ContentLength(length=0)'

    def test_default_value(self):
        content_length = ContentLength()

        assert content_length.length == 0

    def test_user_value(self):
        content_length = ContentLength(42)

        assert content_length.length == 42

    def test_field_name(self):
        content_length = ContentLength()

        assert content_length.field_name() == 'Content-length'


class TestMessageClass:
    def test_instantiates(self):
        message_class = MessageClass()

        assert 'message_class' in locals()

    def test_bytes(self):
        message_class = MessageClass(MessageClassOption.ham)

        assert bytes(message_class) == b'Message-class: ham\r\n'

    def test_repr(self):
        message_class = MessageClass(MessageClassOption.ham)

        assert repr(message_class) == 'MessageClass(value=MessageClassOption.ham)'

    def test_default_value(self):
        message_class = MessageClass()

        assert message_class.value == MessageClassOption.ham

    def test_user_value_ham(self):
        message_class = MessageClass(MessageClassOption.ham)

        assert message_class.value == MessageClassOption.ham

    def test_user_value_spam(self):
        message_class = MessageClass(MessageClassOption.spam)

        assert message_class.value == MessageClassOption.spam

    def test_field_name(self):
        message_class = MessageClass()

        assert message_class.field_name() == 'Message-class'


# class Test_SetRemoveBase:
#     def test_instantiates(self):
#         _set_remove = _SetRemoveBase()
#
#         assert '_set_remove' in locals()
#
#     def test_default_value(self):
#         _set_remove = _SetRemoveBase()
#
#         assert _set_remove.action == ActionOption(False, False)
#
#     def test_user_value(self):
#         _set_remove = _SetRemoveBase(ActionOption(True, True))
#
#         assert _set_remove.action == ActionOption(True, True)
#
#     def test_field_name(self):
#         _set_remove = _SetRemoveBase()
#         with pytest.raises(NotImplementedError):
#             _set_remove.field_name()


class TestDidRemove:
    def test_field_name(self):
        did_remove = DidRemove()

        assert did_remove.field_name() == 'DidRemove'

    def test_repr(self):
        did_remove = DidRemove(ActionOption(local=True, remote=True))

        assert repr(did_remove) == 'DidRemove(action=ActionOption(local=True, remote=True))'

    @pytest.mark.parametrize('test_input,expected', [
        (ActionOption(local=True, remote=False), b'DidRemove: local\r\n'),
        (ActionOption(local=False, remote=True), b'DidRemove: remote\r\n'),
        (ActionOption(local=True, remote=True), b'DidRemove: local, remote\r\n'),
        (ActionOption(local=False, remote=False), b''),
    ])
    def test_bytes(self, test_input, expected):
        did_remove = DidRemove(test_input)

        assert bytes(did_remove) == expected


class TestDidSet:
    def test_field_name(self):
        did_set = DidSet()

        assert did_set.field_name() == 'DidSet'

    def test_repr(self):
        did_set = DidSet(ActionOption(local=True, remote=True))

        assert repr(did_set) == 'DidSet(action=ActionOption(local=True, remote=True))'

    @pytest.mark.parametrize('test_input,expected', [
        (ActionOption(local=True, remote=False), b'DidSet: local\r\n'),
        (ActionOption(local=False, remote=True), b'DidSet: remote\r\n'),
        (ActionOption(local=True, remote=True), b'DidSet: local, remote\r\n'),
        (ActionOption(local=False, remote=False), b''),
    ])
    def test_bytes(self, test_input, expected):
        did_set = DidSet(test_input)

        assert bytes(did_set) == expected


class TestRemove:
    def test_field_name(self):
        remove = Remove()

        assert remove.field_name() == 'Remove'

    def test_repr(self):
        remove = Remove(ActionOption(local=True, remote=True))

        assert repr(remove) == 'Remove(action=ActionOption(local=True, remote=True))'

    @pytest.mark.parametrize('test_input,expected', [
        (ActionOption(local=True, remote=False), b'Remove: local\r\n'),
        (ActionOption(local=False, remote=True), b'Remove: remote\r\n'),
        (ActionOption(local=True, remote=True), b'Remove: local, remote\r\n'),
        (ActionOption(local=False, remote=False), b''),
    ])
    def test_bytes(self, test_input, expected):
        remove = Remove(test_input)

        assert bytes(remove) == expected


class TestSet:
    def test_field_name(self):
        set_ = Set()

        assert set_.field_name() == 'Set'

    def test_repr(self):
        set_ = Set(ActionOption(local=True, remote=True))

        assert repr(set_) == 'Set(action=ActionOption(local=True, remote=True))'

    @pytest.mark.parametrize('test_input,expected', [
        (ActionOption(local=True, remote=False), b'Set: local\r\n'),
        (ActionOption(local=False, remote=True), b'Set: remote\r\n'),
        (ActionOption(local=True, remote=True), b'Set: local, remote\r\n'),
        (ActionOption(local=False, remote=False), b''),
    ])
    def test_bytes(self, test_input, expected):
        set_ = Set(test_input)

        assert bytes(set_) == expected


class TestSpam:
    def test_instantiates(self):
        spam = Spam()

        assert 'spam' in locals()

    def test_bytes(self):
        spam = Spam(value=True, score=4.0, threshold=2.0)

        assert bytes(spam) == b'Spam: True ; 4.0 / 2.0\r\n'

    def test_repr(self):
        spam = Spam(value=True, score=4.0, threshold=2.0)
        assert repr(spam) == 'Spam(value=True, score=4.0, threshold=2.0)'

    def test_default_value(self):
        spam = Spam()
        assert spam.value == False and spam.score == 0.0 and spam.threshold == 0.0

    def test_user_value(self):
        spam = Spam(value=True, score=4.0, threshold=2.0)
        assert spam.value == True and spam.score == 4.0 and spam.threshold == 2.0

    def test_field_name(self):
        spam = Spam()
        assert spam.field_name() == 'Spam'


class TestUser:
    def test_instantiates(self):
        user = User()

        assert 'user' in locals()

    def test_bytes(self):
        user = User('test-user')

        assert bytes(user) == b'User: test-user\r\n'

    def test_repr(self):
        user = User('test-user')

        assert repr(user) == 'User(name=\'test-user\')'

    def test_default_value(self):
        import getpass
        user = User()

        assert user.name == getpass.getuser()

    def test_user_value(self):
        fake_user = 'fake_user_name_for_aiospamc_test'
        user = User(fake_user)

        assert user.name == fake_user

    def test_field_name(self):
        user = User()

        assert user.field_name() == 'User'


class TestXHeader:
    def test_instantiates(self):
        x_header = XHeader('head-name', 'head-value')
        assert 'x_header' in locals()

    def test_bytes(self):
        x_header = XHeader('XHeader', 'head-value')

        assert bytes(x_header) == b'XHeader: head-value\r\n'

    def test_repr(self):
        x_header = XHeader('head-name', 'head-value')
        assert repr(x_header) == 'XHeader(name=\'head-name\', value=\'head-value\')'

    def test_user_value(self):
        x_header = XHeader('head-name', 'head-value')
        assert x_header.name == 'head-name' and x_header.value == 'head-value'

    def test_field_name(self):
        x_header = XHeader('head-name', 'head-value')
        assert x_header.field_name() == 'head-name'
