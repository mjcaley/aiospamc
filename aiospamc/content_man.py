#!/usr/bin/env python3

'''Contains classes that maniuplate and manage the contents of responses
and requests.
'''

import zlib

from aiospamc.headers import ContentLength


class BodyHeaderManager:
    '''Class that implements header and body management for requests and
    responses.'''

    def __init__(self, body=None, *headers):
        '''
        Parameters
        ----------
        body : str
            String representation of the body.  An instance of the
            aiospamc.headers.ContentLength will be automatically added.
        *headers : tuple of aiospamc.headers.Header
            Collection of headers to be added.  If it contains an instance of
            aiospamc.headers.Compress then the body is automatically
            compressed.
        '''

        self._headers = {item.header_field_name() : item for item in headers}
        self._body = None
        if body:
            self.body = body

    @property
    def body(self):
        '''Contains the contents of the body.

        Returns
        -------
        bytes
            Contents of the body.  If the aiospamc.headers.Compress header is
            present then the value of body will be compressed.'''

        if 'Compress' in self._headers:
            return zlib.decompress(self._body)
        else:
            return self._body

    @body.setter
    def body(self, value):
        '''Sets the contents of the body.

        Parameters
        ----------
        value : str
            The contents to be added.  If the aiospamc.headers.Compress header is
            present then the value of body will be compressed.
        '''

        self._body = value.encode()
        if 'Compress' in self._headers:
            self._compress_body()
        self._set_content_length()

    @body.deleter
    def body(self):
        '''Deletes the body.

        The aiospamc.headers.ContentLength header will be automatically
        deleted.
        '''
        del self._body
        self.delete_header('Content-length')

    def _compress_body(self):
        self._body = zlib.compress(bytes(self._body))
        self._set_content_length()

    def _decompress_body(self):
        self._body = zlib.decompress(bytes(self._body))
        self._set_content_length()

    def _set_content_length(self):
        self.add_header(ContentLength(len(self._body)))

    def add_header(self, header):
        '''Adds a header to the request.  A header with the same name will be
        overwritten.

        Parameters
        ----------
        header : aiospamc.headers.Header
            A header object to be added.
        '''

        if header.header_field_name() == 'Compress' and self._body:
            self._compress_body()
        self._headers[header.header_field_name()] = header

    def get_header(self, header_name):
        '''Gets the header matching the name.

        Parameters
        ----------
        header_name : str
            String name of the header.

        Returns
        -------
        aiospamc.headers.Header
            A Header object or subclass of it.

        Raises
        ------
        KeyError
        '''

        return self._headers[header_name]

    def delete_header(self, header_name):
        '''Deletes the header from the request.

        Parameters
        ----------
        header_name : str
            String name of the header.

        Raises
        ------
        KeyError
        '''

        if header_name == 'Compress' and self._body:
            self._decompress_body()
        self._headers.pop(header_name)
