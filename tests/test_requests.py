import zlib
from base64 import b64encode

from aiospamc.header_values import CompressValue, ContentLengthValue, Headers
from aiospamc.incremental_parser import RequestParser
from aiospamc.requests import Request


def test_init_verb():
    r = Request(verb="TEST")

    assert r.verb == "TEST"


def test_init_version():
    r = Request(verb="TEST", version="4.2")

    assert r.version == "4.2"


def test_init_headers():
    r = Request(verb="TEST")

    assert hasattr(r, "headers")


def test_init_headers_type():
    headers = Headers()
    r = Request(verb="TEST", headers=headers)

    assert headers is r.headers


def test_bytes_starts_with_verb():
    r = Request(verb="TEST")
    result = bytes(r)

    assert result.startswith(b"TEST")


def test_bytes_protocol():
    r = Request(verb="TEST", version="4.2")
    result = bytes(r).split(b"\r\n", 1)[0]

    assert result.endswith(b" SPAMC/4.2")


def test_bytes_headers(x_headers):
    r = Request(verb="TEST", headers=x_headers)
    result = bytes(r).partition(b"\r\n")[2]
    expected = b"\r\n".join(
        [
            b"%b: %b" % (key.encode("ascii"), bytes(value))
            for key, value in r.headers.items()
        ]
    )

    assert result.startswith(expected)
    assert result.endswith(b"\r\n\r\n")


def test_bytes_body():
    test_input = b"Test body\n"
    r = Request(verb="TEST", body=test_input)
    result = bytes(r).rpartition(b"\r\n")[2]

    assert result == test_input


def test_bytes_body_compressed():
    test_input = b"Test body\n"
    r = Request(verb="TEST", headers={"Compress": CompressValue()}, body=test_input)
    result = bytes(r).rpartition(b"\r\n")[2]

    assert result == zlib.compress(test_input)


def test_request_from_parser_result(request_with_body):
    p = RequestParser().parse(bytes(request_with_body))
    r = Request(**p)

    assert r is not None


def test_request_to_json():
    test_body = b"Test body\n"
    request = Request(
        "CHECK",
        headers={"Content-length": ContentLengthValue(len(test_body))},
        body=test_body,
    )
    result = request.to_json()

    assert "CHECK" == result["verb"]
    assert "1.5" == result["version"]
    assert b64encode(b"Test body\n").decode() == result["body"]
    assert "Content-length" in result["headers"]
    assert len(request.body) == result["headers"]["Content-length"]
