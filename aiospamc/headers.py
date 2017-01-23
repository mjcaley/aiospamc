#!/usr/bin/env python3

'''Collection of request and response headers.'''

import getpass
import re

from aiospamc.exceptions import HeaderCantParse
from aiospamc.options import _Action, MessageClassOption, RemoveOption, SetOption


class Header:
    '''Header base class.'''

    @classmethod
    def parse(cls, bytes_string):
        '''Parses a bytes string.

        Parameters
        ----------
        bytes_string : bytes
            Bytes string of the header contents.

        Returns
        -------
        aiospamc.headers.Header
            Instance or subclass of Header.
        '''

        raise NotImplementedError

    def __bytes__(self):
        raise NotImplementedError

    def __len__(self):
        return len(bytes(self))

    def field_name(self):
        '''Returns the the field name for the header.

        Returns
        -------
        str
        '''

        raise NotImplementedError

class Compress(Header):
    '''Compress header.  Specifies what encryption scheme to use.  So far only
    'zlib' is supported.

    Attributes
    ----------
    zlib : bool
        True if the zlib compression algorithm is used.
    '''

    _pattern = re.compile(r'\s*zlib\s*')
    '''Regular expression pattern to match 'zlib'.'''

    def __init__(self):
        self.zlib = True

    @classmethod
    def parse(cls, bytes_string):
        string = bytes_string.decode()
        match = cls._pattern.match(string)
        if match:
            obj = cls()
            return obj
        else:
            raise HeaderCantParse({'message': 'Unable to parse string',
                                   'string': string,
                                   'pattern': cls._pattern.pattern})

    def __repr__(self):
        return '{}()'.format(self.__class__.__name__)

    def __bytes__(self):
        return b'%b: zlib\r\n'% (self.field_name().encode())

    def field_name(self):
        return 'Compress'

class ContentLength(Header):
    '''ContentLength header.  Indicates the length of the body in bytes.

    Attributes
    ----------
    length : int
        Length of the body.
    '''

    _pattern = re.compile(r'\s*\d+\s*')
    '''Regular expression pattern to match one or more digits.'''

    def __init__(self, length=0):
        '''ContentLength constructor.

        Parameters
        ----------
        length : :obj:`int`, optional
            Length of the body.
        '''
        self.length = length

    @classmethod
    def parse(cls, bytes_string):
        string = bytes_string.decode()
        match = cls._pattern.match(string)
        if match:
            obj = cls(int(match.group()))
            return obj
        else:
            raise HeaderCantParse({'message': 'Unable to parse string',
                                   'string': string,
                                   'pattern': cls._pattern.pattern})

    def __bytes__(self):
        return b'%b: %d\r\n' % (self.field_name().encode(),
                                self.length)

    def __repr__(self):
        return '{}(length={})'.format(self.__class__.__name__, self.length)

    def field_name(self):
        return 'Content-length'

class MessageClass(Header):
    '''MessageClass header.  Used to specify whether a message is 'spam' or
    'ham.'

    Attributes
    ----------
    value : aiospamc.options.MessageClassOption
        Specifies the classification of the message.
    '''

    _pattern = re.compile(r'^\s*(?P<value>ham|spam)\s*$', flags=re.IGNORECASE)
    '''Regular expression pattern to match either 'spam' or 'ham.\''''

    def __init__(self, value=None):
        '''MessageClass constructor.

        Parameters
        ----------
        value : :obj:`aiospamc.options.MessageClassOption`, optional
            Specifies the classification of the message.
        '''

        self.value = value or MessageClassOption.ham

    @classmethod
    def parse(cls, bytes_string):
        string = bytes_string.decode()
        match = cls._pattern.match(string)
        if match:
            obj = cls()
            obj.value = MessageClassOption[match.groupdict()['value']]
            return obj
        else:
            raise HeaderCantParse({'message': 'Unable to parse string',
                                   'string': string,
                                   'pattern': cls._pattern.pattern})

    def __bytes__(self):
        return b'%b: %b\r\n' % (self.field_name().encode(),
                                self.value.name.encode())

    def __repr__(self):
        return '{}(value={})'.format(self.__class__.__name__, str(self.value))

    def field_name(self):
        return 'Message-class'

class _SetRemoveBase(Header):
    '''Base class for headers that implement "local" and "remote" rules.

    Attributes
    ----------
    action : aiospamc.options._Action
        Actions to be done on local or remote.
    '''

    _local_pattern = re.compile(r'.*local.*', flags=re.IGNORECASE)
    '''Regular expression string to match 'local.\''''
    _remote_pattern = re.compile(r'.*remote.*', flags=re.IGNORECASE)
    '''Regular expression string to match 'remote.\''''

    def __init__(self, action=None):
        '''_SetRemoveBase constructor.

        Parameters
        ----------
        action : :obj:`aiospamc.options._Action`, optional
            Actions to be done on local or remote.
        '''

        self.action = action or _Action(local=False, remote=False)

    @classmethod
    def parse(cls, bytes_string):
        string = bytes_string.decode()
        local_result = bool(cls._local_pattern.match(string))
        remote_result = bool(cls._remote_pattern.match(string))

        if not local_result and not remote_result:
            raise HeaderCantParse({'message': 'Unable to parse string',
                                   'string': string,
                                   'pattern': (cls._local_pattern.pattern,
                                               cls._remote_pattern.pattern)})
        else:
            obj = cls(_Action(local_result, remote_result))

        return obj

    def __bytes__(self):
        if not self.action.local and not self.action.remote:
            # if nothing is set, then return a blank string so the request
            # doesn't get tainted
            return b''

        values = []
        if self.action.local:
            values.append(b'local')
        if self.action.remote:
            values.append(b'remote')

        return b'%b: %b\r\n' % (self.field_name().encode(),
                                b', '.join(values))

class _RemoveBase(_SetRemoveBase):
    '''Base class for all remove-style headers.'''

    def __init__(self, action=None):
        '''_RemoveBase constructor.

        Parameters
        ----------
        action : :obj:`aiospamc.options.RemoveAction`, optional
            Actions to be done on local or remote.
        '''

        super().__init__(action or RemoveOption(local=False, remote=False))

    @classmethod
    def parse(cls, bytes_string):
        obj = super().parse(bytes_string)
        obj.action = RemoveOption(local=obj.action.local,
                                  remote=obj.action.remote)

        return obj

    def __repr__(self):
        return '{}(action={}(local={}, remote={}))'.format(self.__class__.__name__,
                                                           self.action.__class__.__name__,
                                                           self.action.local,
                                                           self.action.remote)

class _SetBase(_SetRemoveBase):
    '''Base class for all set-style headers.'''

    def __init__(self, action=None):
        '''_SetBase constructor.

        Parameters
        ----------
        action : :obj:`aiospamc.options.SetAction`, optional
            Actions to be done on local or remote.
        '''

        super().__init__(action or SetOption(local=False, remote=False))

    @classmethod
    def parse(cls, bytes_string):
        obj = super().parse(bytes_string)
        obj.action = SetOption(local=obj.action.local,
                               remote=obj.action.remote)

        return obj

    def __repr__(self):
        return '{}(action={}(local={}, remote={}))'.format(self.__class__.__name__,
                                                           self.action.__class__.__name__,
                                                           self.action.local,
                                                           self.action.remote)

class DidRemove(_RemoveBase):
    '''DidRemove header.  Used by SPAMD to indicate if a message was removed
    from either a local or remote database in response to a TELL request.

    Attributes
    ----------
    action : aiospamc.options.RemoveAction
        Actions to be done on local or remote.
    '''

    def field_name(self):
        return 'DidRemove'

class DidSet(_SetBase):
    '''DidRemove header.  Used by SPAMD to indicate if a message was added to
    either a local or remote database in response to a TELL request.

    Attributes
    ----------
    action : :obj:`aiospamc.options.SetAction`
        Actions to be done on local or remote.
    '''

    def field_name(self):
        return 'DidSet'

class Remove(_RemoveBase):
    '''Remove header.  Used in a TELL request to ask the SPAMD service remove
    a message from a local or remote database.  The SPAMD service must have the
    --allow-tells switch in order for this to do anything.

    Attributes
    ----------
    action : aiospamc.options.RemoveAction
        Actions to be done on local or remote.
    '''

    def field_name(self):
        return 'Remove'

class Set(_SetBase):
    '''Set header.  Used in a TELL request to ask the SPAMD service add a
    message from a local or remote database.  The SPAMD service must have the
    --allow-tells switch in order for this to do anything.

    Attributes
    ----------
    action : aiospamc.options.SetAction
        Actions to be done on local or remote.
    '''

    def field_name(self):
        return 'Set'

class Spam(Header):
    '''Spam header.  Used by the SPAMD service to report on if the submitted
    message was spam and the score/threshold that it used.

    Attributes
    ----------
    value : bool
            True if the message is spam, False if not.
    score : float
        Score of the message after being scanned.
    threshold : float
        Threshold of which the message would have been marked as spam.
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

    def __init__(self, value=False, score=0.0, threshold=0.0):
        '''Spam header constructor.

        Parameters
        ----------
        value : :obj:`bool`, optional
            True if the message is spam, False if not.
        score : :obj:`float`, optional
            Score of the message after being scanned.
        threshold : :obj:`float`, optional
            Threshold of which the message would have been marked as spam.
        '''

        self.value = value
        self.score = score
        self.threshold = threshold

    @classmethod
    def parse(cls, bytes_string):
        string = bytes_string.decode()
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

    def __bytes__(self):
        return b'%b: %b ; %.1f / %.1f\r\n' % (self.field_name().encode(),
                                              str(self.value).encode(),
                                              self.score,
                                              self.threshold)

    def __repr__(self):
        return '{}(value={}, score={}, threshold={})'.format(self.__class__.__name__,
                                                             self.value,
                                                             self.score,
                                                             self.threshold)

    def field_name(self):
        return 'Spam'

class User(Header):
    '''User header.  Used to specify which user the SPAMD service should use
    when loading configuration files.

    Attributes
    ----------
    name : str
        Name of the user account.
    '''

    _pattern = re.compile(r'^\s*(?P<user>[a-zA-Z0-9_-]+)\s*$')
    '''Regular expression pattern to match the username.'''

    def __init__(self, name=None):
        '''User constructor.

        Parameters
        ----------
        name : :obj:`str`, optional
            Name of the user account.
        '''

        self.name = name or getpass.getuser()

    @classmethod
    def parse(cls, bytes_string):
        string = bytes_string.decode()
        match = cls._pattern.match(string)
        if match:
            obj = cls(match.groupdict()['user'])
            return obj
        else:
            raise HeaderCantParse({'message': 'Unable to parse string',
                                   'string': string,
                                   'pattern': cls._pattern.pattern})

    def __bytes__(self):
        return b'%b: %b\r\n' % (self.field_name().encode(),
                                self.name.encode())

    def __repr__(self):
        return '{}(name=\'{}\')'.format(self.__class__.__name__, self.name)

    def field_name(self):
        return 'User'

class XHeader(Header):
    '''Extension header.  Used to specify a header that's not supported
    natively by the SPAMD service.

    Attributes
    ----------
    name : str
        Name of the header.
    value : str
        Contents of the value.
    '''

    _pattern = re.compile(r'\s*(?P<name>\S+)\s*:\s*(?P<value>\S+)\s*')
    '''Regular expresison pattern to match entire contents of a header
    string.
    '''

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

    @classmethod
    def parse(cls, bytes_string):
        string = bytes_string.decode()
        match = cls._pattern.match(string)
        if match:
            obj = cls(match.groupdict()['name'], match.groupdict()['value'])
            return obj
        else:
            raise HeaderCantParse({'message': 'Unable to parse string',
                                   'string': string,
                                   'pattern': cls._pattern.pattern})

    def __bytes__(self):
        return b'%b: %b\r\n' % (self.field_name().encode(),
                                self.value.encode())

    def __repr__(self):
        return '{}(name=\'{}\', value=\'{}\')'.format(self.__class__.__name__,
                                                      self.name,
                                                      self.value)

    def field_name(self):
        return self.name

def header_from_bytes(bytes_string):
    '''Instantiate a Header object from a bytes object.

    Parameters
    ----------
    bytes_string : bytes
        Text of a single header from a request or response.

    Returns
    -------
    Header
        A subclass of Header.

    Raises
    ------
    aiospamc.exceptions.HeaderCantParse
    '''

    try:
        header, value = bytes_string.split(b':')
        header = header.lower()
    except ValueError:
        raise HeaderCantParse({'message': 'Unable to parse string',
                               'string': bytes_string})

    if header == b'compress':
        return Compress.parse(value)
    elif header == b'content-length':
        return ContentLength.parse(value)
    elif header == b'message-class':
        return MessageClass.parse(value)
    elif header == b'didremove':
        return DidRemove.parse(value)
    elif header == b'didset':
        return DidSet.parse(value)
    elif header == b'remove':
        return Remove.parse(value)
    elif header == b'set':
        return Set.parse(value)
    elif header == b'spam':
        return Spam.parse(value)
    elif header == b'user':
        return User.parse(value)
    else:
        return XHeader(header, value)
