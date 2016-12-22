#!/usr/bin/env python3

import getpass
import re


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
            obj = cls( int(match.group()) )
            return obj
        else:
            return None
    
    def __init__(self, length = 0):
        self.length = length
        
    def compose(self):
        return 'Content-length: {}\r\n'.format(self.length)
    
class MessageClass(Header):
    pattern = re.compile(r'^\s*(?P<ham>ham)\s*$|^\s*(?P<spam>spam)\s*$', flags=re.IGNORECASE)
    
    @classmethod
    def parse(cls, string):
        match = cls.pattern.match(string)
        if match:
            obj = cls()
            if match.groupdict()['ham']:
                obj.ham = True
            elif match.groupdict()['spam']:
                obj.spam = True
            return obj
        else:
            return None
    
    def __init__(self, ham = False, spam = False):
        self.ham = ham
        self.spam = spam
        
    def __repr__(self):
        return 'MessageClass(ham={}, spam={})'.format(self.spam, self.ham)
        
    def compose(self):
        header = 'Message-class: {}\r\n'
        if self.ham:
            header = header.format('ham')
        elif self.spam:
            header = header.format('spam')
        else:
            raise InvalidHeader('Neither "ham" or "spam" are set')

        return header
        
class Remove(Header):
    pattern = re.compile(r'\s*(?P<remote>remote)\s*|\s*(?P<local>local)\s*', flags=re.IGNORECASE)
    
    @classmethod
    def parse(cls, string):
        obj = cls()
        
        for section in string.split(','):
            match = cls.pattern.match(section)
            if match:
                if match.groupdict()['local']:
                    obj.local = True
                elif match.groupdict()['remote']:
                    obj.remote = True

        if not obj.local and not obj.remote:
            # couldn't find any matches
            return None
        else:
            return obj
        
    def __init__(self, local = False, remote = False):
        self.local = local
        self.remote = remote
    
    def __repr(self):
        return 'Remove(local={}, remote={})'.format(self.local, self.remote)
    
    def compose(self):
        if not (self.local or self.remote):
            raise InvalidHeader('Neither "local" or "remote" are set')
        
        header = 'Remove: {}\r\n'
        values = []
        if self.local:
            value.append('local')
        if self.remote:
            value.append('remote')
        header.format(', '.join(values))

        return header
        
class Set(Header):
    pattern = re.compile(r'\s*(?P<remote>remote)\s*|\s*(?P<local>local)\s*', flags=re.IGNORECASE)
    
    @classmethod
    def parse(cls, string):
        obj = cls()
        
        for section in string.split(','):
            match = cls.pattern.match(section)
            if match:
                if match.groupdict()['local']:
                    obj.local = True
                elif match.groupdict()['remote']:
                    obj.remote = True

        if not obj.local and not obj.remote:
            # couldn't find any matches
            return None
        else:
            return obj
        
    def __init__(self, local = False, remote = False):
        self.local = local
        self.remote = remote
    
    def __repr__(self):
        return 'Set(local={}, remote={})'.format(self.local, self.remote)
    
    def compose(self):
        if not (self.local or self.remote):
            raise InvalidHeader('Neither "local" or "remote" are set')
        
        header = 'Set: {}'
        values = []
        if self.local:
            value.append('local')
        if self.remote:
            value.append('remote')
        header.format(', '.join(values))

        return header
    
class Spam(Header):
    pattern = re.compile(r'\s*((?P<true>true)|(?P<false>false))\s*;\s*(?P<score>\d+(\.\d+)?)\s*/\s*(?P<threshold>\d+(\.\d+)?)\s*', flags=re.IGNORECASE)
    
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
    
    def __init__(self, value = False, score = '0', threshold = '0'):
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
    
header_pattern = re.compile(r'(?P<header>\w+)\s*:\s*(?P<value>.+)(\r\n)?')

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
        return None