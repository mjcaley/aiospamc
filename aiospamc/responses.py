#!/usr/bin/env python3

'''Contains classes used for responses.'''

from enum import IntEnum
from typing import Mapping, SupportsBytes, Union
import zlib

from .common import SpamcHeaders
from .exceptions import *
from .header_values import ContentLengthValue, HeaderValue


class Response:
    '''Class to encapsulate response.'''

    def __init__(
            self,
            version: str = '1.5',
            status_code: int = 0,
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
        return f'<{self.status_code} - ' \
            f'{self.message}: ' \
            f'{".".join([self.__class__.__module__, self.__class__.__qualname__])} ' \
            f'object at {id(self)}>'

    @property
    def body(self) -> bytes:
        return self._body

    @body.setter
    def body(self, value: Union[bytes, SupportsBytes]) -> None:
        self._body = bytes(value)

    def raise_for_status(self) -> None:
        if self.status_code == 0:
            return
        else:
            status_exception = {
                64: UsageException,
                65: DataErrorException,
                66: NoInputException,
                67: NoUserException,
                68: NoHostException,
                69: UnavailableException,
                70: InternalSoftwareException,
                71: OSErrorException,
                72: OSFileException,
                73: CantCreateException,
                74: IOErrorException,
                75: TemporaryFailureException,
                76: ProtocolException,
                77: NoPermissionException,
                78: ConfigException,
                79: TimeoutException,
            }
            if self.status_code in status_exception:
                raise status_exception[self.status_code](self.message)
            else:
                raise ResponseException(self.status_code, self.message)
