#!/usr/bin/env python3

import pytest

from aiospamc.options import ActionOption, MessageClassOption
from aiospamc.header_values import GenericHeaderValue, CompressValue, ContentLengthValue, MessageClassValue, \
    SetOrRemoveValue, SpamValue, UserValue


def test_header_bytes():
    h = GenericHeaderValue(value='value', encoding='utf8')

    assert bytes(h) == b'value'


def test_header_repr():
    h = GenericHeaderValue(value='value')

    assert repr(h) == 'GenericHeaderValue(value={}, encoding={})'.format(repr(h.value), repr(h.encoding))


def test_compress_repr():
    c = CompressValue()

    assert repr(c) == 'CompressValue()'


def test_compress_bytes():
    c = CompressValue()

    assert bytes(c) == b'zlib'


def test_content_length_repr():
    c = ContentLengthValue(length=42)

    assert repr(c) == 'ContentLengthValue(length=42)'


def test_content_length_bytes():
    c = ContentLengthValue(length=42)

    assert bytes(c) == b'42'


@pytest.mark.parametrize('test_input,expected', [
    [MessageClassOption.ham, 'MessageClassValue(value=MessageClassOption.ham)'],
    [MessageClassOption.spam, 'MessageClassValue(value=MessageClassOption.spam)']
])
def test_message_class_repr(test_input, expected):
    m = MessageClassValue(value=test_input)

    assert repr(m) == expected


@pytest.mark.parametrize('test_input,expected', [
    [MessageClassOption.ham, b'ham'],
    [MessageClassOption.spam, b'spam']
])
def test_message_class_bytes(test_input, expected):
    m = MessageClassValue(value=test_input)

    assert bytes(m) == expected


@pytest.mark.parametrize('test_input', [
    ActionOption(local=False, remote=False),
    ActionOption(local=True, remote=False),
    ActionOption(local=False, remote=True),
    ActionOption(local=True, remote=True)
])
def test_set_or_remove_repr(test_input):
    s = SetOrRemoveValue(action=test_input)

    assert repr(s) == 'SetOrRemoveValue(action={})'.format(repr(test_input))


@pytest.mark.parametrize('test_input,expected', [
    [ActionOption(local=False, remote=False), b''],
    [ActionOption(local=True, remote=False), b'local'],
    [ActionOption(local=False, remote=True), b'remote'],
    [ActionOption(local=True, remote=True), b'local, remote']
])
def test_set_or_remove_bytes(test_input, expected):
    s = SetOrRemoveValue(action=test_input)

    assert bytes(s) == expected


@pytest.mark.parametrize('value,score,threshold,expected', [
    [True, 1, 42, 'SpamValue(value=True, score=1.0, threshold=42.0)'],
    [False, 1, 42, 'SpamValue(value=False, score=1.0, threshold=42.0)'],
    [True, 1.0, 42.0, 'SpamValue(value=True, score=1.0, threshold=42.0)']
])
def test_spam_repr(value, score, threshold, expected):
    s = SpamValue(value=value, score=score, threshold=threshold)

    assert repr(s) == 'SpamValue(value={}, score={}, threshold={})'.format(repr(value), repr(score), repr(threshold))


@pytest.mark.parametrize('value,score,threshold,expected', [
    [True, 1, 42, b'True ; 1.0 / 42.0'],
    [False, 1, 42, b'False ; 1.0 / 42.0'],
    [True, 1.0, 42.0, b'True ; 1.0 / 42.0']
])
def test_spam_bytes(value, score, threshold, expected):
    s = SpamValue(value=value, score=score, threshold=threshold)

    assert bytes(s) == expected


def test_user_repr():
    u = UserValue(name='username')

    assert repr(u) == 'UserValue(name={})'.format(repr('username'))


def test_user_bytes():
    u = UserValue(name='username')

    assert bytes(u) == b'username'


@pytest.mark.parametrize('test_input', [
    GenericHeaderValue('value'),
    CompressValue(),
    ContentLengthValue(),
    SetOrRemoveValue(ActionOption(local=True, remote=False)),
    MessageClassValue(value=MessageClassOption.ham),
    SpamValue(),
    UserValue()
])
def test_equal(test_input):
    assert test_input == test_input


@pytest.mark.parametrize('test_input', [
    GenericHeaderValue('value'),
    CompressValue(),
    ContentLengthValue(),
    SetOrRemoveValue(ActionOption(local=True, remote=False)),
    MessageClassValue(value=MessageClassOption.ham),
    SpamValue(),
    UserValue()
])
def test_eq_attribute_exception_false(test_input):
    class Empty:
        pass

    e = Empty()

    assert test_input != e
