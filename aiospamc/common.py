#!/usr/bin/env python3

'''Common classes for the project.'''

from collections.abc import Mapping
try:
    from collections.abc import Collection
except ImportError:
    from collections.abc import Sequence as Collection
from typing import Optional, SupportsBytes, Union
import zlib

from aiospamc.headers import ContentLength


class RequestResponseBase:
    '''Base class for requests and responses.'''

    def __init__(self, body=None, headers=None):
        '''
        Parameters
        ----------
        body : :obj:`str`, optional
            String representation of the body.  An instance of the
            aiospamc.headers.ContentLength will be automatically added.
        headers : tuple of :class:`aiospamc.headers.Header`, optional
            Collection of headers to be added.  If it contains an instance of
            aiospamc.headers.Compress then the body is automatically
            compressed.
        '''

        if headers:
            self._headers = {item.field_name(): item for item in headers}
        else:
            self._headers = {}
        self._body = ''
        self._compressed_body = None
        if body:
            if isinstance(body, str):
                self.body = body
            elif isinstance(body, bytes):
                self.body = self._decode_body(body, self._headers.values())

    @staticmethod
    def _decode_body(body, headers):
        '''Parses a body of a response.

        Parameters
        ----------
        body : bytes
            Bytes representation of body.
        headers : :obj:`tuple` or :obj:`list` of :class:`aiospamc.headers.Header`
            Collection of headers.

        Returns
        -------
        str
            Body in a string object.
        '''

        if not body:
            return None
        elif any(header.field_name() == 'Compress' for header in headers):
            return zlib.decompress(body).decode()
        else:
            return body.decode()

    @property
    def body(self):
        '''Contains the contents of the body.

        The getter will return a bytes object.

        The setter expects a string.  If the :class:`aiospamc.headers.Compress`
        header is present then the value of body will be compressed.

        The deleter will automatically remove the
        :class:`aiospamc.headers.ContentLength` header.
        '''

        return self._body

    @body.setter
    def body(self, value):
        self._body = value
        if 'Compress' in self._headers:
            self._compress_body()
        else:
            self._set_content_length(value)

    @body.deleter
    def body(self):
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
        if isinstance(body_, str):
            self.add_header(ContentLength(len(body_.encode())))
        elif isinstance(body_, bytes):
            self.add_header(ContentLength(len(body_)))

    def add_header(self, header):
        '''Adds a header to the request.  A header with the same name will be
        overwritten.

        Parameters
        ----------
        header : :class:`aiospamc.headers.Header`
            A header object to be added.
        '''

        if header.field_name() == 'Compress' and self.body:
            self._compress_body()
        self._headers[header.field_name()] = header

    def get_header(self, header_name):
        '''Gets the header matching the name.

        Parameters
        ----------
        header_name : :obj:`str`
            String name of the header.

        Returns
        -------
        :class:`aiospamc.headers.Header`
            A Header object or subclass of it.

        Raises
        ------
        :class:`KeyError`
        '''

        return self._headers[header_name]

    def delete_header(self, header_name):
        '''Deletes the header from the request.

        Parameters
        ----------
        header_name : :obj:`str`
            String name of the header.

        Raises
        ------
        :class:`KeyError`
        '''

        if header_name == 'Compress' and self.body:
            self._decompress_body()
        self._headers.pop(header_name)


class SpamcBody:
    def __init__(self, *, body: Union[bytes, SupportsBytes] = None, **_):
        '''
        Provides an interface for the body of a message.

        Attributes
        ----------
        body
            A bytes-like object.
        '''

        if body:
            self._body = body
        else:
            self._body = b''

    def __bytes__(self):
        return self.body

    @property
    def body(self) -> bytes:
        return bytes(self._body)

    @body.setter
    def body(self, value):
        self._body = value


class SpamcHeaders(Mapping):
    '''
    Provides a dictionary-like interface for headers.
    '''

    def __init__(self, *, headers: Optional[Collection] = None, **_):
        if headers:
            self._headers = {value.field_name(): value for value in headers}
        else:
            self._headers = {}

    def __bytes__(self):
        return b''.join([bytes(header) for header in self._headers.values()])

    def __getitem__(self, key):
        return self._headers[key]

    def __setitem__(self, key, value):
        self._headers[key] = value

    def __iter__(self):
        return iter(self._headers)

    def __len__(self):
        return len(self._headers)

    def keys(self):
        return self._headers.keys()

    def items(self):
        return self._headers.items()

    def values(self):
        return self._headers.values()
