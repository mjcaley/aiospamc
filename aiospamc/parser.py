#!/usr/bin/env python3

'''Parser object for SPAMC/SPAMD requests and responses.'''


import re
from functools import wraps
from typing import Callable, Match, Optional, Mapping, Union, List

from .options import MessageClassOption, ActionOption
from .requests import Request
from .responses import Status, Response
from . import headers


class ParseError(Exception):
    '''An exception occurring when parsing.'''

    def __init__(self, index: int, message: str):
        '''ParseError constructor.

        :param index: Index in the stream the exception occurred.
        :param message: User readable message.
        '''
        self.index = index
        self.message = message


def checkpoint(func) -> Callable:
    '''A decorator to restore the index if an exception occurred.'''

    @wraps(func)
    def inner(self):
        check = self.index
        try:
            return func(self)
        except ParseError:
            self.index = check
            raise
    return inner


class Parser:
    '''Parser object for requests and responses.'''

    def __init__(self, string: bytes = None) -> None:
        '''Parser constructor.

        :param string: The byte string to parse.
        '''
        self.string = string or b''
        self.index = 0

    def advance(self, by: int) -> None:
        '''Advance the current index by number of bytes.

        :param by: Number of bytes in the stream to advance.
        '''

        self.index += by

    def current(self) -> bytes:
        '''The remainder of the string that hasn't been parsed.'''

        return self.string[self.index:]

    def end(self) -> bool:
        '''Whether the parser has parsed the entire string.'''

        return self.index >= len(self.string)

    def match(self, pattern: bytes) -> Optional[Match[bytes]]:
        '''Returns the regular expression matches string at the current index.

        :param pattern: Regular expression pattern.
        '''

        success = re.match(pattern, self.current())
        if success:
            return success
        else:
            return None

    def consume(self, pattern: bytes) -> Match[bytes]:
        '''If the pattern matches, advances the index the length of the match.
        Returns the regular expression match.

        :param pattern: Regular expression pattern.

        :raises ParseError:
        '''

        match = self.match(pattern)
        if match:
            self.advance(match.end())
            return match
        else:
            raise ParseError(index=self.index, message='Unable to consume match  with pattern {}'.format(pattern))

    @staticmethod
    def skip(func: Callable) -> None:
        '''Makes the parser function optional by ignore whether it raises a
        :class:`aiospamc.parser.ParseError` exception or not.

        :param func: Function to execute.
        '''

        try:
            func()
        except ParseError:
            pass

    def whitespace(self) -> None:
        '''Consumes spaces or tabs.'''

        self.consume(rb'[ \t]+')

    def newline(self) -> None:
        '''Consumes a newline sequence (carriage return and line feed).'''

        self.consume(rb'\r\n')

    def version(self) -> str:
        '''Consumes a version pattern.  For example, "1.5".'''

        return self.consume(rb'\d+\.\d+').group().decode()

    def body(self) -> bytes:
        '''Consumes the rest of the message and returns the contents.'''

        return self.current()

    # Header functions

    @checkpoint
    def compress_value(self) -> str:
        '''Consumes the Compression header value.'''

        self.skip(self.whitespace)
        algorithm = self.consume(rb'zlib').group()
        self.skip(self.whitespace)

        return algorithm.decode()

    @checkpoint
    def content_length_value(self) -> int:
        '''Consumes the Content-length header value.'''

        self.skip(self.whitespace)
        length = int(self.consume(rb'\d+').group())
        self.skip(self.whitespace)

        return length

    @checkpoint
    def message_class_value(self) -> MessageClassOption:
        '''Consumes the Message-class header value.'''

        self.skip(self.whitespace)
        m_class = MessageClassOption.ham if self.consume(
            rb'(ham|spam)').group() == b'ham' else MessageClassOption.spam
        self.skip(self.whitespace)

        return m_class

    @checkpoint
    def set_remove_value(self) -> ActionOption:
        '''Consumes the value for the DidRemove, DidSet, Remove and Set headers.'''

        self.skip(self.whitespace)
        action = self.consume(rb'(local|remote)([ \t]*,[ \t]*(local|remote))?').group()
        self.skip(self.whitespace)

        return ActionOption(local=b'local' in action, remote=b'remote' in action)

    @checkpoint
    def spam_value(self) -> Mapping[str, Union[bool, float]]:
        '''Consumes the Spam header value.'''

        number = rb'(-?\d+(\.\d+)?)'

        self.skip(self.whitespace)
        value = True if self.consume(rb'(True|False)').group() == b'True' else False
        self.skip(self.whitespace)
        self.consume(rb';')
        self.skip(self.whitespace)
        score = float(self.consume(number).group())
        self.skip(self.whitespace)
        self.consume(rb'/')
        self.skip(self.whitespace)
        threshold = float(self.consume(number).group())
        self.skip(self.whitespace)

        return {'value': value, 'score': score, 'threshold': threshold}

    @checkpoint
    def user_value(self) -> str:
        '''Consumes the User header value.'''

        self.skip(self.whitespace)
        username = self.consume(rb'[a-zA-Z0-9-_]+').group()
        self.skip(self.whitespace)

        return username.decode()

    @checkpoint
    def header(self) -> headers.Header:
        '''Consumes the string and returns an instance of
        :class:`aiospamc.headers.Header`.'''

        self.skip(self.whitespace)
        name = self.consume(rb'[a-zA-Z0-9_-]+').group()
        self.skip(self.whitespace)
        self.consume(rb':')
        if name == b'Compress':
            self.compress_value()
            return headers.Compress()
        elif name == b'Content-length':
            return headers.ContentLength(length=self.content_length_value())
        elif name == b'DidRemove':
            return headers.DidRemove(action=self.set_remove_value())
        elif name == b'DidSet':
            return headers.DidSet(action=self.set_remove_value())
        elif name == b'Message-class':
            return headers.MessageClass(value=self.message_class_value())
        elif name == b'Remove':
            return headers.Remove(action=self.set_remove_value())
        elif name == b'Set':
            return headers.Set(action=self.set_remove_value())
        elif name == b'Spam':
            return headers.Spam(**self.spam_value())
        elif name == b'User':
            return headers.User(name=self.user_value())
        else:
            return headers.XHeader(
                    name=name.decode(),
                    value=self.consume(rb'.+(?=\r\n)').group().decode()
            )

    def headers(self) -> List[headers.Header]:
        '''Consumes all headers.'''

        header_list = []
        while not self.match(rb'\r\n'):
            try:
                h = self.header()
                self.newline()
                header_list.append(h)
            except ParseError:
                break

        return header_list

    # Request functions

    def spamc_protocol(self) -> str:
        '''Consumes the string "SPAMC".'''

        return self.consume(rb'SPAMC').group().decode()

    @checkpoint
    def method(self) -> str:
        '''Consumes the method name in a request.'''

        name = self.consume(rb'CHECK|'
                            rb'HEADERS|'
                            rb'PING|'
                            rb'PROCESS|'
                            rb'REPORT_IFSPAM|'
                            rb'REPORT|'
                            rb'SKIP|'
                            rb'SYMBOLS|'
                            rb'TELL')
        self.whitespace()

        return name.group().decode()

    @checkpoint
    def request(self) -> Request:
        '''Consumes a SPAMC request.'''

        m = self.method()
        p = self.spamc_protocol()
        self.consume(rb'/')
        v = self.version()
        self.newline()

        if not self.end():
            h = self.headers()
        else:
            h = []

        if not self.end():
            self.newline()
            b = self.body()
        else:
            b = None

        return Request(verb=m, version=v, headers=h, body=b)

    # Response functions

    def spamd_protocol(self) -> str:
        '''Consumes the string "SPAMD".'''

        return self.consume(rb'SPAMD').group().decode()

    @checkpoint
    def status_code(self) -> Union[Status, int]:
        '''Consumes the status code.'''

        code = int(self.consume(rb'\d+').group())
        try:
            return Status(code)
        except ValueError:
            return code

    def message(self) -> str:
        '''Consumes a string until it matches a newline.'''

        return self.consume(rb'.*(?=\r\n)').group().decode()

    @checkpoint
    def response(self) -> Response:
        '''Consumes a SPAMD response.'''

        p = self.spamd_protocol()
        self.consume(rb'/')
        v = self.version()
        self.whitespace()
        c = self.status_code()
        self.whitespace()
        m = self.message()
        self.newline()

        if not self.end():
            h = self.headers()
        else:
            h = []

        if not self.end():
            self.newline()
            b = self.body()
        else:
            b = None

        return Response(version=v, status_code=c, message=m, headers=h,
                                           body=b)


def parse(string) -> Union[Request, Response]:
    '''Parses a request or response.'''

    parser = Parser(string)

    try:
        return parser.request()
    except ParseError:
        pass

    try:
        return parser.response()
    except ParseError:
        pass

    raise ParseError(0, 'Unable to parse request or response')
