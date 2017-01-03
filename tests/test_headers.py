#!/usr/bin/env python3
#pylint: disable=no-self-use

import pytest

from aiospamc.exceptions import HeaderCantParse
from aiospamc.headers import (Header, Compress, ContentLength, MessageClass,
                              _SetRemove, DidRemove, DidSet, Remove, Set,
                              Spam, User, XHeader, header_from_string)
from aiospamc.options import Action, MessageClassOption


class TestHeader:
    def test_str(self):
        header = Header()
        with pytest.raises(NotImplementedError):
            str(header)

    def test_header_field_name(self):
        header = Header()
        with pytest.raises(NotImplementedError):
            header.header_field_name()

class TestCompressHeader:
    def test_instantiates(self):
        compress = Compress()
        assert 'compress' in locals()

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
        assert 'content_length' in locals()

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
        assert 'content_length' in locals()

    def test_parse_invalid(self):
        with pytest.raises(HeaderCantParse):
            content_length = ContentLength.parse('invalid')

class TestMessageClass:
    def test_instantiates(self):
        message_class = MessageClass()
        assert 'message_class' in locals()

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
        assert 'message_class' in locals()

    def test_parse_invalid(self):
        with pytest.raises(HeaderCantParse):
            message_class = MessageClass.parse('invalid')

class Test_SetRemove:
    def test_instantiates(self):
        _set_remove = _SetRemove()
        assert '_set_remove' in locals()

    def test_default_value(self):
        _set_remove = _SetRemove()
        assert _set_remove.action == Action(True, False)

    def test_user_value(self):
        _set_remove = _SetRemove(Action(True, True))
        assert _set_remove.action == Action(True, True)

    def test_header_field_name(self):
        _set_remove = _SetRemove()
        with pytest.raises(NotImplementedError):
            _set_remove.header_field_name()

    def test_parse_valid_local(self):
        _set_remove = _SetRemove.parse('local')
        assert '_set_remove' in locals()

    def test_parse_valid_remote(self):
        _set_remove = _SetRemove.parse('remote')
        assert '_set_remove' in locals()

    def test_parse_valid_local_remote(self):
        _set_remove = _SetRemove.parse('local, remote')
        assert '_set_remove' in locals()

    def test_parse_valid_remote_local(self):
        _set_remove = _SetRemove.parse('remote, local')
        assert '_set_remove' in locals()

    def test_parse_invalid(self):
        with pytest.raises(HeaderCantParse):
            _set_remove = _SetRemove.parse('invalid')

class TestDidRemove:
    def test_header_field_name(self):
        did_remove = DidRemove()
        assert did_remove.header_field_name() == 'DidRemove'

    def test_compose_local(self):
        did_remove = DidRemove(Action(local=True, remote=False))
        assert did_remove.compose() == 'DidRemove: local\r\n'

    def test_compose_remote(self):
        did_remove = DidRemove(Action(local=False, remote=True))
        assert did_remove.compose() == 'DidRemove: remote\r\n'

    def test_compose_local_remote(self):
        did_remove = DidRemove(Action(local=True, remote=True))
        assert did_remove.compose() == 'DidRemove: local, remote\r\n'

class TestDidSet:
    def test_header_field_name(self):
        did_set = DidSet()
        assert did_set.header_field_name() == 'DidSet'

    def test_compose_local(self):
        did_set = DidSet(Action(local=True, remote=False))
        assert did_set.compose() == 'DidSet: local\r\n'

    def test_compose_remote(self):
        did_set = DidSet(Action(local=False, remote=True))
        assert did_set.compose() == 'DidSet: remote\r\n'

    def test_compose_local_remote(self):
        did_set = DidSet(Action(local=True, remote=True))
        assert did_set.compose() == 'DidSet: local, remote\r\n'

class TestRemove:
    def test_header_field_name(self):
        remove = Remove()
        assert remove.header_field_name() == 'Remove'

    def test_compose_local(self):
        remove = Remove(Action(local=True, remote=False))
        assert remove.compose() == 'Remove: local\r\n'

    def test_compose_remote(self):
        remove = Remove(Action(local=False, remote=True))
        assert remove.compose() == 'Remove: remote\r\n'

    def test_compose_local_remote(self):
        remove = Remove(Action(local=True, remote=True))
        assert remove.compose() == 'Remove: local, remote\r\n'

class TestSet:
    def test_header_field_name(self):
        set = Set()
        assert set.header_field_name() == 'Set'

    def test_compose_local(self):
        set = Set(Action(local=True, remote=False))
        assert set.compose() == 'Set: local\r\n'

    def test_compose_remote(self):
        set = Set(Action(local=False, remote=True))
        assert set.compose() == 'Set: remote\r\n'

    def test_compose_local_remote(self):
        set = Set(Action(local=True, remote=True))
        assert set.compose() == 'Set: local, remote\r\n'

class TestSpam:
    def test_instantiates(self):
        spam = Spam()
        assert 'spam' in locals()

    def test_default_value(self):
        spam = Spam()
        assert spam.value == False and spam.score == 0.0 and spam.threshold == 0.0

    def test_user_value(self):
        spam = Spam(value=True, score=4.0, threshold=2.0)
        assert spam.value == True and spam.score == 4.0 and spam.threshold == 2.0

    def test_header_field_name(self):
        spam = Spam()
        assert spam.header_field_name() == 'Spam'

    def test_compose(self):
        spam = Spam()
        assert spam.compose() == 'Spam: False ; 0.0 / 0.0\r\n'

    def test_parse_valid(self):
        spam = Spam.parse('True ; 4.0 / 2.0')
        assert 'spam' in locals()

    def test_parse_invalid(self):
        with pytest.raises(HeaderCantParse):
            spam = Spam.parse('invalid')

class TestUser:
    def test_instantiates(self):
        user = User()
        assert 'user' in locals()

    def test_default_value(self):
        import getpass
        user = User()
        assert user.name == getpass.getuser()

    def test_user_value(self):
        fake_user = 'fake_user_name_for_aiospamc_test'
        user = User(fake_user)
        assert user.name == fake_user

    def test_header_field_name(self):
        user = User()
        assert user.header_field_name() == 'User'

    def test_compose(self):
        import getpass
        user = User()
        assert user.compose() == 'User: {}\r\n'.format(getpass.getuser())

    def test_parse_valid(self):
        user = User.parse('fake_user_name_for_aiospamc_test')
        assert 'user' in locals()

    def test_parse_invalid(self):
        with pytest.raises(HeaderCantParse):
            user = User.parse('invalid=chars+[];\'\\"')

class TestXHeader:
    def test_instantiates(self):
        x_header = XHeader('head-name', 'head-value')
        assert 'x_header' in locals()

    def test_user_value(self):
        x_header = XHeader('head-name', 'head-value')
        assert x_header.name == 'head-name' and x_header.value == 'head-value'

    def test_header_field_name(self):
        x_header = XHeader('head-name', 'head-value')
        assert x_header.header_field_name() == 'head-name'

    def test_compose(self):
        x_header = XHeader('head-name', 'head-value')
        assert x_header.compose() == 'head-name: head-value\r\n'

    def test_parse_valid(self):
        x_header = XHeader.parse('head-name : head-value')
        assert 'x_header' in locals()

    def test_parse_invalid(self):
        with pytest.raises(HeaderCantParse):
            x_header = XHeader.parse('invalid = invalid')

class TestHeaderFromString:
    def test_compress(self):
        obj = header_from_string('Compress: zlib')
        assert isinstance(obj, Compress)

    def test_content_length(self):
        obj = header_from_string('Content-length: 42')
        assert isinstance(obj, ContentLength)

    def test_message_class(self):
        obj = header_from_string('Message-class: spam')
        assert isinstance(obj, MessageClass)

    def test_did_remove(self):
        obj = header_from_string('DidRemove: local, remote')
        assert isinstance(obj, DidRemove)

    def test_did_set(self):
        obj = header_from_string('DidSet: local, remote')
        assert isinstance(obj, DidSet)

    def test_remove(self):
        obj = header_from_string('Remove: local, remote')
        assert isinstance(obj, Remove)

    def test_set(self):
        obj = header_from_string('Set: local, remote')
        assert isinstance(obj, Set)

    def test_spam(self):
        obj = header_from_string('Spam: True ; 4.0 / 2.0')
        assert isinstance(obj, Spam)

    def test_user(self):
        obj = header_from_string('User: test-user')
        assert isinstance(obj, User)

    def test_x_header(self):
        obj = header_from_string('X-Extension: Value')
        assert isinstance(obj, XHeader)

    def test_invalid(self):
        with pytest.raises(HeaderCantParse):
            obj = header_from_string('Invalid Header Text')
