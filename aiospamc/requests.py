#!/usr/bin/env python3

'''Contains all requests that can be made to the SPAMD service.'''

import zlib

from aiospamc.common import RequestResponseBase, SpamcBody, SpamcHeaders


class Request(SpamcBody):
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

        self.headers = SpamcHeaders(headers=headers)
        self.verb = verb
        self.version = version
        super().__init__(body=body)

    def __bytes__(self):
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
