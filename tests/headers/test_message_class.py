#!/usr/bin/env python3

from aiospamc.headers import MessageClass
from aiospamc.options import MessageClassOption


def test_bytes():
    message_class = MessageClass(MessageClassOption.ham)

    assert bytes(message_class) == b'Message-class: ham\r\n'


def test_repr():
    message_class = MessageClass(MessageClassOption.ham)

    assert repr(message_class) == 'MessageClass(value=MessageClassOption.ham)'


def test_default_value():
    message_class = MessageClass()

    assert message_class.value == MessageClassOption.ham


def test_user_value_ham():
    message_class = MessageClass(MessageClassOption.ham)

    assert message_class.value == MessageClassOption.ham


def test_user_value_spam():
    message_class = MessageClass(MessageClassOption.spam)

    assert message_class.value == MessageClassOption.spam


def test_field_name():
    message_class = MessageClass()

    assert message_class.field_name() == 'Message-class'
