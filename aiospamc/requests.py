#!/usr/bin/env python3

'''Contains all requests that can be made to the SPAMD service.'''

from aiospamc.content_man import BodyHeaderManager
from aiospamc.transport import Outbound


class Request(BodyHeaderManager, Outbound):
    '''SPAMC request object.

    Attributes
    ----------
    verb : str
        Method name of the request.
    body : str
        String representation of the body.  An instance of the
        aiospamc.headers.ContentLength will be automatically added.
    headers : tuple of aiospamc.headers.Header
        Collection of headers to be added.  If it contains an instance of
        aiospamc.headers.Compress then the body is automatically
        compressed.
    '''

    _protocol = b'SPAMC/1.5'
    _request = b'%(verb)b %(protocol)b\r\n%(headers)b\r\n%(body)b'

    def __init__(self, verb, body=None, *headers):
        '''Request constructor.

        Parameters
        ----------
        verb : str
            Method name of the request.
        body : str
            String representation of the body.  An instance of the
            aiospamc.headers.ContentLength will be automatically added.
        headers : tuple of aiospamc.headers.Header
            Collection of headers to be added.  If it contains an instance of
            aiospamc.headers.Compress then the body is automatically
            compressed.
        '''

        self.verb = verb.encode()
        super().__init__(body, *headers)

    def __bytes__(self):
        return self.compose()

    def __repr__(self):
        request_format = '{}(verb=\'{}\', body={}, headers={})'
        return request_format.format(self.__class__.__name__,
                                     self.verb.decode(),
                                     self.body.decode() if self.body else None,
                                     tuple(i for i in self._headers.values()))

    def compose(self):
        request = self._request % {b'verb': self.verb,
                                   b'protocol': self._protocol,
                                   b'headers': b''.join(map(bytes, self._headers.values())),
                                   b'body' : self.body if self.body else b''}

        return request
