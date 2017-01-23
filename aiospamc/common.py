#!/usr/bin/env python3

import zlib

from aiospamc.headers import ContentLength, header_from_bytes


class RequestResponseBase:
    '''Base class for requests and responses.'''

    def __init__(self, body=None, *headers):
        '''
        Parameters
        ----------
        body : str
            String representation of the body.  An instance of the
            aiospamc.headers.ContentLength will be automatically added.
        *headers : list of aiospamc.headers.Header
            Collection of headers to be added.  If it contains an instance of
            aiospamc.headers.Compress then the body is automatically
            compressed.
        '''

        self._headers = {item.header_field_name() : item for item in headers}
        self._body = ''
        self._compressed_body = None
        if body:
            self.body = body

    @classmethod
    def parse(cls, bytes_string):
        raise NotImplementedError

    @staticmethod
    def _parse_headers(headers):
        '''Parse headers of a repsonse.

        Parameters
        ----------
        headers : :obj:`tuple` of :obj:`str`
            Collection of strings.

        Returns
        -------
        headers : :obj:`list` of aiospamce.headers.Header
            Collection of Header objects.
        '''

        if not headers:
            return []
        if headers[-1] == b'':
            headers.pop()
        return [header_from_bytes(header) for header in headers]

    @staticmethod
    def _parse_body(body, headers):
        '''Parses a body of a response.

        Parameters
        ----------
        body : bytes
            Bytes representation of body.
        headers : :obj:`tuple` or :obj:`list` of aiospamc.headers.Header
            Collection of headers

        Returns
        -------
        str
            Body in a string object.
        '''

        print(headers)
        if not body:
            return None
        elif any(header.header_field_name() == 'Compress' for header in headers):
            return zlib.decompress(body).decode()
        else:
            return body.decode()

    @property
    def body(self):
        '''Contains the contents of the body.

        Returns
        -------
        str
            Contents of the body.
        '''

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

        self._body = value
        if 'Compress' in self._headers:
            self._compress_body()
        self._set_content_length(value)

    @body.deleter
    def body(self):
        '''Deletes the body.

        The aiospamc.headers.ContentLength header will be automatically
        deleted.
        '''

        self._body = ''
        self._compressed_body = None
        self.delete_header('Content-length')

    def _compress_body(self):
        self._compressed_body = zlib.compress(self.body.encode())
        self._set_content_length(self._compressed_body)

    def _decompress_body(self):
        self._compressed_body = None
        self._set_content_length(self.body)

    def _set_content_length(self, body_):
        self.add_header(ContentLength(len(body_)))

    def add_header(self, header):
        '''Adds a header to the request.  A header with the same name will be
        overwritten.

        Parameters
        ----------
        header : aiospamc.headers.Header
            A header object to be added.
        '''

        if header.header_field_name() == 'Compress' and self.body:
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

        if header_name == 'Compress' and self.body:
            self._decompress_body()
        self._headers.pop(header_name)
