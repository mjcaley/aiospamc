#!/usr/bin/env python3

'''Collection of request and response headers.'''

import getpass
import re

from aiospamc.exceptions import HeaderCantParse
from aiospamc.transport import Inbound, Outbound
from aiospamc.options import Action, MessageClassOption


class Header(Inbound, Outbound):
    '''Header base class'''

    def __str__(self):
        '''Text representation of the header.'''
        return self.compose()

    def header_field_name(self):
        '''The string of the field name for the header.'''
        raise NotImplementedError

class Compress(Header):
    pattern = re.compile(r'\s*zlib\s*')

    @classmethod
    def parse(cls, string):
        match = cls.pattern.match(string)
        if match:
            obj = cls()
            return obj
        else:
            raise HeaderCantParse({'message': 'Unable to parse string',
                                   'string': string,
                                   'pattern': cls.pattern.pattern})

    def __init__(self):
        self.zlib = True

    def __repr__(self):
        return '{}()'.format(self.__class__.__name__)

    def compose(self):
        return '{}: zlib\r\n'.format(self.header_field_name())

    def header_field_name(self):
        return 'Compress'

class ContentLength(Header):
    pattern = re.compile(r'\s*\d+\s*')

    @classmethod
    def parse(cls, string):
        match = cls.pattern.match(string)
        if match:
            obj = cls(int(match.group()))
            return obj
        else:
            raise HeaderCantParse({'message': 'Unable to parse string',
                                   'string': string,
                                   'pattern': cls.pattern.pattern})

    def __init__(self, length=0):
        self.length = length

    def __repr__(self):
        return '{}(length={})'.format(self.__class__.__name__, self.length)

    def compose(self):
        return '{}: {}\r\n'.format(self.header_field_name(), self.length)

    def header_field_name(self):
        return 'Content-length'

class XHeader(Header):
    pattern = re.compile(r'\s*(?P<name>\S+)\s*:\s*(?P<value>\S+)\s*')

    @classmethod
    def parse(cls, string):
        match = cls.pattern.match(string)
        if match:
            obj = cls(match.groupdict()['name'], match.groupdict()['value'])
            return obj
        else:
            raise HeaderCantParse({'message': 'Unable to parse string',
                                   'string': string,
                                   'pattern': cls.pattern.pattern})

    def __init__(self, name, value):
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
    pattern = re.compile(r'^\s*(?P<value>ham|spam)\s*$', flags=re.IGNORECASE)

    @classmethod
    def parse(cls, string):
        match = cls.pattern.match(string)
        if match:
            obj = cls()
            obj.value = MessageClassOption[match.groupdict()['value']]
            return obj
        else:
            raise HeaderCantParse({'message': 'Unable to parse string',
                                   'string': string,
                                   'pattern': cls.pattern.pattern})

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

    local_pattern = re.compile(r'.*local.*', flags=re.IGNORECASE)
    remote_pattern = re.compile(r'.*remote.*', flags=re.IGNORECASE)

    @classmethod
    def parse(cls, string):
        local_result = bool(cls.local_pattern.match(string))
        remote_result = bool(cls.remote_pattern.match(string))

        if not local_result and not remote_result:
            raise HeaderCantParse({'message': 'Unable to parse string',
                                   'string': string,
                                   'pattern': (cls.local_pattern.pattern,
                                               cls.remote_pattern.pattern)})
        else:
            obj = cls(Action(local_result, remote_result))

        return obj

    def __init__(self, action=Action(local=True, remote=False)):
        self.action = action

    def compose(self):
        values = []
        if self.action.local:
            values.append('local')
        if self.action.remote:
            values.append('remote')

        return '{}: {}\r\n'.format(self.header_field_name(), ', '.join(values))

    def header_field_name(self):
        raise NotImplementedError

class DidRemove(_SetRemove):
    def __repr__(self):
        return '{}(action=Action(local={}, remote={}))'.format(self.__class__.__name__,
                                                               self.action.local,
                                                               self.action.remote)

    def header_field_name(self):
        return 'DidRemove'

class DidSet(_SetRemove):
    def __repr__(self):
        return '{}(action=Action(local={}, remote={}))'.format(self.__class__.__name__,
                                                               self.action.local,
                                                               self.action.remote)

    def header_field_name(self):
        return 'DidSet'

class Remove(_SetRemove):
    def __repr__(self):
        return '{}(action=Action(local={}, remote={}))'.format(self.__class__.__name__,
                                                               self.action.local,
                                                               self.action.remote)

    def header_field_name(self):
        return 'Remove'

class Set(_SetRemove):
    def __repr__(self):
        return '{}(action=Action(local={}, remote={}))'.format(self.__class__.__name__,
                                                               self.action.local,
                                                               self.action.remote)

    def header_field_name(self):
        return 'Set'

class Spam(Header):
    pattern = re.compile(r'\s*'
                         r'(?P<value>true|false)'
                         r'\s*;\s*'
                         r'(?P<score>\d+(\.\d+)?)'
                         r'\s*/\s*'
                         r'(?P<threshold>\d+(\.\d+)?)'
                         r'\s*', flags=re.IGNORECASE)

    @classmethod
    def parse(cls, string):
        match = cls.pattern.match(string)
        if match:
            obj = cls()
            obj.value = bool(match.groupdict()['value'])
            obj.score = float(match.groupdict()['score'])
            obj.threshold = float(match.groupdict()['threshold'])

            return obj
        else:
            raise HeaderCantParse({'message': 'Unable to parse string',
                                   'string': string,
                                   'pattern': cls.pattern.pattern})

    def __init__(self, value=False, score=0.0, threshold=0.0):
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
    pattern = re.compile(r'^\s*(?P<user>[a-zA-Z0-9_-]+)\s*$')

    @classmethod
    def parse(cls, string):
        match = cls.pattern.match(string)
        if match:
            obj = cls(match.groupdict()['user'])
            return obj
        else:
            raise HeaderCantParse({'message': 'Unable to parse string',
                                   'string': string,
                                   'pattern': cls.pattern.pattern})

    def __init__(self, name=getpass.getuser()):
        self.name = name

    def __repr__(self):
        return '{}(name=\'{}\')'.format(self.__class__.__name__, self.name)

    def compose(self):
        return '{}: {}\r\n'.format(self.header_field_name(), self.name)

    def header_field_name(self):
        return 'User'

HEADER_PATTERN = re.compile(r'(?P<header>\S+)\s*:\s*(?P<value>.+)(\r\n)?')

def header_from_string(string):
    match = HEADER_PATTERN.match(string)
    if not match:
        raise HeaderCantParse({'message': 'Unable to parse string',
                               'string': string,
                               'pattern': HEADER_PATTERN.pattern})

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
