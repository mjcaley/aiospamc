#!/usr/bin/env python3

from enum import Enum
import re
from typing import Any, Callable, Mapping, Tuple, Union, Dict

from aiospamc.options import ActionOption, MessageClassOption


class NotEnoughDataError(Exception):
    pass


class TooMuchDataError(Exception):
    pass


class ParseError(Exception):
    def __init__(self, message) -> None:
        self.message = message


class States(Enum):
    Status = 1
    Header = 2
    Body = 3
    Done = 4


class Parser:
    def __init__(self,
                 delimiter: bytes,
                 status_parser: Callable[[bytes], Mapping[str, str]],
                 header_parser: Callable[[bytes], Tuple[str, Any]],
                 body_parser: Callable[[bytes, int], bytes],
                 start: States = States.Status) -> None:
        self.delimiter = delimiter
        self.status_parser = status_parser
        self.header_parser = header_parser
        self.body_parser = body_parser
        self.result = {'status': {}, 'headers': {}, 'body': b''}

        self._state = start
        self.buffer = b''

        self._state_table = {
            States.Status: self.status,
            States.Header: self.header,
            States.Body: self.body
        }

    @property
    def state(self) -> States:
        return self._state

    def parse(self, stream: bytes) -> Mapping[str, Any]:
        self.buffer += stream

        while self._state != States.Done:
            if self._state == States.Status:
                self.status()
            if self._state == States.Header:
                self.header()
            if self._state == States.Body:
                self.body()

        return self.result

    def status(self) -> None:
        status_line, delimiter, leftover = self.buffer.partition(self.delimiter)

        if status_line and delimiter:
            self.buffer = leftover
            self.result['status'] = self.status_parser(status_line)
            self._state = States.Header
        else:
            raise NotEnoughDataError

    def header(self) -> None:
        header_line, delimiter, leftover = self.buffer.partition(self.delimiter)

        if not header_line and delimiter:
            self.buffer = leftover
            self._state = States.Body
        elif header_line and delimiter:
            self.buffer = leftover
            key, value = self.header_parser(header_line)
            self.result['headers'][key] = value
        else:
            raise NotEnoughDataError

    def body(self) -> None:
        content_length = self.result['headers'].get('Content-length', {'length': 0})['length']
        try:
            self.result['body'] += self.body_parser(self.buffer, content_length)
            self._state = States.Done
        except TooMuchDataError:
            self._state = States.Done
            raise


def parse_request_status(stream: bytes) -> Dict[str, str]:
    try:
        verb, protocol_version = stream.decode('ascii').split(' ')
        protocol, version = protocol_version.split('/')
    except ValueError:
        raise ParseError('Could not parse request status line, not in recognizable format')

    if verb not in ['CHECK', 'HEADERS', 'PING', 'PROCESS', 'REPORT_IFSPAM', 'REPORT', 'SKIP', 'SYMBOLS', 'TELL']:
        raise ParseError('Not a valid verb')

    if protocol != 'SPAMC':
        raise ParseError('Protocol name does not match')

    return {'verb': verb, 'protocol': protocol, 'version': version}


def parse_response_status(stream: bytes) -> Dict[str, str]:
    try:
        protocol_version, status_code, message = list(filter(None, stream.decode('ascii').split(' ')))
        protocol, version = protocol_version.split('/')
    except ValueError:
        raise ParseError('Could not parse response status line, not in recognizable format')

    if protocol != 'SPAMD':
        raise ParseError('Protocol name does not match')

    try:
        status_code = int(status_code)
    except ValueError:
        raise ParseError('Protocol status code is not an integer')

    return {
        'protocol': protocol,
        'version': version,
        'status_code': status_code,
        'message': message
    }


def parse_message_class_value(stream: str) -> Dict[str, MessageClassOption]:
    stream = stream.strip()

    if stream == 'ham':
        return {'value': MessageClassOption.ham}
    elif stream == 'spam':
        return {'value': MessageClassOption.spam}
    else:
        raise ParseError('Unable to parse Message-class header value')


def parse_content_length_value(stream: Union[str, int]) -> Dict[str, int]:
    try:
        value = int(stream)
    except ValueError:
        raise ParseError('Unable to parse Content-length value, must be integer')

    return {'length': value}


def parse_compress_value(stream: str) -> Dict[str, str]:
    return {'algorithm': stream.strip()}


def parse_set_remove_value(stream: str) -> ActionOption:
    stream = stream.replace(' ', '')
    values = stream.split(',')

    if 'local' in values:
        local = True
    else:
        local = False

    if 'remote' in values:
        remote = True
    else:
        remote = False

    return {'action': ActionOption(local=local, remote=remote)}


def parse_spam_value(stream: str) -> Dict[str, Union[bool, float]]:
    stream = stream.replace(' ', '')
    try:
        found, score, threshold = re.split('[;/]', stream)
    except ValueError:
        raise ParseError('Spam header in unrecognizable format')

    found = found.lower()
    if found in ['true', 'yes']:
        value = True
    elif found in ['false', 'no']:
        value = False
    else:
        raise ParseError('Spam header is not a true or false value')

    try:
        score = float(score)
    except ValueError:
        raise ParseError('Cannot parse Spam header score value')

    try:
        threshold = float(threshold)
    except ValueError:
        raise ParseError('Cannot parse Spam header threshold value')

    return {'value': value, 'score': score, 'threshold': threshold}


def parse_user_value(stream: str) -> Dict[str, str]:
    return {'name': stream.strip()}


def parse_xheader_value(stream: bytes) -> Dict[str, bytes]:
    return {'value': stream.strip()}


def parse_header(stream: bytes) -> Tuple[str, Any]:
    header, _, value = stream.partition(b':')
    header = header.decode('ascii').strip()
    if header in header_value_parsers:
        value = header_value_parsers[header](value.decode('ascii'))
    else:
        value = parse_xheader_value(value)

    return header, value


def parse_body(stream: bytes, content_length: int) -> bytes:
    if len(stream) == content_length:
        return stream
    elif len(stream) < content_length:
        raise NotEnoughDataError
    else:
        raise TooMuchDataError


header_value_parsers = {
    'Compress': parse_compress_value,
    'Content-length': parse_content_length_value,
    'DidRemove': parse_set_remove_value,
    'DidSet': parse_set_remove_value,
    'Message-class': parse_message_class_value,
    'Remove': parse_set_remove_value,
    'Set': parse_set_remove_value,
    'Spam': parse_spam_value,
    'User': parse_user_value
}


def get_header_value_parser(header: str) -> Callable:
    return header_value_parsers.get(header, parse_xheader_value)


class RequestParser(Parser):
    def __init__(self):
        super().__init__(
            delimiter=b'\r\n',
            status_parser=parse_request_status,
            header_parser=parse_header,
            body_parser=parse_body
        )


class ResponseParser(Parser):
    def __init__(self):
        super().__init__(
            delimiter=b'\r\n',
            status_parser=parse_response_status,
            header_parser=parse_header,
            body_parser=parse_body
        )
