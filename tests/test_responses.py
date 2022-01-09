#!/usr/bin/env python3

import pytest

import zlib

from aiospamc.exceptions import *
from aiospamc.header_values import CompressValue, ContentLengthValue
from aiospamc.incremental_parser import ResponseParser
from aiospamc.responses import Response, Status


def test_init_version():
    r = Response(version="4.2", status_code=0, message="EX_OK")
    result = bytes(r).split(b" ")[0]

    assert result == b"SPAMD/4.2"


def test_init_status_code():
    r = Response(version="1.5", status_code=0, message="EX_OK")
    result = bytes(r).split(b" ")[1]

    assert result == str(0).encode()


def test_init_message():
    r = Response(version="1.5", status_code=0, message="EX_OK")
    result = bytes(r).split(b"\r\n")[0]

    assert result.endswith("EX_OK".encode())


def test_bytes_status():
    r = Response(status_code=999, message="Test message")
    result = bytes(r).partition(b"\r\n")[0]

    assert b"999 Test message" in result


def test_bytes_headers(x_headers):
    r = Response(version="1.5", status_code=0, message="EX_OK", headers=x_headers)
    result = bytes(r).partition(b"\r\n")[2]
    expected = b"".join(
        [
            b"%b: %b\r\n" % (key.encode("ascii"), bytes(value))
            for key, value in r.headers.items()
        ]
    )

    assert result.startswith(expected)
    assert result.endswith(b"\r\n\r\n")


def test_bytes_body():
    test_input = b"Test body\n"
    r = Response(version="1.5", status_code=0, message="EX_OK", body=test_input)
    result = bytes(r).rpartition(b"\r\n")[2]

    assert result == test_input


def test_bytes_body_compressed():
    test_input = b"Test body\n"
    r = Response(
        version="1.5",
        status_code=0,
        message="EX_OK",
        headers={"Compress": CompressValue()},
        body=test_input,
    )
    result = bytes(r).rpartition(b"\r\n")[2]

    assert result == zlib.compress(test_input)


def test_eq_other_obj_is_false():
    r = Response()

    assert False is (r == "")


def test_raise_for_status_ok():
    r = Response(version="1.5", status_code=0, message="")

    assert r.raise_for_status() is None


@pytest.mark.parametrize(
    "status_code, exception",
    [
        (64, UsageException),
        (65, DataErrorException),
        (66, NoInputException),
        (67, NoUserException),
        (68, NoHostException),
        (69, UnavailableException),
        (70, InternalSoftwareException),
        (71, OSErrorException),
        (72, OSFileException),
        (73, CantCreateException),
        (74, IOErrorException),
        (75, TemporaryFailureException),
        (76, ProtocolException),
        (77, NoPermissionException),
        (78, ConfigException),
        (79, ServerTimeoutException),
    ],
)
def test_raise_for_status(status_code, exception):
    r = Response(version="1.5", status_code=status_code, message="")

    with pytest.raises(exception):
        r.raise_for_status()


def test_raise_for_undefined_status():
    r = Response(version="1.5", status_code=999, message="")

    with pytest.raises(ResponseException):
        r.raise_for_status()


def test_response_from_parser_result(response_with_body):
    p = ResponseParser().parse(response_with_body)
    r = Response(**p)

    assert r is not None


def test_response_to_dict():
    test_body = b"Test body\n"
    result = Response(
        status_code=Status.EX_OK,
        headers={"Content-length": ContentLengthValue(len(test_body))},
        body=test_body,
    ).to_dict()

    assert "1.5" == result["version"]
    assert int(Status.EX_OK) == result["status_code"]
    assert test_body == result["body"]
    assert "Content-length" in result["headers"]
    assert {"length": len(result["body"])} == result["headers"]["Content-length"]
