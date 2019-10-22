#!/usr/bin/env python3

'''Common classes for the project.'''

from typing import Any, Iterator, ItemsView, KeysView, Mapping, ValuesView, SupportsBytes, Union

from .header_values import HeaderValue
from .incremental_parser import parse_header_value


class SpamcBody:
    '''Provides a descriptor for a bytes-like object.'''

    def __get__(self, instance, owner) -> bytes:
        return instance._body

    def __set__(self, instance, value: Union[bytes, SupportsBytes]) -> None:
        instance._body = bytes(value)


class SpamcHeaders:
    '''Provides a dictionary-like interface for headers.'''

    def __init__(self, *, headers: Mapping[str, Union[HeaderValue, str, Any]] = None) -> None:
        self._headers = {}
        if headers:
            for key, value in headers.items():
                self[key] = value

    def __str__(self):
        return '<{} object at {}, keys: {}>'.format(
            '.'.join([self.__class__.__module__, self.__class__.__qualname__]),
            id(self),
            ', '.join(self._headers.keys())
        )

    def __bytes__(self) -> bytes:
        return b''.join(
            [b'%b: %b\r\n' % (name.encode('ascii'), bytes(value)) for name, value in self._headers.items()]
        )

    def __getitem__(self, key: str) -> HeaderValue:
        return self._headers[key]

    def __setitem__(self, key: str, value: Union[HeaderValue, str]) -> None:
        if isinstance(value, HeaderValue):
            self._headers[key] = value
        else:
            self._headers[key] = parse_header_value(key, value)

    def __iter__(self) -> Iterator[str]:
        return iter(self._headers)

    def __len__(self) -> int:
        return len(self._headers)

    def keys(self) -> KeysView[str]:
        return self._headers.keys()

    def items(self) -> ItemsView[str, HeaderValue]:
        return self._headers.items()

    def values(self) -> ValuesView[HeaderValue]:
        return self._headers.values()
