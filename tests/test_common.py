#!/usr/bin/env python3

from aiospamc.common import SpamcHeaders
from aiospamc.header_values import CompressValue, ContentLengthValue, GenericHeaderValue


def test_headers_instantiates_none():
    h = SpamcHeaders()

    assert "h" in locals()


def test_headers_instantiates_dict():
    h = SpamcHeaders(headers={})

    assert "h" in locals()


def test_headers_instantiate_dict_headers():
    compress_value = CompressValue()
    content_length_value = ContentLengthValue(length=42)
    h = SpamcHeaders(
        headers={"Compress": compress_value, "Content-length": content_length_value}
    )

    assert h["Compress"] is compress_value
    assert h["Content-length"] is content_length_value


def test_headers_instantiates_dict_str_and_int():
    h = SpamcHeaders(headers={"Compress": "zlib", "Content-length": 42})

    assert isinstance(h["Compress"], CompressValue)
    assert isinstance(h["Content-length"], ContentLengthValue)


def test_headers_get_item():
    header1 = CompressValue()
    h = SpamcHeaders(headers={"Compress": header1})
    result = h["Compress"]

    assert result is header1


def test_headers_set_item():
    header1 = CompressValue()
    h = SpamcHeaders()
    h["Compress"] = header1

    assert h["Compress"] is header1


def test_headers_iter():
    h = SpamcHeaders(
        headers={"A": GenericHeaderValue(value="a"), "B": GenericHeaderValue(value="b")}
    )

    for test_result in iter(h):
        assert test_result in ["A", "B"]


def test_headers_keys():
    h = SpamcHeaders(
        headers={"A": GenericHeaderValue(value="a"), "B": GenericHeaderValue(value="b")}
    )

    for test_result in h.keys():
        assert test_result in ["A", "B"]


def test_headers_items():
    headers = {"A": GenericHeaderValue(value="a"), "B": GenericHeaderValue(value="b")}
    h = SpamcHeaders(headers=headers)

    for test_key, test_value in h.items():
        assert test_key in headers
        assert headers[test_key] is test_value


def test_headers_values():
    values = [GenericHeaderValue(value="a"), GenericHeaderValue(value="b")]
    h = SpamcHeaders(headers={"A": values[0], "B": values[1]})

    for test_result in h.values():
        assert test_result in values


def test_headers_len():
    h = SpamcHeaders(
        headers={"A": GenericHeaderValue(value="a"), "B": GenericHeaderValue(value="b")}
    )

    assert len(h) == 2


def test_headers_str_object():
    h = SpamcHeaders()
    result = str(h)

    assert result.startswith(f"<aiospamc.common.SpamcHeaders object at {id(h)}")
    assert result.endswith(">")


def test_headers_str_keys():
    test_input = {"Content-length": 42, "User": "testuser"}
    h = SpamcHeaders(headers=test_input)
    result = str(h)
    keys_start = result.find("keys: ")
    keys_str = result[keys_start:-1].split("keys: ")[1].split(", ")

    for key_name in test_input.keys():
        assert key_name in keys_str


def test_headers_bytes():
    h = SpamcHeaders(
        headers={"A": GenericHeaderValue(value="a"), "B": GenericHeaderValue(value="b")}
    )
    result = bytes(h)

    header_bytes = [
        b"%b: %b\r\n" % (name.encode("ascii"), bytes(value))
        for name, value in h.items()
    ]
    for header in header_bytes:
        assert header in result
