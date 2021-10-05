#!/usr/bin/env python3

import pytest

from aiospamc.options import ActionOption, MessageClassOption
from aiospamc.header_values import (
    BytesHeaderValue,
    HeaderValue,
    GenericHeaderValue,
    CompressValue,
    ContentLengthValue,
    MessageClassValue,
    SetOrRemoveValue,
    SpamValue,
    UserValue,
)


def test_header_value_bytes_raises():
    with pytest.raises(NotImplementedError):
        bytes(HeaderValue())


def test_bytes_value():
    b = BytesHeaderValue(b"test")

    assert b"test" == b.value


def test_bytes_bytes():
    b = BytesHeaderValue(b"test")

    assert b"test" == bytes(b)


def test_bytes_eq_true():
    b = BytesHeaderValue(b"test")

    assert BytesHeaderValue(b"test") == b


def test_bytes_eq_false():
    b = BytesHeaderValue(b"test")

    assert BytesHeaderValue(b"other") != b


def test_bytes_eq_fail():
    b = BytesHeaderValue(b"test")

    assert "other" != b


def test_header_bytes():
    h = GenericHeaderValue(value="value", encoding="utf8")

    assert bytes(h) == b"value"


def test_compress_bytes():
    c = CompressValue()

    assert bytes(c) == b"zlib"


def test_content_length_bytes():
    c = ContentLengthValue(length=42)

    assert bytes(c) == b"42"


def test_content_length_int():
    c = ContentLengthValue(length=42)

    assert 42 == int(c)


@pytest.mark.parametrize(
    "test_input,expected",
    [[MessageClassOption.ham, b"ham"], [MessageClassOption.spam, b"spam"]],
)
def test_message_class_bytes(test_input, expected):
    m = MessageClassValue(value=test_input)

    assert bytes(m) == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        [ActionOption(local=False, remote=False), b""],
        [ActionOption(local=True, remote=False), b"local"],
        [ActionOption(local=False, remote=True), b"remote"],
        [ActionOption(local=True, remote=True), b"local, remote"],
    ],
)
def test_set_or_remove_bytes(test_input, expected):
    s = SetOrRemoveValue(action=test_input)

    assert bytes(s) == expected


@pytest.mark.parametrize(
    "value,score,threshold,expected",
    [
        [True, 1, 42, b"True ; 1.0 / 42.0"],
        [False, 1, 42, b"False ; 1.0 / 42.0"],
        [True, 1.0, 42.0, b"True ; 1.0 / 42.0"],
    ],
)
def test_spam_bytes(value, score, threshold, expected):
    s = SpamValue(value=value, score=score, threshold=threshold)

    assert bytes(s) == expected


def test_spam_bool_true():
    s = SpamValue(value=True)

    assert True is bool(s)


def test_spam_bool_false():
    s = SpamValue(value=False)

    assert False is bool(s)


def test_user_str():
    u = UserValue(name="username")

    assert str(u) == "username"


def test_user_bytes():
    u = UserValue(name="username")

    assert bytes(u) == b"username"


@pytest.mark.parametrize(
    "test_input",
    [
        GenericHeaderValue("value"),
        CompressValue(),
        ContentLengthValue(),
        SetOrRemoveValue(ActionOption(local=True, remote=False)),
        MessageClassValue(value=MessageClassOption.ham),
        SpamValue(),
        UserValue(),
    ],
)
def test_equal(test_input):
    assert test_input == test_input


@pytest.mark.parametrize(
    "test_input",
    [
        GenericHeaderValue("value"),
        CompressValue(),
        ContentLengthValue(),
        SetOrRemoveValue(ActionOption(local=True, remote=False)),
        MessageClassValue(value=MessageClassOption.ham),
        SpamValue(),
        UserValue(),
    ],
)
def test_eq_attribute_exception_false(test_input):
    class Empty:
        pass

    e = Empty()

    assert test_input != e
