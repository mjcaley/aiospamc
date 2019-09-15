#!/usr/bin/env python3

'''Unix domain socket connection and manager.'''

import asyncio
from typing import Tuple

from . import Connection
from . import ConnectionManager
from ..exceptions import AIOSpamcConnectionFailed


class UnixConnectionManager(ConnectionManager):
    '''Creates new connections based on Unix domain socket path provided.

    Attributes
    ----------
    path
        Path of the socket.
    '''

    def __init__(self, path: str, loop: asyncio.AbstractEventLoop = None) -> None:
        '''Constructor for UnixConnectionManager.

        Parameters
        ----------
        path
            Path of the socket.
        loop
            The asyncio event loop.
        '''

        self.path = path
        super().__init__(loop)

    def __repr__(self) -> str:
        return 'UnixConnectionManager(path={})'.format(repr(self.path))

    def new_connection(self) -> 'UnixConnection':
        '''Creates a new Unix domain socket connection.

        Raises
        ------
        AIOSpamcConnectionFailed
        '''

        return UnixConnection(self.path, self.loop)


class UnixConnection(Connection):
    '''Manages a Unix domain socket connection.

    Attributes
    ----------
    path
        Path of the socket.
    loopAbstractEventLoop
        The asyncio event loop.
    '''

    def __init__(self, path: str, loop: asyncio.AbstractEventLoop = None) -> None:
        '''Constructor for UnixConnection.

        Parameters
        ----------
        path : str
            Path of the socket.
        loop : asyncio.AbstractEventLoop
            The asyncio event loop.
        '''

        self.path = path
        super().__init__(loop)

    def __repr__(self) -> str:
        return 'UnixConnection(path={})'.format(repr(self.path))

    async def open(self) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        '''Opens a connection.

        Raises
        ------
        aiospamc.exceptions.AIOSpamcConnectionFailed
        '''

        try:
            reader, writer = await asyncio.open_unix_connection(self.path,
                                                                loop=self.loop)
        except (ConnectionRefusedError, OSError) as error:
            raised = AIOSpamcConnectionFailed(error)
            self.logger.exception('Exception occurred when connecting: %s', raised)
            raise raised

        return reader, writer

    @property
    def connection_string(self) -> str:
        '''String representation of the connection.'''

        return self.path
