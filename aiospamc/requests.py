#!/usr/bin/env python3

'''Contains all requests that can be made to the SPAMD service.'''

from aiospamc.common import RequestResponseBase


class Request(RequestResponseBase):
    '''SPAMC request object.

    Attributes
    ----------
    verb : :obj:`str`
        Method name of the request.
    version : :obj:`str`
        Protocol version.
    body : :obj:`str` or :obj:`bytes`
        String representation of the body.  An instance of the
        :class:`aiospamc.headers.ContentLength` will be automatically added.
    '''

    def __init__(self, verb, version='1.5', headers=None, body=None):
        '''Request constructor.

        Parameters
        ----------
        verb : :obj:`str`
            Method name of the request.
        version: :obj:`str`
            Version of the protocol.
        body : :obj:`str` or :obj:`bytes`, optional
            String representation of the body.  An instance of the
            :class:`aiospamc.headers.ContentLength` will be automatically added.
        headers : tuple of :class:`aiospamc.headers.Header`, optional
            Collection of headers to be added.  If it contains an instance of
            :class:`aiospamc.headers.Compress` then the body is automatically
            compressed.
        '''

        self.verb = verb
        self.version = version
        super().__init__(body, headers)

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
                          b'version': self.version.encode(),
                          b'headers': b''.join(map(bytes, self._headers.values())),
                          b'body': body}
