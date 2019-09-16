#!/usr/bin/env python3

'''Common classes for the project.'''

from collections.abc import Mapping
from typing import Iterator, ItemsView, KeysView, ValuesView, SupportsBytes, Union

from .headers import Header


class SpamcBody:
    '''Provides a descriptor for a bytes-like object.'''

    def __get__(self, instance, owner) -> bytes:
        return instance._body

    def __set__(self, instance, value: Union[bytes, SupportsBytes]) -> None:
        instance._body = bytes(value)


class SpamcHeaders(Mapping):
    '''Provides a dictionary-like interface for headers.'''

    def __init__(self, *, headers: Iterator[Header] = None, **_) -> None:
        if headers:
            self._headers = {value.field_name(): value for value in headers}
        else:
            self._headers = {}

    def __bytes__(self) -> bytes:
        return b''.join([bytes(header) for header in self._headers.values()])

    def __getitem__(self, key: str) -> Header:
        return self._headers[key]

    def __setitem__(self, key: str, value: Header) -> None:
        self._headers[key] = value

    def __iter__(self) -> Iterator[str]:
        return iter(self._headers)

    def __len__(self) -> int:
        return len(self._headers)

    def keys(self) -> KeysView[str]:
        return self._headers.keys()

    def items(self) -> ItemsView[str, Header]:
        return self._headers.items()

    def values(self) -> ValuesView[Header]:
        return self._headers.values()
