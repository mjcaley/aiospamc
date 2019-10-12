#!/usr/bin/env python3

import pytest

from aiospamc.header_values import CompressValue, ContentLengthValue, GenericHeaderValue, MessageClassValue, \
    SetOrRemoveValue, SpamValue, UserValue
from aiospamc.incremental_parser import NotEnoughDataError, Parser, ParseError, States, TooMuchDataError, \
    parse_request_status, parse_response_status, parse_content_length_value, parse_message_class_value, \
    parse_set_remove_value, parse_spam_value, parse_generic_header_value, parse_header, parse_body, ResponseParser, \
    RequestParser
from aiospamc.options import MessageClassOption, ActionOption


@pytest.fixture
def delimiter():
    return b'\r\n'


def test_default_result(delimiter, mocker):
    p = Parser(delimiter=delimiter, status_parser=mocker.stub(), header_parser=mocker.stub(), body_parser=mocker.stub())

    assert p.result == {'headers': {}, 'body': b''}


def test_default_state(delimiter, mocker):
    p = Parser(delimiter=delimiter, status_parser=mocker.stub(), header_parser=mocker.stub(), body_parser=mocker.stub())

    assert p.state == States.Status


def test_status_transitions_to_header_state(delimiter, mocker):
    p = Parser(
        delimiter=delimiter,
        status_parser=mocker.Mock(return_value={'status': 'status success'}),
        header_parser=mocker.stub(),
        body_parser=mocker.stub()
    )
    p.buffer = b'left\r\nright'
    p.status()

    assert p.result['status'] == 'status success'
    assert p.state == States.Header


def test_status_raises_not_enough_data(delimiter, mocker):
    p = Parser(
        delimiter=delimiter,
        status_parser=mocker.stub(),
        header_parser=mocker.stub(),
        body_parser=mocker.stub()
    )

    with pytest.raises(NotEnoughDataError):
        p.status()


def test_header_writes_value(delimiter, mocker):
    p = Parser(
        delimiter=delimiter,
        status_parser=mocker.stub(),
        header_parser=mocker.Mock(return_value=('header key', 'header value')),
        body_parser=mocker.stub(),
        start=States.Header
    )
    p.buffer = b'header key: header value\r\n\r\nright'
    p.header()

    assert p.result['headers']['header key'] == 'header value'
    assert p.state == States.Header


def test_header_transitions_to_body_state(delimiter, mocker):
    p = Parser(
        delimiter=delimiter,
        status_parser=mocker.stub(),
        header_parser=mocker.stub(),
        body_parser=mocker.stub(),
        start=States.Header
    )
    p.buffer = b'\r\nright'
    p.header()

    assert p.state == States.Body


def test_header_raises_not_enough_data(delimiter, mocker):
    p = Parser(
        delimiter=delimiter,
        status_parser=mocker.stub(),
        header_parser=mocker.stub(),
        body_parser=mocker.stub(),
        start=States.Header
    )

    with pytest.raises(NotEnoughDataError):
        p.header()


def test_body_saves_value_and_transitions_to_done(delimiter, mocker):
    p = Parser(
        delimiter=delimiter,
        status_parser=mocker.stub(),
        header_parser=mocker.stub(),
        body_parser=mocker.Mock(return_value=b'body value'),
        start=States.Body
    )
    p.buffer = b'body value'
    p.result['headers']['Content-length'] = ContentLengthValue(length=len(p.buffer))
    p.body()

    assert p.result['body'] == b'body value'
    assert p.state == States.Done


def test_body_transitions_to_done_on_empty_body(delimiter, mocker):
    p = Parser(
        delimiter=delimiter,
        status_parser=mocker.stub(),
        header_parser=mocker.stub(),
        body_parser=mocker.Mock(return_value=b'body value'),
        start=States.Body
    )
    p.body()

    assert p.state == States.Done


def test_body_too_much_data_and_transitions_to_done(delimiter, mocker):
    p = Parser(
        delimiter=delimiter,
        status_parser=mocker.stub(),
        header_parser=mocker.stub(),
        body_parser=mocker.Mock(side_effect=TooMuchDataError),
        start=States.Body
    )
    p.buffer = b'body value'
    p.result['headers']['Content-length'] = ContentLengthValue(length=1)

    with pytest.raises(TooMuchDataError):
        p.body()
    assert p.state == States.Done


def test_parse(delimiter, mocker):
    p = Parser(
        delimiter=delimiter,
        status_parser=mocker.Mock(return_value={'status': 'status value'}),
        header_parser=mocker.Mock(return_value=('header key', 'header value')),
        body_parser=mocker.Mock(return_value=b'body value'),
    )
    result = p.parse(b'status line\r\nheader lines\r\nContent-length: 10\r\n\r\nbody value')

    assert result['status'] == 'status value'
    assert result['headers']['header key'] == 'header value'
    assert result['body'] == b'body value'
    assert p.state == States.Done


@pytest.mark.parametrize('verb', [
    'CHECK', 'HEADERS', 'PING', 'PROCESS', 'REPORT_IFSPAM', 'REPORT', 'SKIP', 'SYMBOLS', 'TELL'
])
def test_parse_request_status_success(verb):
    result = parse_request_status(b'%s SPAMC/1.5' % verb.encode('ascii'))

    assert result['verb'] == verb
    assert result['protocol'] == 'SPAMC'
    assert result['version'] == '1.5'


@pytest.mark.parametrize('test_input', [
    b'Unrecognizable format',
    b'NOTAVERB SPAMC/1.5',
    b'CHECK NOTAPROTOCOL/1.5'
])
def test_parse_request_status_raises_parseerror(test_input):
    with pytest.raises(ParseError):
        parse_request_status(test_input)


def test_parse_response_status_success():
    result = parse_response_status(b'SPAMD/1.5 0 EX_OK')

    assert result['protocol'] == 'SPAMD'
    assert result['version'] == '1.5'
    assert result['status_code'] == 0
    assert result['message'] == 'EX_OK'


@pytest.mark.parametrize('test_input', [
    b'Unrecognizable format',
    b'NOTAPROTOCOL/1.5 0 EX_OK',
    b'SPAMD/1.5 NOTACODE EX_OK'
])
def test_parse_response_status_raises_parseerror(test_input):
    with pytest.raises(ParseError):
        parse_response_status(test_input)


def test_parse_content_length_value_success():
    result = parse_content_length_value('42')

    assert result.length == 42


def test_parse_content_length_value_raises_parse_error():
    with pytest.raises(ParseError):
        parse_content_length_value('Invalid')


@pytest.mark.parametrize('test_input,expected', [
    ['ham', MessageClassOption.ham],
    ['spam', MessageClassOption.spam],
    [MessageClassOption.ham, MessageClassOption.ham],
    [MessageClassOption.spam, MessageClassOption.spam]
])
def test_parse_message_class_value_success(test_input, expected):
    result = parse_message_class_value(test_input)

    assert result.value == expected


def test_parse_message_class_value_raises_parseerror():
    with pytest.raises(ParseError):
        parse_message_class_value('invalid')


@pytest.mark.parametrize('test_input,local_expected,remote_expected', [
    ['local, remote', True, True],
    ['remote, local', True, True],
    ['local', True, False],
    ['remote', False, True],
    ['', False, False]
])
def test_parse_set_remove_value_success(test_input, local_expected, remote_expected):
    result = parse_set_remove_value(test_input)

    assert result.action.local == local_expected
    assert result.action.remote == remote_expected


@pytest.mark.parametrize('test_input,value,score,threshold', [
    ['True ; 40.0 / 20.0', True, 40.0, 20.0],
    ['True ; -40.0 / 20.0', True, -40.0, 20.0],
    ['False ; 40.0 / 20.0', False, 40.0, 20.0],
    ['true ; 40.0 / 20.0', True, 40.0, 20.0],
    ['false ; 40.0 / 20.0', False, 40.0, 20.0],
    ['Yes ; 40.0 / 20.0', True, 40.0, 20.0],
    ['No ; 40.0 / 20.0', False, 40.0, 20.0],
    ['yes ; 40.0 / 20.0', True, 40.0, 20.0],
    ['no ; 40.0 / 20.0', False, 40.0, 20.0],
    ['True;40/20', True, 40.0, 20.0],
])
def test_parse_spam_value_success(test_input, value, score, threshold):
    result = parse_spam_value(test_input)

    assert result.value == value
    assert pytest.approx(result.score, score)
    assert pytest.approx(result.threshold, threshold)


@pytest.mark.parametrize('test_input', [
    'Unrecognizable spam',
    'NOTAVALUE ; 40.0 / 20.0',
    'True ; NOTASCORE / 20.0',
    'True ; 40.0 / NOTATHRESHOLD',
])
def test_parse_spam_value_raises_parseerror(test_input):
    with pytest.raises(ParseError):
        parse_spam_value(test_input)


def test_parse_xheader_success():
    result = parse_generic_header_value('value')

    assert isinstance(result, GenericHeaderValue)
    assert result.value == 'value'


@pytest.mark.parametrize('test_input,header,value', [
    [b'Compress: zlib', 'Compress', CompressValue(algorithm='zlib')],
    [b'Content-length: 42', 'Content-length', ContentLengthValue(length=42)],
    [b'DidRemove: local, remote', 'DidRemove', SetOrRemoveValue(action=ActionOption(local=True, remote=True))],
    [b'DidSet: local, remote', 'DidSet', SetOrRemoveValue(action=ActionOption(local=True, remote=True))],
    [b'Message-class: spam', 'Message-class', MessageClassValue(value=MessageClassOption.spam)],
    [b'Remove: local, remote', 'Remove', SetOrRemoveValue(action=ActionOption(local=True, remote=True))],
    [b'Set: local, remote', 'Set', SetOrRemoveValue(action=ActionOption(local=True, remote=True))],
    [b'Spam: True ; 40 / 20', 'Spam', SpamValue(value=True, score=40, threshold=20)],
    [b'User: username', 'User', UserValue(name='username')],
    [b'XHeader: x value', 'XHeader', GenericHeaderValue('x value')]
])
def test_parse_header_success(test_input, header, value):
    result = parse_header(test_input)

    assert result[0] == header
    assert result[1] == value


def test_parse_body_success():
    test_input = b'Test body'
    result = parse_body(test_input, len(test_input))

    assert result == test_input


def test_parse_body_raises_not_enough_data():
    test_input = b'Test body'

    with pytest.raises(NotEnoughDataError):
        parse_body(test_input, len(test_input) + 1)


def test_parse_body_raises_too_much_data():
    test_input = b'Test body'

    with pytest.raises(TooMuchDataError):
        parse_body(test_input, len(test_input) - 1)


def test_response_parser():
    r = ResponseParser()

    assert r.delimiter == b'\r\n'
    assert r.status_parser == parse_response_status
    assert r.header_parser == parse_header
    assert r.body_parser == parse_body
    assert r.state == States.Status


def test_response_from_bytes(response_with_body):
    r = ResponseParser()
    result = r.parse(response_with_body)

    assert result is not None


def test_request_parser():
    r = RequestParser()

    assert r.delimiter == b'\r\n'
    assert r.status_parser == parse_request_status
    assert r.header_parser == parse_header
    assert r.body_parser == parse_body
    assert r.state == States.Status


def test_request_from_bytes(request_with_body):
    r = RequestParser()
    result = r.parse(request_with_body)

    assert result is not None
