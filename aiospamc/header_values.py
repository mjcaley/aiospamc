#!/usr/bin/env python3

'''Collection of request and response header value objects.'''

import getpass

from .options import ActionOption, MessageClassOption


class HeaderValue:
    pass


class GenericHeaderValue(HeaderValue):
    '''Generic header value.'''
    
    def __init__(self, value: str, encoding='utf8') -> None:
        self.value = value
        self.encoding = encoding

    def __str__(self):
        return 'value={}, encoding={}'.format(repr(self.value), repr(self.encoding))

    def __bytes__(self) -> bytes:
        return self.value.encode(self.encoding)

    def __eq__(self, other):
        try:
            return other.value == self.value and other.encoding == self.encoding
        except AttributeError:
            return False

    def __repr__(self):
        return '{}(value={}, encoding={})'.format(
            self.__class__.__qualname__,
            repr(self.value),
            repr(self.encoding)
        )


class CompressValue(HeaderValue):
    '''Compress header.  Specifies what encryption scheme to use.  So far only
    'zlib' is supported.
    '''

    def __init__(self, algorithm='zlib') -> None:
        '''Constructor

        :param algorithm: Compression algorithm to use.  Currently on zlib is supported.
        '''

        self.algorithm = algorithm

    def __str__(self):
        return 'algorithm={}'.format(repr(self.algorithm))

    def __eq__(self, other):
        try:
            return self.algorithm == other.algorithm
        except AttributeError:
            return False

    def __repr__(self) -> str:
        return '{}()'.format(self.__class__.__qualname__)

    def __bytes__(self) -> bytes:
        return self.algorithm.encode('ascii')


class ContentLengthValue(HeaderValue):
    '''ContentLength header.  Indicates the length of the body in bytes.'''

    def __init__(self, length: int = 0) -> None:
        '''ContentLength constructor.

        :param length: Length of the body.
        '''
        self.length = length

    def __str__(self):
        return 'length={}'.format(repr(self.length))

    def __eq__(self, other):
        try:
            return self.length == other.length
        except AttributeError:
            return False

    def __bytes__(self) -> bytes:
        return str(self.length).encode('ascii')

    def __repr__(self) -> str:
        return '{}(length={})'.format(self.__class__.__qualname__, self.length)


class MessageClassValue(HeaderValue):
    '''MessageClass header.  Used to specify whether a message is 'spam' or
    'ham.'
    '''

    def __init__(self, value: MessageClassOption = None) -> None:
        '''MessageClass constructor.

        :param value: Specifies the classification of the message.
        '''

        self.value = value or MessageClassOption.ham

    def __str__(self):
        return self.value.name

    def __eq__(self, other):
        try:
            return self.value == other.value
        except AttributeError:
            return False

    def __bytes__(self) -> bytes:
        return self.value.name.encode('ascii')

    def __repr__(self) -> str:
        return '{}(value={})'.format(self.__class__.__qualname__, str(self.value))


class SetOrRemoveValue(HeaderValue):
    '''Base class for headers that implement "local" and "remote" rules.'''

    def __init__(self, action: ActionOption = None) -> None:
        '''_SetRemoveBase constructor.

        :param action: Actions to be done on local or remote.
        '''

        self.action = action or ActionOption(local=False, remote=False)

    def __str__(self):
        return 'local={}, remote={}'.format(str(self.action.local), str(self.action.remote))

    def __eq__(self, other):
        try:
            return self.action == other.action
        except AttributeError:
            return False

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

        return b', '.join(values)

    def __repr__(self) -> str:
        return '{}(action={})'.format(self.__class__.__qualname__,
                                      repr(self.action))


class SpamValue(HeaderValue):
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

    def __str__(self):
        return 'value={}, score={}, threshold={}'.format(str(self.value), str(self.score), str(self.threshold))

    def __eq__(self, other):
        try:
            return all([self.value == other.value, self.score == other.score, self.threshold == other.threshold])
        except AttributeError:
            return False

    def __bytes__(self) -> bytes:
        return b'%b ; %.1f / %.1f' % (str(self.value).encode('ascii'),
                                          self.score,
                                          self.threshold)

    def __repr__(self) -> str:
        return '{}(value={}, score={}, threshold={})'.format(self.__class__.__qualname__,
                                                             self.value,
                                                             self.score,
                                                             self.threshold)


class UserValue(HeaderValue):
    '''User header.  Used to specify which user the SPAMD service should use
    when loading configuration files.'''

    def __init__(self, name: str = None) -> None:
        '''User constructor.

        :param name: Name of the user account.
        '''

        self.name = name or getpass.getuser()

    def __str__(self):
        return 'name={}'.format(self.name)

    def __eq__(self, other):
        try:
            return self.name == other.name
        except AttributeError:
            return False

    def __bytes__(self) -> bytes:
        return self.name.encode('ascii')

    def __repr__(self) -> str:
        return '{}(name={})'.format(self.__class__.__qualname__, repr(self.name))
