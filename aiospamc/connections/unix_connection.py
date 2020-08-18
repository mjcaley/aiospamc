#!/usr/bin/env python3

'''Unix domain socket connection and manager.'''

import asyncio
from typing import Tuple

from . import Connection
from . import ConnectionManager
from ..exceptions import AIOSpamcConnectionFailed


class UnixConnectionManager(ConnectionManager):
    '''Creates new connections based on Unix domain socket path provided.'''

    def __init__(self, path: str) -> None:
        '''Constructor for UnixConnectionManager.

        :param path: Path of the socket.
        '''

        self.path = path
        super().__init__()

    def __repr__(self) -> str:
        return f'UnixConnectionManager(path={repr(self.path)})'

    def new_connection(self) -> 'UnixConnection':
        '''Creates a new Unix domain socket connection.

        :raises AIOSpamcConnectionFailed:
        '''

        return UnixConnection(self.path)


class UnixConnection(Connection):
    '''Manages a Unix domain socket connection.'''

    def __init__(self, path: str) -> None:
        '''Constructor for UnixConnection.

        :param path: Path of the socket.
        '''

        self.path = path
        super().__init__()

    def __repr__(self) -> str:
        return f'UnixConnection(path={repr(self.path)})'

    async def open(self) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        '''Opens a connection.

        :raises AIOSpamcConnectionFailed:
        '''

        try:
            reader, writer = await asyncio.open_unix_connection(self.path)
        except (ConnectionRefusedError, OSError) as error:
            raised = AIOSpamcConnectionFailed(error)
            self.logger.exception('Exception occurred when connecting: %s', raised)
            raise raised

        return reader, writer

    @property
    def connection_string(self) -> str:
        '''String representation of the connection.'''

        return self.path
