#!/usr/bin/env python3

'''Contains all requests that can be made to the SPAMD service.'''

import re

from aiospamc.common import RequestResponseBase
from aiospamc.exceptions import BadRequest


class Request(RequestResponseBase):
    '''SPAMC request object.

    Attributes
    ----------
    verb : str
        Method name of the request.
    protocol_version : str
        Protocol version.
    body : str
        String representation of the body.  An instance of the
        aiospamc.headers.ContentLength will be automatically added.
    '''

    _request_pattern = re.compile(r'^\s*'
                                  r'(?P<verb>[a-zA-Z]+)'
                                  r'\s+'
                                  r'SPAMC/(?P<version>\d+\.\d+)')

    def __init__(self, verb, body=None, *headers):
        '''Request constructor.

        Parameters
        ----------
        verb : str
            Method name of the request.
        body : :obj:`str`, optional
            String representation of the body.  An instance of the
            aiospamc.headers.ContentLength will be automatically added.
        *headers : :obj:`aiospamc.headers.Header`, optional
            Collection of headers to be added.  If it contains an instance of
            aiospamc.headers.Compress then the body is automatically
            compressed.
        '''

        self.verb = verb
        self.protocol_version = '1.5'
        super().__init__(body, *headers)

    @classmethod
    def parse(cls, bytes_string):
        '''Parses a request and returns an instance.

        Parameters
        ----------
        bytes_string : bytes
            Bytes string of the request.

        Returns
        -------
        aiospamc.requests.Request
            An instance of the request.
        '''

        request, *body = bytes_string.split(b'\r\n\r\n', 1)
        request, *headers = request.split(b'\r\n')

        request = request.decode()

        # Process request
        match = cls._request_pattern.match(request)
        if match:
            request_match = match.groupdict()
        else:
            # Not a SPAMD response
            raise BadRequest

        verb = request_match['verb'].strip()
        protocol_version = request_match['version'].strip()

        parsed_headers = cls._parse_headers(headers)
        parsed_body = cls._parse_body(body[0] if body else None, parsed_headers)

        obj = cls(verb,
                  parsed_body,
                  *parsed_headers)
        obj.protocol_version = protocol_version

        return obj

    def __bytes__(self):
        if self._compressed_body:
            body = self._compressed_body
        elif self.body:
            body = self.body.encode()
        else:
            body = b''

        request = (b'%(verb)b '
                   b'SPAMC/%(version)b'
                   b'\r\n'
                   b'%(headers)b\r\n'
                   b'%(body)b')

        return request % {b'verb': self.verb.encode(),
                          b'version': self.protocol_version.encode(),
                          b'headers': b''.join(map(bytes, self._headers.values())),
                          b'body': body}

    def __repr__(self):
        request_format = '{}(verb=\'{}\', version=\'{}\', body={}, headers={})'
        return request_format.format(self.__class__.__name__,
                                     self.verb,
                                     self.protocol_version,
                                     repr(self.body) if self.body else 'None',
                                     [i for i in self._headers.values()])
