#!/usr/bin/env python3

'''Parser combinators for the SPAMC/SPAMD protocol.'''

from collections import namedtuple
import re
import string

import aiospamc.headers
import aiospamc.options
import aiospamc.requests
import aiospamc.responses


class Success:
    '''Contains successful result and location for a parser.

    Attributes
    ----------
    value
        Result of a successful parse.
    remaining : :class:`aiospamc.parser.Stream`
        Remaining stream to parse.
    '''

    def __init__(self, value, remaining):
        '''Success object constructor.

        Parameters
        ----------
        value
            Result of a successful parse.
        remaining : :class:`aiospamc.parser.Stream`
            Remaining stream to parse.
        '''

        self.value = value
        self.remaining = remaining

    def __bool__(self):
        return True

    def __str__(self):
        return 'Found {}'.format(self.value)

    def __repr__(self):
        return '{}(value={}, remaining={})'.format(self.__class__.__name__,
                                                   repr(self.value),
                                                   repr(self.remaining))


class Failure:
    '''Contains error message and location the where the parser failed.

    Attributes
    ----------
    error : :obj:`str`
        Error message.
    remaining : :class:`aiospamc.parser.Stream`
        Remaining stream to parse.
    '''

    def __init__(self, error, remaining):
        '''Failure object constructor.

        Parameters
        ----------
        error : :obj:`str`
            Error message.
        remaining : :class:`aiospamc.parser.Stream`
            Remaining stream to parse.
        '''

        self.error = error
        self.remaining = remaining

    def __bool__(self):
        return False

    def __str__(self):
        return 'Failure: {}, index={}'.format(self.error, self.remaining.index)

    def __repr__(self):
        return '{}(error={}, remaining={})'.format(self.__class__.__name__,
                                                   repr(self.error),
                                                   repr(self.remaining))


Stream = namedtuple('Stream', ['stream', 'index'])
'''A namedtuple containing a reference to the stream being parsed and the index
to start.'''

#################################################
##                                             ##
## Parsers which work on other Parsers objects ##
##                                             ##
#################################################

class Parser:
    '''Parser base class.  Overloads operators for ease of writing parsers.

    The following lists the operator and the effect it has:

    +----------+------------------------------------+
    | Operator | Effect                             |
    +==========+====================================+
    | -A       | Matches A, but discards the result |
    +----------+------------------------------------+
    | ~A       | Optionally matches A               |
    +----------+------------------------------------+
    | A | B    | Logical OR                         |
    +----------+------------------------------------+
    | A >> B   | Sequence of A then B               |
    +----------+------------------------------------+
    | A ^ B    | Logical XOR                        |
    +----------+------------------------------------+
    '''

    def __call__(self, stream, index=0):
        raise NotImplementedError

    def __invert__(self):
        return Optional(self)

    def __neg__(self):
        return Discard(self)

    def __or__(self, other):
        return Or(self, other)

    def __rshift__(self, other):
        return Sequence(self, other)

    def __xor__(self, other):
        return Xor(self, other)


class Or(Parser):
    '''Matches the left or right parser.

    Attributes
    ----------
    left : :class:`aiospamc.parser.Parser`
    right : :class:`aiospamc.parser.Parser`
    '''

    def __init__(self, left, right):
        self.left, self.right = left, right

    def __call__(self, stream, index=0):
        left_result = self.left(stream, index)
        if left_result:
            return left_result
        right_result = self.right(stream, index)
        if right_result:
            return right_result

        return Failure(error='OR did not match',
                       remaining=(stream, index))


class Xor(Parser):
    '''Matches only either the left or right parser.

    Attributes
    ----------
    left : :class:`aiospamc.parser.Parser`
    right : :class:`aiospamc.parser.Parser`
    '''

    def __init__(self, left, right):
        self.left, self.right = left, right

    def __call__(self, stream, index=0):
        left_result = self.left(stream, index)
        right_result = self.right(stream, index)
        if left_result and not right_result:
            return left_result
        if right_result and not left_result:
            return right_result

        return Failure(error='XOR did not match',
                       remaining=Stream(stream, index))


class Sequence(Parser):
    '''Matches the left and then the right parser in sequence.

    Attributes
    ----------
    left : :class:`aiospamc.parser.Parser`
    right : :class:`aiospamc.parser.Parser`
    '''
    def __init__(self, left, right):
        self.left, self.right = left, right

    def __call__(self, stream, index=0):
        left_result = self.left(stream, index)
        if left_result:
            right_result = self.right(stream, left_result.remaining.index)
            if right_result:
                return Success(value=flatten([left_result.value, right_result.value]),
                               remaining=right_result.remaining)

        return Failure(error='Could not match sequence',
                       remaining=Stream(stream, index))


class Map(Parser):
    '''Applies the referenced function to the value returned from the parser.

    Attributes
    ----------
    parser : :class:`aiospamc.parser.Parser`
    func : callable
    '''

    def __init__(self, parser, func):
        self.parser = parser
        self.func = func

    def __call__(self, stream, index=0):
        result = self.parser(stream, index)
        if result:
            result.value = self.func(result.value)
            return result
        else:
            return Failure(error='Unable to map function',
                           remaining=Stream(stream, index))


def concat(container):
    '''Concatenates items within a collection into a string.'''

    if isinstance(container, (list, tuple)):
        return ''.join([concat(item) for item in container])
    else:
        return container


def flatten(container):
    '''Flattens nested lists into one list.'''

    def inner(value):
        for item in value:
            if isinstance(item, list):
                yield from inner(item)
            else:
                yield item

    return list(inner(container))


def remove_empty(container):
    '''Removes None and empty strings from the container.'''

    def empty(value):
        if value is None:
            return True
        elif value == '':
            return True
        elif str(value) in string.whitespace:
            return True
        else:
            return False

    return [item for item in container if not empty(item)]


class Optional(Parser):
    '''If the parser is found then the value is returned, if not then a :obj:`None`
    value is returned.

    Parameters
    ----------
    parser : :class:`aiospamc.parser.Parser`
    '''

    def __init__(self, parser):
        self.parser = parser

    def __call__(self, stream, index=0):
        result = self.parser(stream, index)
        if result:
            return result
        else:
            return Success(value=None,
                           remaining=Stream(stream, index))


class Replace(Parser):
    '''If parser returns a successful result then it's replaced with the value
    given.

    Parameters
    ----------
    parser : :class:`aiospamc.parser.Parser`
    replace
        Value to replace a successful result with.
    '''

    def __init__(self, parser, replace):
        self.parser = parser
        self.replace = replace

    def __call__(self, stream, index=0):
        result = self.parser(stream, index)
        if result:
            result.value = self.replace
            return result
        else:
            return Failure(error='Could not match and replace parser',
                           remaining=Stream(stream, index))


class Discard(Parser):
    '''Shortcut for :class:`Replace` which replaces with a :obj:`None` value.

    Parameters
    ----------
    parser : :class:`aiospamc.parser.Parser`
    '''

    def __init__(self, parser):
        self.parser = Replace(parser, None)

    def __call__(self, stream, index=0):
        return self.parser(stream, index)


class ZeroOrMore(Parser):
    '''Matches zero or more repetitions of the parser.

    Parameters
    ----------
    parser : :class:`aiospamc.parser.Parser`
    '''

    def __init__(self, parser):
        self.parser = parser

    def __call__(self, stream, index=0):
        result = Success(value=[], remaining=Stream(stream, index))

        while True:
            next_result = self.parser(result.remaining.stream,
                                      result.remaining.index)
            if next_result:
                result.value.append(next_result.value)
                result.remaining = next_result.remaining
            else:
                break

        return result


class OneOrMore(Parser):
    '''Matches one or more repetitions of the parser.

    Parameters
    ----------
    parser : :class:`aiospamc.parser.Parser`
    '''

    def __init__(self, parser):
        self.parser = parser

    def __call__(self, stream, index=0):
        result = Success(value=[], remaining=Stream(stream, index))

        first_result = self.parser(stream, index)
        if first_result:
            result.value.append(first_result.value)
            result.remaining = first_result.remaining

            while True:
                next_result = self.parser(result.remaining.stream,
                                          result.remaining.index)
                if next_result:
                    result.value.append(next_result.value)
                    result.remaining = next_result.remaining
                else:
                    break

        else:
            return Failure(error='First result wasn\'t found',
                           remaining=Stream(stream, index))

        return result


#################################################
##                                             ##
##         Parsers which work on data          ##
##                                             ##
#################################################

class Match(Parser):
    '''Matches a regular expression.  Returns the regular expression result as
    the value if successful.

    Parameters
    ----------
    match : :obj:`bytes`
        Regular expression to match.
    '''

    def __init__(self, match):
        self.match = re.compile(match)

    def __call__(self, stream, index=0):
        result = self.match.match(stream, index)
        if result:
            return Success(value=result,
                           remaining=Stream(stream, result.end()))
        else:
            return Failure(error='Could not match',
                           remaining=Stream(stream, index))


class Str(Parser):
    '''Matches a regular expression and casts it to a string.

    Parameters
    ----------
    match : :obj:`bytes`
        Regular expression to match.
    '''

    def __init__(self, match):
        self.match = re.compile(match)

    def __call__(self, stream, index=0):
        result = self.match.match(stream, index)
        if result:
            return Success(value=stream[result.start():result.end()].decode(),
                           remaining=Stream(stream, result.end()))
        else:
            return Failure(error='Could not match string',
                           remaining=Stream(stream, index))


class Digits(Parser):
    '''Matches a sequence of digits and returns a string.'''

    def __init__(self):
        self.match = Str(b'[0-9]+')

    def __call__(self, stream, index=0):
        return self.match(stream, index)


class Integer(Parser):
    '''Matches a sequence of digits and returns an integer.'''

    def __init__(self):
        self.match = Map(Digits(), int)

    def __call__(self, stream, index=0):
        return self.match(stream, index)


class Float(Parser):
    '''Matches a floating point number and returns a float.'''

    def __init__(self):
        self.match = Map(Map(Digits() >> Str(b'\.') >> Digits(), concat), float)

    def __call__(self, stream, index=0):
        return self.match(stream, index)


class Number(Parser):
    '''Matches either an integer or a float.'''

    def __init__(self):
        self.match = Float() | Integer()

    def __call__(self, stream, index=0):
        return self.match(stream, index)


class TrueValue(Parser):
    '''Matches the string "true" or "True" and returns the boolean value.'''

    def __init__(self):
        self.match = Str(b'True') | Str(b'true')

    def __call__(self, stream, index=0):
        result = self.match(stream, index)
        if result:
            return Success(value=True, remaining=result.remaining)
        else:
            return Failure(error='Could not match True value',
                           remaining=Stream(stream, index))


class FalseValue(Parser):
    '''Matches the string "false" or "False" and returns the boolean value.'''

    def __init__(self):
        self.match = Str(b'False') | Str(b'false')

    def __call__(self, stream, index=0):
        result = self.match(stream, index)
        if result:
            return Success(value=False, remaining=result.remaining)
        else:
            return Failure(error='Could not match False value',
                           remaining=Stream(stream, index))


class Boolean(Parser):
    '''Matches and returns a bool.'''

    def __init__(self):
        self.match = TrueValue() | FalseValue()

    def __call__(self, stream, index=0):
        return self.match(stream, index)


class Whitespace(Parser):
    '''Matches sequence of whitespace and returns regular expression result.'''

    def __init__(self):
        self.match = Match(br'[ \t\x0b\x0c]+')

    def __call__(self, stream, index=0):
        return self.match(stream, index)


class Newline(Parser):
    '''Matches newline sequence and returns regular expression result.'''

    def __init__(self):
        self.match = Match(br'\r\n')

    def __call__(self, stream, index=0):
        return self.match(stream, index)


class Header(Parser):
    '''Matches a header format, name and value separated by a colon and
    terminated by a newline.
    '''

    def __init__(self, name, value):
        match = name >> \
                -~Whitespace() >> \
                -Str(b':') >> \
                -~Whitespace() >> \
                value >> \
                -~Whitespace() >> \
                -Newline()
        self.match = Map(match, remove_empty)

    def __call__(self, stream, index=0):
        return self.match(stream, index)


class CompressHeader(Parser):
    '''Matches a :class:`aiospamc.headers.Compress` header and returns an
    instance if successful.
    '''

    def __init__(self):
        self.match = Header(Str(b'Compress'), Str(b'zlib'))

    def __call__(self, stream, index=0):
        result = self.match(stream, index)
        if result:
            return Success(value=aiospamc.headers.Compress(),
                           remaining=result.remaining)
        else:
            return Failure(error='Could not parse Compress header',
                           remaining=Stream(stream, index))


class ContentLengthHeader(Parser):
    '''Matches a :class:`aiospamc.headers.ContentLength` header and returns an
    instance if successful.
    '''

    def __init__(self):
        match = Header(Str(b'Content-length'), Integer())
        self.match = Map(match, remove_empty)

    def __call__(self, stream, index=0):
        result = self.match(stream, index)
        if result:
            return Success(
                    value=aiospamc.headers.ContentLength(length=result.value[1]),
                    remaining=result.remaining
            )
        else:
            return Failure(error='Could not parse Content-length header',
                           remaining=Stream(stream, index))


class MessageClassOption(Parser):
    '''Matches 'spam' or 'ham' and returns an instance of
    :class:`aiospamc.options.MessageClassOption`.
    '''

    def __init__(self):
        self.match = Str(b'ham|spam')

    def __call__(self, stream, index=0):
        result = self.match(stream, index)
        if result:
            return Success(value=aiospamc.options.MessageClassOption[result.value],
                           remaining=result.remaining)
        else:
            return Failure(error='Could not parse Message-class header value',
                           remaining=Stream(stream, index))


class MessageClassHeader(Parser):
    '''Matches a :class:`aiospamc.headers.MessageClass` header and returns an
    instance if successful.
    '''

    def __init__(self):
        self.match = Header(Str(b'Message-class'), MessageClassOption())

    def __call__(self, stream, index=0):
        result = self.match(stream, index)
        if result:
            return Success(value=aiospamc.headers.MessageClass(result.value[1]),
                           remaining=result.remaining)
        else:
            return Failure(error='Could not parse Message-class header',
                           remaining=Stream(stream, index))


class SetRemoveValue(Parser):
    '''Matches a value for the :class:`aiospamc.headers.DidRemove`,
    :class:`aiospamc.headers.DidSet`, :class:`aiospamc.headers.Remove`, or
    :class:`aiospamc.headers.Set`.
    '''

    def __init__(self):
        match = Str(b'local|remote') >> ~(
                -~Whitespace() >>
                -Match(b',') >>
                -~Whitespace() >>
                Str(b'local|remote')
        )
        self.match = Map(match, remove_empty)

    def __call__(self, stream, index=0):
        result = self.match(stream, index)
        if result:
            action_option = aiospamc.options.ActionOption(
                    'local' in result.value,
                    'remote' in result.value
            )
            return Success(value=action_option,
                           remaining=result.remaining)
        else:
            return Failure(error='Cannot parse SetRemove value',
                           remaining=Stream(stream, index))


class DidRemoveHeader(Parser):
    '''Matches a :class:`aiospamc.headers.DidRemove` header and returns an
    instance if successful.
    '''

    def __init__(self):
        match = Header(Str(b'DidRemove'), SetRemoveValue())
        self.match = Map(match, remove_empty)

    def __call__(self, stream, index=0):
        result = self.match(stream, index)
        if result:
            return Success(value=aiospamc.headers.DidRemove(result.value[1]),
                           remaining=result.remaining)
        else:
            return Failure(error='Cannot parse DidRemove header',
                           remaining=Stream(stream, index))


class DidSetHeader(Parser):
    '''Matches a :class:`aiospamc.headers.DidSet` header and returns an
    instance if successful.
    '''

    def __init__(self):
        match = Header(Str(b'DidSet'), SetRemoveValue())
        self.match = Map(match, remove_empty)

    def __call__(self, stream, index=0):
        result = self.match(stream, index)
        if result:
            return Success(value=aiospamc.headers.DidSet(result.value[1]),
                           remaining=result.remaining)
        else:
            return Failure(error='Cannot parse DidRemove header',
                           remaining=Stream(stream, index))


class RemoveHeader(Parser):
    '''Matches a :class:`aiospamc.headers.Remove` header and returns an
    instance if successful.
    '''

    def __init__(self):
        match = Header(Str(b'Remove'), SetRemoveValue())
        self.match = Map(match, remove_empty)

    def __call__(self, stream, index=0):
        result = self.match(stream, index)
        if result:
            return Success(value=aiospamc.headers.Remove(result.value[1]),
                           remaining=result.remaining)
        else:
            return Failure(error='Cannot parse DidRemove header',
                           remaining=Stream(stream, index))


class SetHeader(Parser):
    '''Matches a :class:`aiospamc.headers.Set` header and returns an
    instance if successful.
    '''

    def __init__(self):
        match = Header(Str(b'Set'), SetRemoveValue())
        self.match = Map(match, remove_empty)

    def __call__(self, stream, index=0):
        result = self.match(stream, index)
        if result:
            return Success(value=aiospamc.headers.Set(result.value[1]),
                           remaining=result.remaining)
        else:
            return Failure(error='Cannot parse DidRemove header',
                           remaining=Stream(stream, index))


class SpamHeader(Parser):
    '''Matches a :class:`aiospamc.headers.Spam` header and returns an
    instance if successful.
    '''

    def __init__(self):
        match = Header(Str(b'Spam'),

                       Boolean() >>
                       -~Whitespace() >>
                       -Str(b';') >>
                       -~Whitespace() >>
                       Number() >>
                       -~Whitespace() >>
                       -Str(b'/') >>
                       -~Whitespace() >>
                       Number())
        self.match = Map(match, remove_empty)

    def __call__(self, stream, index=0):
        result = self.match(stream, index)
        if result:
            return Success(value=aiospamc.headers.Spam(value=result.value[1],
                                                       score=result.value[2],
                                                       threshold=result.value[3]),
                           remaining=result.remaining)
        else:
            return Failure(error='Could not parse Spam header',
                           remaining=Stream(stream, index))


class UserHeader(Parser):
    '''Matches a :class:`aiospamc.headers.User` header and returns an
    instance if successful.
    '''

    def __init__(self):
        self.match = Header(Str(b'User'), Str(b'[a-zA-Z0-9_-]+'))

    def __call__(self, stream, index=0):
        result = self.match(stream, index)
        if result:
            return Success(value=aiospamc.headers.User(result.value[1]),
                           remaining=result.remaining)
        else:
            return Failure(error='Could not parse User header',
                           remaining=Stream(stream, index))


class CustomHeader(Parser):
    '''Matches a custom header and returns an instance of
    :class:`aiospamc.headers.XHeader` if successful.
    '''

    def __init__(self):
        self.match = Header(Str(br'[^\s:]+'), Str(br'[^\r\n]+'))

    def __call__(self, stream, index=0):
        result = self.match(stream, index)
        if result:
            return Success(value=aiospamc.headers.XHeader(result.value[0], result.value[1]),
                           remaining=result.remaining)
        else:
            return Failure(error='Could not parse custom header',
                           remaining=Stream(stream, index))


class Headers(Parser):
    '''Matches headers and returns an instance if successful.'''

    def __init__(self):
        self.match = CompressHeader() | \
                     ContentLengthHeader() | \
                     MessageClassHeader() | \
                     DidRemoveHeader() | \
                     DidSetHeader() | \
                     RemoveHeader() | \
                     SetHeader() | \
                     SpamHeader() | \
                     UserHeader() | \
                     CustomHeader()

    def __call__(self, stream, index=0):
        return self.match(stream, index)


class Body(Parser):
    '''Matches the remaining stream as the body of the request/response.'''

    def __call__(self, stream, index=0):
        return Success(value=stream[index:],
                       remaining=Stream(stream, len(stream)))


class Version(Parser):
    '''Matches a version code and returns a string.'''

    def __init__(self):
        self.match = Str(b'\d+\.\d+')

    def __call__(self, stream, index=0):
        return self.match(stream, index)


class RequestMethod(Parser):
    '''Matches a request method.'''

    def __init__(self):
        self.match = Str(b'CHECK')         | \
                     Str(b'HEADERS')       | \
                     Str(b'PING')          | \
                     Str(b'PROCESS')       | \
                     Str(b'REPORT_IFSPAM') | \
                     Str(b'REPORT')        | \
                     Str(b'SKIP')          | \
                     Str(b'SYMBOLS')       | \
                     Str(b'TELL')

    def __call__(self, stream, index=0):
        return self.match(stream, index)


class Request(Parser):
    '''Matches a SPAMC request and returns an instance of
    :class:`aiospamc.requests.Request`.
    '''

    def __init__(self):
        match = RequestMethod() >> -~Whitespace() >> \
                Str(b'SPAMC') >> -Match(b'/') >> \
                Version() >> -Newline() >> \
                ZeroOrMore(Headers()) >> -Newline() >> \
                Body()
        self.match = Map(match, remove_empty)

    def __call__(self, stream, index=0):
        result = self.match(stream, index)
        if result:
            method, _, version, *headers, body = result.value
            return Success(
                    value=aiospamc.requests.Request(
                            verb=method,
                            version=version,
                            headers=headers,
                            body=body
                    ),
                    remaining=result.remaining
            )
        else:
            return Failure(error='Could not parse Request',
                           remaining=Stream(stream, index))


class Response(Parser):
    '''Matches a SPAMD response and returns an instance of
    :class:`aiospamc.responses.Response`.
    '''

    def __init__(self):
        status_line = Str(b'SPAMD') >> -~Whitespace() >> \
            -Match(b'/') >> Version() >> \
            -~Whitespace() >> \
            Integer() >> -~Whitespace() >> \
            Str(b'[^\r\n]+') >> -~Whitespace() >> \
            -Newline()
        self.status_line = Map(status_line, remove_empty)
        headers_body = ZeroOrMore(Headers()) >> -Newline() >> Body()
        self.headers_body = Map(headers_body, remove_empty)

    def __call__(self, stream, index=0):
        status_result = self.status_line(stream, index)
        header_body_result = self.headers_body(*status_result.remaining)

        if status_result:
            _, version, status_code, message = status_result.value

            if header_body_result:
                *headers, body = header_body_result.value

                return Success(
                    value=aiospamc.responses.Response(
                            version=version,
                            status_code=aiospamc.responses.Status(status_code),
                            message=message,
                            headers=headers,
                            body=body
                    ),
                    remaining=header_body_result.remaining)
            else:
                return Success(
                        value=aiospamc.responses.Response(
                                version=version,
                                status_code=aiospamc.responses.Status(status_code),
                                message=message
                        ),
                        remaining=status_result.remaining
                )
        else:
            return Failure(error='Could not parse Response',
                           remaining=Stream(stream, index))


class SAParser(Parser):
    '''Start rule for the parser.  Returns an instance of either
    :class:`aiospamc.requests.Request` or :class:`aiospamc.responses.Response`.
    '''

    def __init__(self):
        self.match = Response() | Request()

    def __call__(self, stream, index=0):
        return self.match(stream, index)
