#!/usr/bin/env python3

from base64 import b64encode

import pytest
from aiospamc.header_values import (
    ActionOption,
    BytesHeaderValue,
    CompressValue,
    ContentLengthValue,
    GenericHeaderValue,
    Headers,
    MessageClassOption,
    MessageClassValue,
    SetOrRemoveValue,
    SpamValue,
    UserValue,
)


def test_bytes_value():
    b = BytesHeaderValue(b"test")

    assert b"test" == b.value


def test_bytes_bytes():
    b = BytesHeaderValue(b"test")

    assert b"test" == bytes(b)


def test_bytes_to_json():
    b = BytesHeaderValue(b"test")
    expected = b64encode(b"test").decode()

    assert expected == b.to_json()


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

    assert expected == bytes(m)


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


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (GenericHeaderValue("value"), "value"),
        (CompressValue(), "zlib"),
        (ContentLengthValue(42), 42),
        (
            SetOrRemoveValue(ActionOption(local=True, remote=False)),
            {"local": True, "remote": False},
        ),
        (MessageClassValue(value=MessageClassOption.ham), "ham"),
        (
            SpamValue(value=True, score=1.0, threshold=10.0),
            {"value": True, "score": 1.0, "threshold": 10.0},
        ),
        (UserValue("username"), "username"),
    ],
)
def test_to_json(test_input, expected):
    result = test_input.to_json()

    assert expected == result


def test_headers_get_header():
    h = Headers({"Exists": GenericHeaderValue("test")})

    assert None is h.get_header("Doesnt-exist")
    assert "test" == h.get_header("Exists")


def test_headers_set_header():
    h = Headers()
    h.set_header("Test", "test")

    assert "test" == h.get_header("Test")


def test_headers_get_bytes_header():
    test_input = BytesHeaderValue(b"test")
    h = Headers({"Exists": BytesHeaderValue(test_input)})

    assert None is h.get_bytes_header("Doesnt-exist")
    assert test_input == h.get_bytes_header("Exists")


def test_headers_set_bytes_header():
    test_input = BytesHeaderValue(b"test")
    h = Headers()
    h.set_bytes_header("Test", test_input)

    assert test_input == h.get_bytes_header("Test")


def test_headers_compress():
    test_input = CompressValue()
    h = Headers()

    assert None is h.compress
    h.compress = test_input
    assert test_input == h.compress


def test_headers_content_length():
    test_input = ContentLengthValue()
    h = Headers()

    assert None is h.content_length
    h.content_length = test_input
    assert test_input == h.content_length


def test_headers_message_class():
    test_input = MessageClassOption.ham
    h = Headers()

    assert None is h.message_class
    h.message_class = test_input
    assert test_input == h.message_class


def test_headers_set():
    test_input = SetOrRemoveValue(action=ActionOption(False, False))
    h = Headers()

    assert None is h.set_
    h.set_ = test_input
    assert test_input == h.set_


def test_headers_remove():
    test_input = SetOrRemoveValue(action=ActionOption(False, False))
    h = Headers()

    assert None is h.remove
    h.remove = test_input
    assert test_input == h.remove


def test_headers_did_set():
    test_input = SetOrRemoveValue(action=ActionOption(False, False))
    h = Headers()

    assert None is h.did_set
    h.did_set = test_input
    assert test_input == h.did_set


def test_headers_did_remove():
    test_input = SetOrRemoveValue(action=ActionOption(False, False))
    h = Headers()

    assert None is h.did_remove
    h.did_remove = test_input
    assert test_input == h.did_remove


def test_headers_spam():
    test_input = SpamValue()
    h = Headers()

    assert None is h.spam
    h.spam = test_input
    assert test_input == h.spam


def test_headers_user():
    test_input = UserValue()
    h = Headers()

    assert None is h.user
    h.user = test_input
    assert test_input == h.user
