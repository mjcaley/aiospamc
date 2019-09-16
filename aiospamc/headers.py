#!/usr/bin/env python3

'''Collection of request and response headers.'''

import getpass

from .options import ActionOption, MessageClassOption


class Header:
    '''Header base class.'''

    def __bytes__(self) -> bytes:
        raise NotImplementedError

    def __len__(self) -> int:
        return len(bytes(self))

    def field_name(self) -> str:
        '''Returns the the field name for the header.'''

        raise NotImplementedError


class Compress(Header):
    '''Compress header.  Specifies what encryption scheme to use.  So far only
    'zlib' is supported.
    '''

    def __init__(self) -> None:
        self.zlib = True

    def __repr__(self) -> str:
        return '{}()'.format(self.__class__.__name__)

    def __bytes__(self) -> bytes:
        return b'%b: zlib\r\n' % (self.field_name().encode())

    def field_name(self) -> str:
        return 'Compress'


class ContentLength(Header):
    '''ContentLength header.  Indicates the length of the body in bytes.'''

    def __init__(self, length: int = 0) -> None:
        '''ContentLength constructor.

        :param length: Length of the body.
        '''
        self.length = length

    def __bytes__(self) -> bytes:
        return b'%b: %d\r\n' % (self.field_name().encode(),
                                self.length)

    def __repr__(self) -> str:
        return '{}(length={})'.format(self.__class__.__name__, self.length)

    def field_name(self) -> str:
        return 'Content-length'


class MessageClass(Header):
    '''MessageClass header.  Used to specify whether a message is 'spam' or
    'ham.'
    '''

    def __init__(self, value: MessageClassOption = None) -> None:
        '''MessageClass constructor.

        :param value: Specifies the classification of the message.
        '''

        self.value = value or MessageClassOption.ham

    def __bytes__(self) -> bytes:
        return b'%b: %b\r\n' % (self.field_name().encode(),
                                self.value.name.encode())

    def __repr__(self) -> str:
        return '{}(value={})'.format(self.__class__.__name__, str(self.value))

    def field_name(self) -> str:
        return 'Message-class'


class _SetRemoveBase(Header):
    '''Base class for headers that implement "local" and "remote" rules.'''

    def __init__(self, action: ActionOption = None) -> None:
        '''_SetRemoveBase constructor.

        :param action: Actions to be done on local or remote.
        '''

        self.action = action or ActionOption(local=False, remote=False)

    def __bytes__(self) -> bytes:
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

    def __repr__(self) -> str:
        return '{}(action={})'.format(self.__class__.__name__,
                                      repr(self.action))


class DidRemove(_SetRemoveBase):
    '''DidRemove header.  Used by SPAMD to indicate if a message was removed
    from either a local or remote database in response to a TELL request.'''

    def field_name(self) -> str:
        return 'DidRemove'


class DidSet(_SetRemoveBase):
    '''DidRemove header.  Used by SPAMD to indicate if a message was added to
    either a local or remote database in response to a TELL request.'''

    def field_name(self) -> str:
        return 'DidSet'


class Remove(_SetRemoveBase):
    '''Remove header.  Used in a TELL request to ask the SPAMD service remove
    a message from a local or remote database.  The SPAMD service must have the
    --allow-tells switch in order for this to do anything.'''

    def field_name(self):
        return 'Remove'


class Set(_SetRemoveBase):
    '''Set header.  Used in a TELL request to ask the SPAMD service add a
    message from a local or remote database.  The SPAMD service must have the
    --allow-tells switch in order for this to do anything.'''

    def field_name(self) -> str:
        return 'Set'


class Spam(Header):
    '''Spam header.  Used by the SPAMD service to report on if the submitted
    message was spam and the score/threshold that it used.'''

    def __init__(self, value: bool = False, score: float = 0.0, threshold: float = 0.0) -> None:
        '''Spam header constructor.

        :param value: True if the message is spam, False if not.
        :param score: Score of the message after being scanned.
        :param threshold: Threshold of which the message would have been marked as spam.
        '''

        self.value = value
        self.score = score
        self.threshold = threshold

    def __bytes__(self) -> bytes:
        return b'%b: %b ; %.1f / %.1f\r\n' % (self.field_name().encode(),
                                              str(self.value).encode(),
                                              self.score,
                                              self.threshold)

    def __repr__(self) -> str:
        return '{}(value={}, score={}, threshold={})'.format(self.__class__.__name__,
                                                             self.value,
                                                             self.score,
                                                             self.threshold)

    def field_name(self) -> str:
        return 'Spam'


class User(Header):
    '''User header.  Used to specify which user the SPAMD service should use
    when loading configuration files.'''

    def __init__(self, name: str = None) -> None:
        '''User constructor.

        :param name: Name of the user account.
        '''

        self.name = name or getpass.getuser()

    def __bytes__(self) -> bytes:
        return b'%b: %b\r\n' % (self.field_name().encode(),
                                self.name.encode())

    def __repr__(self) -> str:
        return '{}(name={})'.format(self.__class__.__name__, repr(self.name))

    def field_name(self) -> str:
        return 'User'


class XHeader(Header):
    '''Extension header.  Used to specify a header that's not supported
    natively by the SPAMD service.'''

    def __init__(self, name: str, value: str) -> None:
        '''XHeader constructor.

        Parameters
        ----------
        name
            Name of the header.
        value
            Contents of the value.
        '''

        self.name = name
        self.value = value

    def __bytes__(self) -> bytes:
        return b'%b: %b\r\n' % (self.field_name().encode(),
                                self.value.encode())

    def __repr__(self) -> str:
        return '{}(name={}, value={})'.format(self.__class__.__name__,
                                              repr(self.name),
                                              repr(self.value))

    def field_name(self) -> str:
        return self.name
