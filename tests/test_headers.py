#!/usr/bin/env python3

import pytest

from aiospamc.exceptions import HeaderCantParse
from aiospamc.headers import (Header, Compress, ContentLength, MessageClass,
                              _SetRemoveBase, _RemoveBase, _SetBase,
                              DidRemove, DidSet, Remove, Set,
                              Spam, User, XHeader, header_from_bytes)
from aiospamc.options import _Action, MessageClassOption, RemoveOption, SetOption


class TestHeader:
    def test_bytes(self):
        header = Header()
        with pytest.raises(NotImplementedError):
            bytes(header)

    def test_parse(self):
        with pytest.raises(NotImplementedError):
            Header.parse(b'')

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

    def test_parse_valid(self):
        compress = Compress()

        assert compress.parse(b'zlib')

    def test_parse_invalid(self):
        with pytest.raises(HeaderCantParse):
            compress = Compress.parse(b'invalid')

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

    def test_parse_valid(self):
        content_length = ContentLength.parse(b'42')

        assert 'content_length' in locals()

    def test_parse_invalid(self):
        with pytest.raises(HeaderCantParse):
            content_length = ContentLength.parse(b'invalid')

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

    @pytest.mark.parametrize('test_input', [
        b'ham',
        b'spam',
    ])
    def test_parse_valid(self, test_input):
        message_class = MessageClass.parse(test_input)

        assert 'message_class' in locals()

    def test_parse_invalid(self):
        with pytest.raises(HeaderCantParse):
            message_class = MessageClass.parse(b'invalid')

class Test_SetRemoveBase:
    def test_instantiates(self):
        _set_remove = _SetRemoveBase()

        assert '_set_remove' in locals()

    def test_default_value(self):
        _set_remove = _SetRemoveBase()

        assert _set_remove.action == _Action(False, False)

    def test_user_value(self):
        _set_remove = _SetRemoveBase(_Action(True, True))

        assert _set_remove.action == _Action(True, True)

    def test_field_name(self):
        _set_remove = _SetRemoveBase()
        with pytest.raises(NotImplementedError):
            _set_remove.field_name()

    @pytest.mark.parametrize('test_input', [
        b'local',
        b'remote',
        b'local, remote',
        b'remote, local',
    ])
    def test_parse_valid(self, test_input):
        _set_remove = _SetRemoveBase.parse(test_input)

        assert '_set_remove' in locals()

    def test_parse_invalid(self):
        with pytest.raises(HeaderCantParse):
            _set_remove = _SetRemoveBase.parse(b'invalid')

class Test_RemoveBase:
    def test_repr(self):
        _remove_base = _RemoveBase()

        assert repr(_remove_base) == '_RemoveBase(action=RemoveOption(local=False, remote=False))'

    def test_field_name(self):
        _remove_base = _RemoveBase()
        with pytest.raises(NotImplementedError):
            _remove_base.field_name()

class Test_SetBase:
    def test_repr(self):
        _set_base = _SetBase()

        assert repr(_set_base) == '_SetBase(action=SetOption(local=False, remote=False))'

    def test_field_name(self):
        _set_base = _SetBase()
        with pytest.raises(NotImplementedError):
            _set_base.field_name()

class TestDidRemove:
    def test_field_name(self):
        did_remove = DidRemove()

        assert did_remove.field_name() == 'DidRemove'

    def test_repr(self):
        did_remove = DidRemove(RemoveOption(local=True, remote=True))

        assert repr(did_remove) == 'DidRemove(action=RemoveOption(local=True, remote=True))'

    @pytest.mark.parametrize('test_input,expected', [
        (RemoveOption(local=True, remote=False), b'DidRemove: local\r\n'),
        (RemoveOption(local=False, remote=True), b'DidRemove: remote\r\n'),
        (RemoveOption(local=True, remote=True), b'DidRemove: local, remote\r\n'),
        (RemoveOption(local=False, remote=False), b''),
    ])
    def test_bytes(self, test_input, expected):
        did_remove = DidRemove(test_input)

        assert bytes(did_remove) == expected

class TestDidSet:
    def test_field_name(self):
        did_set = DidSet()

        assert did_set.field_name() == 'DidSet'

    def test_repr(self):
        did_set = DidSet(SetOption(local=True, remote=True))

        assert repr(did_set) == 'DidSet(action=SetOption(local=True, remote=True))'

    @pytest.mark.parametrize('test_input,expected', [
        (SetOption(local=True, remote=False), b'DidSet: local\r\n'),
        (SetOption(local=False, remote=True), b'DidSet: remote\r\n'),
        (SetOption(local=True, remote=True), b'DidSet: local, remote\r\n'),
        (SetOption(local=False, remote=False), b''),
    ])
    def test_bytes(self, test_input, expected):
        did_set = DidSet(test_input)

        assert bytes(did_set) == expected

class TestRemove:
    def test_field_name(self):
        remove = Remove()

        assert remove.field_name() == 'Remove'

    def test_repr(self):
        remove = Remove(SetOption(local=True, remote=True))

        assert repr(remove) == 'Remove(action=SetOption(local=True, remote=True))'

    @pytest.mark.parametrize('test_input,expected', [
        (SetOption(local=True, remote=False), b'Remove: local\r\n'),
        (SetOption(local=False, remote=True), b'Remove: remote\r\n'),
        (SetOption(local=True, remote=True), b'Remove: local, remote\r\n'),
        (SetOption(local=False, remote=False), b''),
    ])
    def test_bytes(self, test_input, expected):
        remove = Remove(test_input)

        assert bytes(remove) == expected

class TestSet:
    def test_field_name(self):
        set = Set()

        assert set.field_name() == 'Set'

    def test_repr(self):
        set_ = Set(SetOption(local=True, remote=True))

        assert repr(set_) == 'Set(action=SetOption(local=True, remote=True))'

    @pytest.mark.parametrize('test_input,expected', [
        (SetOption(local=True, remote=False), b'Set: local\r\n'),
        (SetOption(local=False, remote=True), b'Set: remote\r\n'),
        (SetOption(local=True, remote=True), b'Set: local, remote\r\n'),
        (SetOption(local=False, remote=False), b''),
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

    @pytest.mark.parametrize('test_input', [
        b'True ; 4.0 / 2.0',
        b'Yes ; 4.0 / 2.0',
        b'False ; 4.0 / 2.0',
        b'No ; 4.0 / 2.0',
    ])
    def test_parse_valid(self, test_input):
        spam = Spam.parse(test_input)

        assert 'spam' in locals()

    def test_parse_invalid(self):
        with pytest.raises(HeaderCantParse):
            spam = Spam.parse(b'invalid')

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

    def test_parse_valid(self):
        user = User.parse(b'fake_user_name_for_aiospamc_test')

        assert 'user' in locals()

    def test_parse_invalid(self):
        with pytest.raises(HeaderCantParse):
            user = User.parse(b'invalid=chars+[];\'\\"')

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

    def test_parse_valid(self):
        x_header = XHeader.parse(b'head-name : head-value')
        assert 'x_header' in locals()

    def test_parse_invalid(self):
        with pytest.raises(HeaderCantParse):
            x_header = XHeader.parse(b'invalid = invalid')

class TestHeaderFromBytes:
    def test_compress(self):
        obj = header_from_bytes(b'Compress: zlib')
        assert isinstance(obj, Compress)

    def test_content_length(self):
        obj = header_from_bytes(b'Content-length: 42')
        assert isinstance(obj, ContentLength)

    def test_message_class(self):
        obj = header_from_bytes(b'Message-class: spam')
        assert isinstance(obj, MessageClass)

    def test_did_remove(self):
        obj = header_from_bytes(b'DidRemove: local, remote')
        assert isinstance(obj, DidRemove)

    def test_did_set(self):
        obj = header_from_bytes(b'DidSet: local, remote')
        assert isinstance(obj, DidSet)

    def test_remove(self):
        obj = header_from_bytes(b'Remove: local, remote')
        assert isinstance(obj, Remove)

    def test_set(self):
        obj = header_from_bytes(b'Set: local, remote')
        assert isinstance(obj, Set)

    def test_spam(self):
        obj = header_from_bytes(b'Spam: True ; 4.0 / 2.0')
        assert isinstance(obj, Spam)

    def test_user(self):
        obj = header_from_bytes(b'User: test-user')
        assert isinstance(obj, User)

    def test_x_header(self):
        obj = header_from_bytes(b'X-Extension: Value')
        assert isinstance(obj, XHeader)

    def test_invalid(self):
        with pytest.raises(HeaderCantParse):
            obj = header_from_bytes(b'Invalid Header Text')
