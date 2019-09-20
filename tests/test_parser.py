#!/usr/bin/env python3

import pytest

from unittest.mock import Mock

from aiospamc.headers import Compress, ContentLength, DidRemove, DidSet, Remove, Set, MessageClass, Spam, User, XHeader
from aiospamc.requests import Request
from aiospamc.responses import Response, Status
from aiospamc.options import ActionOption, MessageClassOption

from aiospamc.parser import parse, Parser, ParseError


def test_parseerror_is_exception():
    assert issubclass(ParseError, Exception)


def test_parserror_instantiates():
    p = ParseError(index=0, message='Message')

    assert hasattr(p, 'index')
    assert hasattr(p, 'message')
    assert p.index == 0
    assert p.message == 'Message'


def test_parser_instantiates():
    p = Parser()

    assert 'p' in locals()
    assert p.string == b''
    assert p.index == 0


def test_parser_instantiates_with_string():
    p = Parser(b'data')

    assert 'p' in locals()
    assert p.string == b'data'
    assert p.index == 0


def test_parser_advance():
    p = Parser(b'data')
    p.advance(3)

    assert p.index == 3


def test_parser_current():
    p = Parser(b'data')

    assert p.current() == b'data'


@pytest.mark.parametrize('index,expected', [
    (0, False),
    (4, True),
    (100, True)
])
def test_parser_end(index, expected):
    p = Parser(b'data')
    p.index = index

    assert p.end() == expected


def test_parser_match_success():
    p = Parser(b'data')

    assert p.match(rb'data').group() == b'data'


def test_parser_match_fail():
    p = Parser(b'data')

    assert p.match(rb'invalid') is None


def test_parser_consume_success():
    p = Parser(b'data')
    result = p.consume(rb'data')

    assert result
    assert p.index == 4


def test_parser_consume_fail():
    p = Parser(b'data')

    with pytest.raises(ParseError):
        p.consume(rb'invalid')


@pytest.mark.parametrize('func', [
    Mock(),
    Mock(side_effect=ParseError(index=0, message='Raised'))
])
def test_parser_skip(func):
    p = Parser(b'data')

    p.test = func
    p.skip(p.test)

    assert p.test.called


@pytest.mark.parametrize('data,index', [
    (b' ', 1),
    (b'\t', 1),
    (b'     ', 5)
])
def test_parser_whitespace(data, index):
    p = Parser(data)
    p.whitespace()

    assert p.index == index


def test_parser_newline():
    p = Parser(b'\r\n')
    p.newline()

    assert p.index == 2


@pytest.mark.parametrize('data,expected', [
    (b'4.2', "4.2"),
    (b'42.42', "42.42")
])
def test_parser_version(data, expected):
    p = Parser(data)
    result = p.version()

    assert result == expected


def test_parser_body():
    p = Parser(b' 12345')
    p.index += 1
    result = p.body()

    assert result == b'12345'


@pytest.mark.parametrize('data', [
    b'zlib',
    b' zlib '
])
def test_parser_compress_value_success(data):
    p = Parser(data)
    result = p.compress_value()

    assert result == "zlib"


def test_parser_compress_value_fail():
    p = Parser(b'invalid')

    with pytest.raises(ParseError):
        p.compress_value()


@pytest.mark.parametrize('data,expected', [
    (b'4', 4),
    (b' 42', 42)
])
def test_parser_content_length_value_success(data, expected):
    p = Parser(data)
    result = p.content_length_value()

    assert result == expected


def test_parser_content_length_value_fail():
    p = Parser(b'abcdef')

    with pytest.raises(ParseError):
        p.content_length_value()


@pytest.mark.parametrize('data,expected', [
    (b'ham', MessageClassOption.ham),
    (b' ham ', MessageClassOption.ham),
    (b'spam', MessageClassOption.spam),
    (b' spam ', MessageClassOption.spam)
])
def test_parser_message_class_value_success(data, expected):
    p = Parser(data)
    result = p.message_class_value()

    assert result == expected


def test_parser_message_class_value_fail():
    p = Parser(b'invalid')

    with pytest.raises(ParseError):
        p.message_class_value()


@pytest.mark.parametrize('data,expected', [
    (b'local', ActionOption(local=True, remote=False)),
    (b'remote', ActionOption(local=False, remote=True)),
    (b'local, remote', ActionOption(local=True, remote=True)),
    (b'remote, local', ActionOption(local=True, remote=True)),
])
def test_parser_set_remove_value_success(data, expected):
    p = Parser(data)
    result = p.set_remove_value()

    assert isinstance(result, ActionOption)
    assert result == expected


def test_parser_set_remove_value_fail():
    p = Parser(b'invalid')

    with pytest.raises(ParseError):
        p.set_remove_value()


@pytest.mark.parametrize('data,value,score,threshold', [
    (b'True ; -4 / -2', True, -4.0, -2.0),
    (b'True ; 4 / 2', True, 4.0, 2.0),
    (b'False ; 4 / 2', False, 4.0, 2.0),
    (b'True ; 4.0 / 2.0', True, 4.0, 2.0)
])
def test_parser_spam_value_success(data, value, score, threshold):
    p = Parser(data)
    result = p.spam_value()

    assert result['value'] is value
    assert result['score'] == pytest.approx(score)
    assert result['threshold'] == pytest.approx(threshold)


def test_parser_spam_value_fail():
    p = Parser(b'invalid')

    with pytest.raises(ParseError):
        p.spam_value()


def test_parser_user_value_success():
    p = Parser(b' user-name_123 ')

    assert p.user_value() == "user-name_123"


@pytest.mark.parametrize('data,expected', [
    (b'Compress : zlib\r\n', Compress),
    (b'Content-length : 42\r\n', ContentLength),
    (b'Message-class : ham\r\n', MessageClass),
    (b'DidRemove : local\r\n', DidRemove),
    (b'DidSet : remote\r\n', DidSet),
    (b'Remove : local, remote\r\n', Remove),
    (b'Set : remote, local\r\n', Set),
    (b'Spam : True ; 4.0 / 2.0\r\n', Spam),
    (b'User : user_name-123\r\n', User),
    (b'CustomHeader : value\r\n', XHeader)
])
def test_parser_header(data, expected):
    p = Parser(data)
    result = p.header()

    assert isinstance(result, expected)


def test_parser_headers():
    p = Parser(b'Content-length : 42\r\nUser : username\r\nCustom : header\r\nInvalidHeader\r\n')

    result = p.headers()
    expected = (ContentLength, User, XHeader)

    for parsed_header, expected_header in zip(result, expected):
        assert isinstance(parsed_header, expected_header)


def test_parser_spamc_protocol():
    p = Parser(b'SPAMC')

    assert p.spamc_protocol() == "SPAMC"


@pytest.mark.parametrize('data,expected', [
    (b'CHECK ', 'CHECK'),
    (b'HEADERS ', 'HEADERS'),
    (b'PING ', 'PING'),
    (b'PROCESS ', 'PROCESS'),
    (b'REPORT ', 'REPORT'),
    (b'REPORT_IFSPAM ', 'REPORT_IFSPAM'),
    (b'SKIP ', 'SKIP'),
    (b'SYMBOLS ', 'SYMBOLS'),
    (b'TELL ', 'TELL'),
])
def test_parser_method(data, expected):
    p = Parser(data)

    assert p.method() == expected


@pytest.mark.parametrize('data', [
    b'CHECK SPAMC/1.5\r\nContent-length : 42\r\n\r\nA body',
    b'CHECK SPAMC/1.5\r\nContent-length : 42\r\n\r\n',
    b'PING SPAMC/1.5\r\n'
])
def test_parser_request(data):
    p = Parser(data)

    assert isinstance(p.request(), Request)


def test_parser_spamd_protocol():
    p = Parser(b'SPAMD')

    assert p.spamd_protocol() == 'SPAMD'


@pytest.mark.parametrize('data,expected', [
    (b'0', Status.EX_OK),
    (b'64', Status.EX_USAGE),
    (b'65', Status.EX_DATAERR),
    (b'66', Status.EX_NOINPUT),
    (b'67', Status.EX_NOUSER),
    (b'68', Status.EX_NOHOST),
    (b'69', Status.EX_UNAVAILABLE),
    (b'70', Status.EX_SOFTWARE),
    (b'71', Status.EX_OSERR),
    (b'72', Status.EX_OSFILE),
    (b'73', Status.EX_CANTCREAT),
    (b'74', Status.EX_IOERR),
    (b'75', Status.EX_TEMPFAIL),
    (b'76', Status.EX_PROTOCOL),
    (b'77', Status.EX_NOPERM),
    (b'78', Status.EX_CONFIG),
    (b'79', Status.EX_TIMEOUT),
    (b'999', 999),
])
def test_parser_status_code(data, expected):
    p = Parser(data)

    assert p.status_code() == expected


def test_parser_message():
    p = Parser(b'This is a message\r\n')

    assert p.message() == 'This is a message'


@pytest.mark.parametrize('data', [
    b'SPAMD/1.5 0 EX_OK\r\nContent-length : 42\r\n\r\nA body',
    b'SPAMD/1.5 0 EX_OK\r\nContent-length : 42\r\n\r\n',
    b'SPAMD/1.5 0 PONG\r\n'
])
def test_parser_response(data):
    p = Parser(data)

    assert isinstance(p.response(), Response)


@pytest.mark.parametrize('data,expected', [
    (b'SPAMD/1.5 0 PONG\r\n', Response),
     (b'PING SPAMC/1.5\r\n', Request)
])
def test_parser_parse_success(data, expected):
    assert isinstance(parse(data), expected)


def test_parser_parse_fail():
    with pytest.raises(ParseError):
        parse(b'invalid')
