#!/usr/bin/env python3

import enum
import getpass
import re
from collections import namedtuple

from aiospamc.options import Action, MessageClassOption


class Header:
    '''Header base class'''

    @classmethod
    def parse(cls, string):
        '''Returns an instance of the object from a string.'''
        raise NotImplementedError

    def __bytes__(self):
        '''UFT-8 encoded output of the header.'''
        return self.compose().encode()

    def __len__(self):
        '''Length of the UTF-8 encoded output of the header.'''
        return len(bytes(self))

    def __str__(self):
        '''Text representation of the header.'''
        return self.compose()

    def compose(self):
        ''''''
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
            return None

    def __init__(self):
        self.zlib = True

    def __repr__(self):
        return 'Compress()'

    def compose(self):
        return 'Compress: zlib\r\n'

class ContentLength(Header):
    pattern = re.compile(r'\s*\d+\s*')

    @classmethod
    def parse(cls, string):
        match = cls.pattern.match(string)
        if match:
            obj = cls(int(match.group()))
            return obj
        else:
            return None

    def __init__(self, length=0):
        self.length = length

    def __repr__(self):
        return 'Content-length: {}'.format(self.length)

    def compose(self):
        return 'Content-length: {}\r\n'.format(self.length)

class XHeader(Header):
    pattern = re.compile('\s*(?P<name>\S+)\s*:\s*(?P<value>\S+)\s*')

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return 'XHeader(name={}, value=[])'.format(self.name, self.value)

    def compose(self):
        return '{} : {}'.format(self.name, self.value)

class MessageClass(Header):
    pattern = re.compile(r'^\s*(?P<ham>ham)\s*$|^\s*(?P<spam>spam)\s*$', flags=re.IGNORECASE)

    @classmethod
    def parse(cls, string):
        match = cls.pattern.match(string)
        if match:
            obj = cls()
            if match.groupdict()['ham']:
                obj.value = MessageClassOption.ham
            elif match.groupdict()['spam']:
                obj.value = MessageClassOption.spam
            return obj
        else:
            return None

    def __init__(self, value: MessageClassOption):
        self.value = value

    def __repr__(self):
        return 'MessageClass(value={})'.format(self.value)

    def compose(self):
        return 'Message-class: {}\r\n'.format(self.value.name)

class _SetRemove(Header):
    '''Base class for headers that implement "local" and "remote" rules.'''

    local_pattern = re.compile(r'.*local.*', flags=re.IGNORECASE)
    remote_pattern = re.compile(r'.*remote.*', flags=re.IGNORECASE)

    @classmethod
    def parse(cls, string):
        obj = cls(
                  Action(bool(local_pattern.match(string)), 
                         bool(remote_pattern.match(string)))
                 )

        return obj

    def __init__(self, action=Action(local=False, remote=False)):
        self.action = action

    def _compose(self, header_name):
        values = []
        if self.action.local:
            values.append('local')
        if self.action.remote:
            values.append('remote')

        return '{}: {}\r\n'.format(header_name, ', '.join(values))

class DidRemove(_SetRemove):
    def __repr(self):
        return 'DidRemove(local={}, remote={})'.format(self.action.local, self.action.remote)

    def compose(self):
        return self._compose('DidRemove')

class DidSet(_SetRemove):
    def __repr(self):
        return 'DidSet(local={}, remote={})'.format(self.action.local, self.action.remote)

    def compose(self):
        return self._compose('DidSet')

class Remove(_SetRemove):
    def __repr(self):
        return 'Remove(local={}, remote={})'.format(self.action.local, self.action.remote)

    def compose(self):
        return self._compose('Remove')

class Set(_SetRemove):
    def __repr(self):
        return 'Set(local={}, remote={})'.format(self.action.local, self.action.remote)

    def compose(self):
        return self._compose('Set')

class Spam(Header):
    pattern = re.compile(r'\s*'
                         r'((?P<true>true)|(?P<false>false))'
                         r'\s*;\s*'
                         r'(?P<score>\d+(\.\d+)?)'
                         r'\s*/\s*'
                         r'(?P<threshold>\d+(\.\d+)?)'
                         r'\s*', flags=re.IGNORECASE)

    @classmethod
    def parse(cls, string):
        match = cls.pattern.match(string)
        if match:
            value = match.groupdict()['true']
            score = match.groupdict()['score']
            threshold = match.groupdict()['threshold']

            obj = cls()
            if value:
                obj.value = True
            else:
                obj.value = False

            if score:
                obj.score = float(score)
            else:
                obj.score = 0.0

            if threshold:
                obj.threshold = float(threshold)
            else:
                obj.threshold = 0.0

            return obj
        else:
            return None

    def __init__(self, value=False, score='0', threshold='0'):
        self.value = value
        self.score = score
        self.threshold = threshold

    def __repr__(self):
        return 'Spam(value={}, score={}, threshold={})'.format(self.value, self.score, self.threshold)

    def compose(self):
        return 'Spam: {} ; {} / {}\r\n'.format(self.value, self.score, self.threshold)

class User(Header):
    pattern = re.compile(r'^\s*(?P<user>[a-zA-Z0-9_-]+)\s*$')

    @classmethod
    def parse(cls, string):
        match = cls.pattern.match(string)
        if match:
            obj = cls(match.groupdict()['user'])
            return obj
        else:
            return None

    def __init__(self, name = getpass.getuser()):
        self.name = name

    def __repr__(self):
        return 'User(name={})'.format(self.name)

    def compose(self):
        return 'User: {}\r\n'.format(self.name)

header_pattern = re.compile(r'(?P<header>\S+)\s*:\s*(?P<value>.+)(\r\n)?')

def header_from_string(string):
    match = header_pattern.match(string).groupdict()
    header = match['header'].strip().lower()
    value = match['value'].strip().lower()

    if header == 'compress':
        return Compress.parse(value)
    elif header == 'content-length':
        return ContentLength.parse(value)
    elif header == 'message-class':
        return MessageClass.parse(value)
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
