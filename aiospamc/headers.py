#!/usr/bin/env python3

'''Collection of request and response headers.'''

import getpass
import re

from aiospamc.exceptions import HeaderCantParse
from aiospamc.transport import Inbound, Outbound
from aiospamc.options import Action, MessageClassOption


class Header(Inbound, Outbound):
    '''Header base class.'''

    def __str__(self):
        return self.compose()

    def header_field_name(self):
        '''Returns the the field name for the header.

        Returns
        -------
        str
        '''

        raise NotImplementedError

class Compress(Header):
    '''Compress header.  Specifies what encryption scheme to use.  So far only
    'zlib' is supported.
    '''

    _pattern = re.compile(r'\s*zlib\s*')
    '''Regular expression pattern to match 'zlib'.'''

    @classmethod
    def parse(cls, string):
        match = cls._pattern.match(string)
        if match:
            obj = cls()
            return obj
        else:
            raise HeaderCantParse({'message': 'Unable to parse string',
                                   'string': string,
                                   'pattern': cls._pattern.pattern})

    def __init__(self):
        self.zlib = True

    def __repr__(self):
        return '{}()'.format(self.__class__.__name__)

    def compose(self):
        return '{}: zlib\r\n'.format(self.header_field_name())

    def header_field_name(self):
        return 'Compress'

class ContentLength(Header):
    '''ContentLength header.  Indicates the length of the body in bytes.'''

    _pattern = re.compile(r'\s*\d+\s*')
    '''Regular expression pattern to match one or more digits.'''

    @classmethod
    def parse(cls, string):
        match = cls._pattern.match(string)
        if match:
            obj = cls(int(match.group()))
            return obj
        else:
            raise HeaderCantParse({'message': 'Unable to parse string',
                                   'string': string,
                                   'pattern': cls._pattern.pattern})

    def __init__(self, length=0):
        self.length = length

    def __repr__(self):
        return '{}(length={})'.format(self.__class__.__name__, self.length)

    def compose(self):
        return '{}: {}\r\n'.format(self.header_field_name(), self.length)

    def header_field_name(self):
        return 'Content-length'

class XHeader(Header):
    '''Extension header.  Used to specify a header that's not supported
    natively by the SPAMD service.
    '''

    _pattern = re.compile(r'\s*(?P<name>\S+)\s*:\s*(?P<value>\S+)\s*')
    '''Regular expresison pattern to match entire contents of a header
    string.
    '''

    @classmethod
    def parse(cls, string):
        match = cls._pattern.match(string)
        if match:
            obj = cls(match.groupdict()['name'], match.groupdict()['value'])
            return obj
        else:
            raise HeaderCantParse({'message': 'Unable to parse string',
                                   'string': string,
                                   'pattern': cls._pattern.pattern})

    def __init__(self, name, value):
        '''XHeader constructor.

        Parameters
        ----------
        name : str
            Name of the header.
        value : str
            Contents of the value.
        '''

        self.name = name
        self.value = value

    def __repr__(self):
        return '{}(name=\'{}\', value=\'{}\')'.format(self.__class__.__name__,
                                                      self.name,
                                                      self.value)

    def compose(self):
        return '{}: {}\r\n'.format(self.header_field_name(), self.value)

    def header_field_name(self):
        return self.name

class MessageClass(Header):
    '''MessageClass header.  Used to specify whether a message is 'spam' or
    'ham.\''''

    _pattern = re.compile(r'^\s*(?P<value>ham|spam)\s*$', flags=re.IGNORECASE)
    '''Regular expression pattern to match either 'spam' or 'ham.\''''

    @classmethod
    def parse(cls, string):
        match = cls._pattern.match(string)
        if match:
            obj = cls()
            obj.value = MessageClassOption[match.groupdict()['value']]
            return obj
        else:
            raise HeaderCantParse({'message': 'Unable to parse string',
                                   'string': string,
                                   'pattern': cls._pattern.pattern})

    def __init__(self, value=MessageClassOption.ham):
        self.value = value

    def __repr__(self):
        return '{}(value={})'.format(self.__class__.__name__, str(self.value))

    def compose(self):
        return '{}: {}\r\n'.format(self.header_field_name(), self.value.name)

    def header_field_name(self):
        return 'Message-class'

class _SetRemove(Header):
    '''Base class for headers that implement "local" and "remote" rules.'''

    _local_pattern = re.compile(r'.*local.*', flags=re.IGNORECASE)
    '''Regular expression string to match 'local.\''''
    _remote_pattern = re.compile(r'.*remote.*', flags=re.IGNORECASE)
    '''Regular expression string to match 'remote.\''''

    @classmethod
    def parse(cls, string):
        local_result = bool(cls._local_pattern.match(string))
        remote_result = bool(cls._remote_pattern.match(string))

        if not local_result and not remote_result:
            raise HeaderCantParse({'message': 'Unable to parse string',
                                   'string': string,
                                   'pattern': (cls._local_pattern.pattern,
                                               cls._remote_pattern.pattern)})
        else:
            obj = cls(Action(local_result, remote_result))

        return obj

    def __init__(self, action=Action(local=True, remote=False)):
        self.action = action

    def compose(self):
        if not self.action.local and not self.action.remote:
            # if nothing is set, then return a blank string so the request
            # doesn't get tainted
            return ''

        values = []
        if self.action.local:
            values.append('local')
        if self.action.remote:
            values.append('remote')

        return '{}: {}\r\n'.format(self.header_field_name(), ', '.join(values))

    def header_field_name(self):
        raise NotImplementedError

class DidRemove(_SetRemove):
    '''DidRemove header.  Used by SPAMD to indicate if a message was removed
    from either a local or remote database in response to a TELL request.
    '''

    def __repr__(self):
        return '{}(action=Action(local={}, remote={}))'.format(self.__class__.__name__,
                                                               self.action.local,
                                                               self.action.remote)

    def header_field_name(self):
        return 'DidRemove'

class DidSet(_SetRemove):
    '''DidRemove header.  Used by SPAMD to indicate if a message was added to
    either a local or remote database in response to a TELL request.
    '''

    def __repr__(self):
        return '{}(action=Action(local={}, remote={}))'.format(self.__class__.__name__,
                                                               self.action.local,
                                                               self.action.remote)

    def header_field_name(self):
        return 'DidSet'

class Remove(_SetRemove):
    '''Remove header.  Used in a TELL request to ask the SPAMD service remove
    a message from a local or remote database.  The SPAMD service must have the
    --allow-tells switch in order for this to do anything.
    '''

    def __repr__(self):
        return '{}(action=Action(local={}, remote={}))'.format(self.__class__.__name__,
                                                               self.action.local,
                                                               self.action.remote)

    def header_field_name(self):
        return 'Remove'

class Set(_SetRemove):
    '''Set header.  Used in a TELL request to ask the SPAMD service add a
    message from a local or remote database.  The SPAMD service must have the
    --allow-tells switch in order for this to do anything.
    '''

    def __repr__(self):
        return '{}(action=Action(local={}, remote={}))'.format(self.__class__.__name__,
                                                               self.action.local,
                                                               self.action.remote)

    def header_field_name(self):
        return 'Set'

class Spam(Header):
    '''Spam header.  Used by the SPAMD service to report on if the submitted
    message was spam and the score/threshold that it used.
    '''

    _pattern = re.compile(r'\s*'
                          r'(?P<value>true|yes|false|no)'
                          r'\s*;\s*'
                          r'(?P<score>\d+(\.\d+)?)'
                          r'\s*/\s*'
                          r'(?P<threshold>\d+(\.\d+)?)'
                          r'\s*', flags=re.IGNORECASE)
    '''Regular expression pattern to match the 'true' or 'false' result, the
    score, and the threshold of the submitted message.
    '''

    @classmethod
    def parse(cls, string):
        match = cls._pattern.match(string)
        if match:
            obj = cls()
            obj.value = match.groupdict()['value'].lower() in ['true', 'yes']
            obj.score = float(match.groupdict()['score'])
            obj.threshold = float(match.groupdict()['threshold'])

            return obj
        else:
            raise HeaderCantParse({'message': 'Unable to parse string',
                                   'string': string,
                                   'pattern': cls._pattern.pattern})

    def __init__(self, value=False, score=0.0, threshold=0.0):
        '''Spam header constructor.

        Parameters
        ----------
        value : bool
            True if the message is spam, False if not.
        score : float
            Score of the message after being scanned.
        threshold : float
            Threshold of which the message would have been marked as spam.
        '''

        self.value = value
        self.score = score
        self.threshold = threshold

    def __repr__(self):
        return '{}(value={}, score={}, threshold={})'.format(self.__class__.__name__,
                                                             self.value,
                                                             self.score,
                                                             self.threshold)

    def compose(self):
        return '{}: {} ; {} / {}\r\n'.format(self.header_field_name(),
                                             self.value,
                                             self.score,
                                             self.threshold)

    def header_field_name(self):
        return 'Spam'

class User(Header):
    '''User header.  Used to specify which user the SPAMD service should use
    when loading configuration files.
    '''

    _pattern = re.compile(r'^\s*(?P<user>[a-zA-Z0-9_-]+)\s*$')
    '''Regular expression pattern to match the username.'''

    @classmethod
    def parse(cls, string):
        match = cls._pattern.match(string)
        if match:
            obj = cls(match.groupdict()['user'])
            return obj
        else:
            raise HeaderCantParse({'message': 'Unable to parse string',
                                   'string': string,
                                   'pattern': cls._pattern.pattern})

    def __init__(self, name=getpass.getuser()):
        self.name = name

    def __repr__(self):
        return '{}(name=\'{}\')'.format(self.__class__.__name__, self.name)

    def compose(self):
        return '{}: {}\r\n'.format(self.header_field_name(), self.name)

    def header_field_name(self):
        return 'User'

_HEADER_PATTERN = re.compile(r'(?P<header>\S+)\s*:\s*(?P<value>.+)(\r\n)?')
'''Regular expression pattern to match the header name and value.'''

def header_from_string(string):
    '''Instantiate a Header object from a string.

    Parameters
    ----------
    string : str
        Text of a single header from a request or response.

    Returns
    -------
    Header
        A subclass of Header.

    Raises
    ------
    aiospamc.exceptions.HeaderCantParse
    '''

    #pylint: disable=too-many-return-statements
    match = _HEADER_PATTERN.match(string)
    if not match:
        raise HeaderCantParse({'message': 'Unable to parse string',
                               'string': string,
                               'pattern': _HEADER_PATTERN.pattern})

    header = match.groupdict()['header'].strip().lower()
    value = match.groupdict()['value'].strip().lower()

    if header == 'compress':
        return Compress.parse(value)
    elif header == 'content-length':
        return ContentLength.parse(value)
    elif header == 'message-class':
        return MessageClass.parse(value)
    elif header == 'didremove':
        return DidRemove.parse(value)
    elif header == 'didset':
        return DidSet.parse(value)
    elif header == 'remove':
        return Remove.parse(value)
    elif header == 'set':
        return Set.parse(value)
    elif header == 'spam':
        return Spam.parse(value)
    elif header == 'user':
        return User.parse(value)
    else:
        return XHeader(header, value)
