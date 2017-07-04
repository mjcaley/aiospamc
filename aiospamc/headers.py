#!/usr/bin/env python3

'''Collection of request and response headers.'''

import getpass

from aiospamc.options import ActionOption, MessageClassOption


class Header:
    '''Header base class.'''

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

    def __init__(self):
        self.zlib = True

    def __repr__(self):
        return '{}()'.format(self.__class__.__name__)

    def __bytes__(self):
        return b'%b: zlib\r\n' % (self.field_name().encode())

    def field_name(self):
        return 'Compress'


class ContentLength(Header):
    '''ContentLength header.  Indicates the length of the body in bytes.

    Attributes
    ----------
    length : int
        Length of the body.
    '''

    def __init__(self, length=0):
        '''ContentLength constructor.

        Parameters
        ----------
        length : :obj:`int`, optional
            Length of the body.
        '''
        self.length = length

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
    value : :class:`aiospamc.options.MessageClassOption`
        Specifies the classification of the message.
    '''

    def __init__(self, value=None):
        '''MessageClass constructor.

        Parameters
        ----------
        value : :class:`aiospamc.options.MessageClassOption`, optional
            Specifies the classification of the message.
        '''

        self.value = value or MessageClassOption.ham

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
    action : :class:`aiospamc.options.ActionOption`
        Actions to be done on local or remote.
    '''

    def __init__(self, action=None):
        '''_SetRemoveBase constructor.

        Parameters
        ----------
        action : :class:`aiospamc.options.ActionOption`, optional
            Actions to be done on local or remote.
        '''

        self.action = action or ActionOption(local=False, remote=False)

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

    def __repr__(self):
        return '{}(action={})'.format(self.__class__.__name__,
                                      repr(self.action))


class DidRemove(_SetRemoveBase):
    '''DidRemove header.  Used by SPAMD to indicate if a message was removed
    from either a local or remote database in response to a TELL request.

    Attributes
    ----------
    action : :class:`aiospamc.options.ActionOption`
        Actions to be done on local or remote.
    '''

    def field_name(self):
        return 'DidRemove'


class DidSet(_SetRemoveBase):
    '''DidRemove header.  Used by SPAMD to indicate if a message was added to
    either a local or remote database in response to a TELL request.

    Attributes
    ----------
    action : :class:`aiospamc.options.ActionOption`
        Actions to be done on local or remote.
    '''

    def field_name(self):
        return 'DidSet'


class Remove(_SetRemoveBase):
    '''Remove header.  Used in a TELL request to ask the SPAMD service remove
    a message from a local or remote database.  The SPAMD service must have the
    --allow-tells switch in order for this to do anything.

    Attributes
    ----------
    action : :class:`aiospamc.options.ActionOption`
        Actions to be done on local or remote.
    '''

    def field_name(self):
        return 'Remove'


class Set(_SetRemoveBase):
    '''Set header.  Used in a TELL request to ask the SPAMD service add a
    message from a local or remote database.  The SPAMD service must have the
    --allow-tells switch in order for this to do anything.

    Attributes
    ----------
    action : :class:`aiospamc.options.ActionOption`
        Actions to be done on local or remote.
    '''

    def field_name(self):
        return 'Set'


class Spam(Header):
    '''Spam header.  Used by the SPAMD service to report on if the submitted
    message was spam and the score/threshold that it used.

    Attributes
    ----------
    value : :obj:`bool`
            True if the message is spam, False if not.
    score : :obj:`float`
        Score of the message after being scanned.
    threshold : :obj:`float`
        Threshold of which the message would have been marked as spam.
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
    name : :obj:`str`
        Name of the user account.
    '''

    def __init__(self, name=None):
        '''User constructor.

        Parameters
        ----------
        name : :obj:`str`, optional
            Name of the user account.
        '''

        self.name = name or getpass.getuser()

    def __bytes__(self):
        return b'%b: %b\r\n' % (self.field_name().encode(),
                                self.name.encode())

    def __repr__(self):
        return '{}(name={})'.format(self.__class__.__name__, repr(self.name))

    def field_name(self):
        return 'User'


class XHeader(Header):
    '''Extension header.  Used to specify a header that's not supported
    natively by the SPAMD service.

    Attributes
    ----------
    name : :obj:`str`
        Name of the header.
    value : :obj:`str`
        Contents of the value.
    '''

    def __init__(self, name, value):
        '''XHeader constructor.

        Parameters
        ----------
        name : :obj:`str`
            Name of the header.
        value : :obj:`str`
            Contents of the value.
        '''

        self.name = name
        self.value = value

    def __bytes__(self):
        return b'%b: %b\r\n' % (self.field_name().encode(),
                                self.value.encode())

    def __repr__(self):
        return '{}(name={}, value={})'.format(self.__class__.__name__,
                                              repr(self.name),
                                              repr(self.value))

    def field_name(self):
        return self.name
