#!/usr/bin/env python3

'''Module for the parsing functions and objects.'''

from enum import Enum
import re
from typing import Any, Callable, Mapping, Tuple, Union, Dict

from .header_values import CompressValue, ContentLengthValue, GenericHeaderValue, HeaderValue, MessageClassValue, \
    SetOrRemoveValue, SpamValue, UserValue
from .options import ActionOption, MessageClassOption


class ParseError(Exception):
    '''Error occurred while parsing.'''

    def __init__(self, message=None) -> None:
        '''Construct parsing exception with optional message.

        :param message: User friendly message.
        '''

        self.message = message


class NotEnoughDataError(ParseError):
    '''Expected more data than what the protocol content specified.'''

    pass


class TooMuchDataError(ParseError):
    '''Too much data was received than what the protocol content specified.'''
    pass


class States(Enum):
    '''States for the parser state machine.'''

    Status = 1
    Header = 2
    Body = 3
    Done = 4


class Parser:
    '''The parser state machine.

    :ivar result: Storage location for parsing results.'''

    def __init__(self,
                 delimiter: bytes,
                 status_parser: Callable[[bytes], Mapping[str, str]],
                 header_parser: Callable[[bytes], Tuple[str, Any]],
                 body_parser: Callable[[bytes, int], bytes],
                 start: States = States.Status) -> None:
        '''Parser constructor.

        :param delimiter: Byte string to split the different sections of the message.
        :param status_parser: Callable to parse the status line of the message.
        :param header_parser: Callable to parse each header line of the message.
        :param body_parser: Callable to parse the body of the message.
        :param start: The state to start the parser on.  Allowed for easier testing.
        '''

        self.delimiter = delimiter
        self.status_parser = status_parser
        self.header_parser = header_parser
        self.body_parser = body_parser
        self.result = {'headers': {}, 'body': b''}

        self._state = start
        self.buffer = b''

        self._state_table = {
            States.Status: self.status,
            States.Header: self.header,
            States.Body: self.body
        }

    @property
    def state(self) -> States:
        '''The current state of the parser.

        :return: The :class:`States` instance.
        '''

        return self._state

    def parse(self, stream: bytes) -> Mapping[str, Any]:
        '''Entry method to parse a message.

        :param stream: Byte string to parse.

        :return: Returns the parser results dictionary stored in the class attribute :attr:`result`.

        :raises NotEnoughDataError: Raised when not enough data is sent to be parsed.
        :raises TooMuchDataError: Raised when too much data is sent to be parsed.
        :raises ParseError: Raised when a general parse error is found.
        '''

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
        '''Splits the message at the delimiter and sends the first part of the message to the `status_line` callable to
        be parsed.  If successful then the results are stored in the :attr:`result` class attribute and the state
        transitions to :class:`States.Header`.

        :raises NotEnoughDataError: When there is no delimiter the message is incomplete.
        :raises ParseError: When the `status_line` callable experiences an error.
        '''

        status_line, delimiter, leftover = self.buffer.partition(self.delimiter)

        if status_line and delimiter:
            self.buffer = leftover
            self.result = {**self.result, **self.status_parser(status_line)}
            self._state = States.Header
        else:
            raise NotEnoughDataError

    def header(self) -> None:
        '''Splits the message at the delimiter and sends the line to the `header_parser`.

        When splitting the action will be determined depending what is matched:

        +-------------+-----------+-----------+----------------------------------------------------------------------+
        | Header line | Delimiter | Leftover  | Action                                                               |
        +=============+===========+===========+======================================================================+
        |     No      |    Yes    | Delimiter | Headers done, empty body. Clear buffer and transition to             |
        |             |           |           | :class:`States.Body`.                                                |
        +-------------+-----------+-----------+----------------------------------------------------------------------+
        |     No      |    Yes    |    N/A    | Headers done.  Transition to :class:`States.Body`.                   |
        +-------------+-----------+-----------+----------------------------------------------------------------------+
        |     Yes     |    Yes    |    N/A    | Parse header.  Record in :attr:`result` class attribute.             |
        +-------------+-----------+-----------+----------------------------------------------------------------------+
        |     No      |    No     |    No     | Message was a status line only.  Transition to :class:`States.Body`. |
        +-------------+-----------+-----------+----------------------------------------------------------------------+

        :raises ParseError: None of the previous conditions are matched.
        '''

        header_line, delimiter, leftover = self.buffer.partition(self.delimiter)

        if not header_line and delimiter and leftover == self.delimiter:
            self.buffer = b''
            self._state = States.Body
        elif not header_line and delimiter:
            self.buffer = leftover
            self._state = States.Body
        elif header_line and delimiter:
            self.buffer = leftover
            key, value = self.header_parser(header_line)
            self.result['headers'][key] = value
        elif not header_line and not delimiter and not leftover:
            self._state = States.Body
        else:
            raise ParseError('Header section not in recognizable format')

    def body(self) -> None:
        '''Uses the length defined in the `Content-length` header (defaulted to 0) to determine how many bytes the body
        contains.

        :raises TooMuchDataError:
            When there are too many bytes in the buffer compared to the `Content-length` header value.  Transitions the
            state to :class:`States.Done`.
        '''

        content_length = self.result['headers'].get('Content-length', ContentLengthValue(length=0)).length
        try:
            self.result['body'] += self.body_parser(self.buffer, content_length)
            self._state = States.Done
        except TooMuchDataError:
            self._state = States.Done
            raise


def parse_request_status(stream: bytes) -> Dict[str, str]:
    '''Parses the status line from a request.

    :param stream: The byte stream to parse.

    :return: A dictionary with the keys `verb`, `protocol` and `version`.

    :raises ParseError:
        When the status line is in an invalid format, not a valid verb, or doesn't have the correct protocol.
    '''

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
    '''Parse the status line for a response.

    :param stream: The byte stream to parse.

    :return: A dictionary with the keys `protocol`, `version`, `status_code`, and `message`.

    :raises ParseError:
        When the status line is in an invalid format, status code is not an integer, or doesn't have the correct
        protocol.
    '''

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


def parse_message_class_value(stream: Union[str, MessageClassOption]) -> MessageClassValue:
    '''Parses the `Message-class` header value.

    :param stream: String or `MessageClassOption` instance.

    :return: A `MessageClassValue` instance representing the value.

    :raises ParseError: When the value doesn't match either `ham` or `spam`.
    '''

    try:
        stream = stream.name
    except AttributeError:
        pass

    stream = stream.strip()

    try:
        return MessageClassValue(value=getattr(MessageClassOption, stream))
    except AttributeError:
        raise ParseError('Unable to parse Message-class header value')


def parse_content_length_value(stream: Union[str, int]) -> ContentLengthValue:
    '''Parses the `Content-length` header value.

    :param stream: String or integer value of the header.

    :return: A `ContentLengthValue` instance.

    :raises ParseError: When the value cannot be cast to an integer.
    '''

    try:
        value = int(stream)
    except ValueError:
        raise ParseError('Unable to parse Content-length value, must be integer')

    return ContentLengthValue(length=value)


def parse_compress_value(stream: str) -> CompressValue:
    '''Parses a value for the `Compress` header.

    :param stream: String to parse.

    :return: A `CompressValue` instance.
    '''

    return CompressValue(algorithm=stream.strip())


def parse_set_remove_value(stream: Union[ActionOption, str]) -> SetOrRemoveValue:
    '''Parse a value for the `DidRemove`, `DidSet`, `Remove`, and `Set` headers.

    :param stream: String to parse or an instance of `ActionOption`.

    :return: A `SetOrRemoveValue` instance.
    '''

    if isinstance(stream, ActionOption):
        value = stream
    else:
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

        value = ActionOption(local=local, remote=remote)

    return SetOrRemoveValue(action=value)


def parse_spam_value(stream: str) -> SpamValue:
    '''Parses the values for the `Spam` header.

    :param stream: String to parse.

    :return: An `SpamValue` instance.

    :raises ParseError: Raised if there is no true/false value, or valid numbers for the score or threshold.
    '''

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

    return SpamValue(value=value, score=score, threshold=threshold)


def parse_user_value(stream: str) -> UserValue:
    return UserValue(name=stream.strip())


def parse_generic_header_value(stream: str) -> GenericHeaderValue:
    '''Parses any user-defined or currently unknown header values.

    :param stream: String to parse.

    :return: A `GenericHeaderValue` instance.
    '''

    return GenericHeaderValue(value=stream.strip())


def parse_header_value(header: str, value: Union[str, bytes]) -> HeaderValue:
    '''Sends the header value stream to the header value parsing function.

    :param header: Name of the header.
    :param value: String or byte stream of the header value.

    :return: The `HeaderValue` instance from the parsing function.
    '''

    if header in header_value_parsers:
        if isinstance(value, bytes):
            value = value.decode('ascii')
        value = header_value_parsers[header](value)
    else:
        if isinstance(value, bytes):
            value = value.decode('utf8')
        value = parse_generic_header_value(value)

    return value


def parse_header(stream: bytes) -> Tuple[str, HeaderValue]:
    '''Splits the header line and sends to the header parsing function.

    :param stream: Byte stream of the header line.

    :return: A tuple of the header name and value.
    '''

    header, _, value = stream.partition(b':')
    header = header.decode('ascii').strip()
    value = parse_header_value(header, value)

    return header, value


def parse_body(stream: bytes, content_length: int) -> bytes:
    '''Parses the body of a message.

    :param stream: Byte stream for the body.
    :param content_length: Expected length of the body in bytes.

    :return: Byte stream of the body.

    :raises NotEnoughDataError: If the length is less than the stream.
    :raises TooMuchDataError: If the length is more than the stream.
    '''

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
'''Mapping for header names to their parsing functions.'''


class RequestParser(Parser):
    '''Sub-class of the parser for requests.'''

    def __init__(self):
        super().__init__(
            delimiter=b'\r\n',
            status_parser=parse_request_status,
            header_parser=parse_header,
            body_parser=parse_body
        )


class ResponseParser(Parser):
    '''Sub-class of the parser for responses.'''

    def __init__(self):
        super().__init__(
            delimiter=b'\r\n',
            status_parser=parse_response_status,
            header_parser=parse_header,
            body_parser=parse_body
        )
