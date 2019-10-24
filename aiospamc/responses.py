#!/usr/bin/env python3

'''Contains classes used for responses.'''

import enum
from typing import Mapping, SupportsBytes, Union
import zlib

from .common import SpamcBody, SpamcHeaders
from .exceptions import (UsageException, DataErrorException, NoInputException, NoUserException,
                         NoHostException, UnavailableException, InternalSoftwareException, OSErrorException,
                         OSFileException, CantCreateException, IOErrorException, TemporaryFailureException,
                         ProtocolException, NoPermissionException, ConfigException, TimeoutException, ResponseException)
from .header_values import ContentLengthValue, HeaderValue


class Status(enum.IntEnum):
    '''Enumeration of status codes that the SPAMD will accompany with a
    response.

    Reference: https://svn.apache.org/repos/asf/spamassassin/trunk/spamd/spamd.raw
    Look for the %resphash variable.
    '''

    def __new__(cls, value, exception=None, description=''):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.exception = exception
        obj.description = description

        return obj

    EX_OK = 0, None, 'No problems'
    EX_USAGE = 64, UsageException, 'Command line usage error'
    EX_DATAERR = 65, DataErrorException, 'Data format error'
    EX_NOINPUT = 66, NoInputException, 'Cannot open input'
    EX_NOUSER = 67, NoUserException, 'Addressee unknown'
    EX_NOHOST = 68, NoHostException, 'Host name unknown'
    EX_UNAVAILABLE = 69, UnavailableException, 'Service unavailable'
    EX_SOFTWARE = 70, InternalSoftwareException, 'Internal software error'
    EX_OSERR = 71, OSErrorException, 'System error (e.g., can\'t fork)'
    EX_OSFILE = 72, OSFileException, 'Critical OS file missing'
    EX_CANTCREAT = 73, CantCreateException, 'Can\'t create (user) output file'
    EX_IOERR = 74, IOErrorException, 'Input/output error'
    EX_TEMPFAIL = 75, TemporaryFailureException, 'Temp failure; user is invited to retry'
    EX_PROTOCOL = 76, ProtocolException, 'Remote error in protocol'
    EX_NOPERM = 77, NoPermissionException, 'Permission denied'
    EX_CONFIG = 78, ConfigException, 'Configuration error'
    EX_TIMEOUT = 79, TimeoutException, 'Read timeout'


class Response:
    '''Class to encapsulate response.'''

    def __init__(
            self,
            version: str = '1.5',
            status_code: Union[Status, int] = 0,
            message: str = '',
            headers: Mapping[str, HeaderValue] = None,
            body: bytes = b'',
            **_
    ):
        '''Response constructor.

        :param version: Version reported by the SPAMD service response.
        :param status_code: Success or error code.
        :param message: Message associated with status code.
        :param body: Byte string representation of the body.
        :param headers: Collection of headers to be added.
        '''

        self.version = version

        self.headers = SpamcHeaders(headers=headers)

        try:
            self.status_code = Status(status_code)
        except ValueError:
            self.status_code = status_code

        self.message = message

        self.body = body

    def __bytes__(self) -> bytes:
        if 'Compress' in self.headers:
            body = zlib.compress(self.body)
        else:
            body = self.body

        if len(body) > 0:
            self.headers['Content-length'] = ContentLengthValue(length=len(body))

        if isinstance(self.status_code, Status):
            status = self.status_code.value
            message = str(self.status_code).encode('ascii')
        else:
            status = self.status_code
            message = self.message.encode('ascii')

        return b'SPAMD/%(version)b ' \
               b'%(status)d ' \
               b'%(message)b\r\n' \
               b'%(headers)b\r\n' \
               b'%(body)b' % {b'version': self.version.encode('ascii'),
                              b'status': status,
                              b'message': message,
                              b'headers': bytes(self.headers),
                              b'body': body}

    def __str__(self):
        return '<{} - {}: {} object at {}>'.format(
            self.status_code.value,
            self.status_code.name,
            '.'.join([self.__class__.__module__, self.__class__.__qualname__]),
            id(self)
        )

    body = SpamcBody()  # type: Union[bytes, SupportsBytes]

    def raise_for_status(self) -> None:
        if isinstance(self.status_code, Status):
            if self.status_code.exception:
                raise self.status_code.exception
            return
        else:
            raise ResponseException
