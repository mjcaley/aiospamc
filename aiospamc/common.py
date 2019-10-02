#!/usr/bin/env python3

'''Common classes for the project.'''

from typing import Iterator, ItemsView, KeysView, Mapping, ValuesView, SupportsBytes, Union

from .header_values import HeaderValue, parse_header


class SpamcBody:
    '''Provides a descriptor for a bytes-like object.'''

    def __get__(self, instance, owner) -> bytes:
        return instance._body

    def __set__(self, instance, value: Union[bytes, SupportsBytes]) -> None:
        instance._body = bytes(value)


class SpamcHeaders:
    '''Provides a dictionary-like interface for headers.'''

    def __init__(self, *, headers: Mapping[str, Union[HeaderValue, str]] = None, **_) -> None:
        if headers:
            self._headers = {
                key: value if isinstance(value, HeaderValue)
                else parse_header(key, value)
                for key, value in headers.items()
            }
        else:
            self._headers = {}

    def __bytes__(self) -> bytes:
        return b'\r\n'.join(
            [b': '.join([name.encode('ascii'), bytes(value)]) for name, value in self._headers.items()]
        )

    def __getitem__(self, key: str) -> HeaderValue:
        return self._headers[key]

    def __setitem__(self, key: str, value: Union[HeaderValue, str]) -> None:
        if isinstance(value, HeaderValue):
            self._headers[key] = value
        else:
            self._headers[key] = parse_header(key, value)

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
