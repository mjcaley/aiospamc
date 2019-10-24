#!/usr/bin/env python3

'''Contains all requests that can be made to the SPAMD service.'''

from typing import Mapping, SupportsBytes, Union
import zlib

from .common import SpamcBody, SpamcHeaders
from .header_values import ContentLengthValue, HeaderValue


class Request:
    '''SPAMC request object.'''

    def __init__(
        self,
        verb: str = None,
        version: str = '1.5',
        headers: Mapping[str, Union[str, HeaderValue]] = None,
        body: Union[bytes, SupportsBytes] = b'',
        **_
    ) -> None:
        '''Request constructor.

        :param verb: Method name of the request.
        :param version: Version of the protocol.
        :param headers: Collection of headers to be added.
        :param body: Byte string representation of the body.
        '''

        self.verb = verb
        self.version = version
        self.headers = SpamcHeaders(headers=headers)
        self.body = body

    def __bytes__(self) -> bytes:
        if 'Compress' in self.headers.keys():
            body = zlib.compress(self.body)
        else:
            body = self.body

        if len(body) > 0:
            self.headers['Content-length'] = ContentLengthValue(length=len(body))

        request = (b'%(verb)b '
                   b'SPAMC/%(version)b'
                   b'\r\n'
                   b'%(headers)b\r\n'
                   b'%(body)b')

        return request % {b'verb': self.verb.encode('ascii'),
                          b'version': self.version.encode('ascii'),
                          b'headers': bytes(self.headers),
                          b'body': body}

    def __str__(self):
        return '<{}: {} object at {}>'.format(
            self.verb,
            '.'.join([self.__class__.__module__, self.__class__.__qualname__]),
            id(self)
        )

    body = SpamcBody()  # type: Union[bytes, SupportsBytes]
