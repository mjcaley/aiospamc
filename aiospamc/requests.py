#!/usr/bin/env python3

'''Contains all requests that can be made to the SPAMD service.'''

from typing import Iterator, SupportsBytes, Union
import zlib

from .common import SpamcBody, SpamcHeaders
from .headers import Header


class Request:
    '''SPAMC request object.'''

    def __init__(
        self,
        verb: str,
        version: str = '1.5',
        headers: Iterator[Header] = None,
        body: Union[bytes, SupportsBytes] = None
    ) -> None:
        '''Request constructor.

        :param verb: Method name of the request.
        :param version: Version of the protocol.
        :param headers: Collection of headers to be added.
        :param body: Byte string representation of the body.
        '''

        self.headers = SpamcHeaders(headers=headers)
        self.verb = verb
        self.version = version
        if body:
            self.body = body
        else:
            self.body = b''

    def __bytes__(self) -> bytes:
        if 'Compress' in self.headers.keys():
            body = zlib.compress(self.body)
        else:
            body = self.body

        request = (b'%(verb)b '
                   b'SPAMC/%(version)b'
                   b'\r\n'
                   b'%(headers)b\r\n'
                   b'%(body)b')

        return request % {b'verb': self.verb.encode(),
                          b'version': self.version.encode(),
                          b'headers': b''.join(map(bytes, self.headers.values())),
                          b'body': body}

    body = SpamcBody()  # type: Union[bytes, SupportsBytes]
