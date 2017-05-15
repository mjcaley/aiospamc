#!/usr/bin/env python3

'''Unix domain socket connection and manager.'''

import asyncio

from aiospamc.connections import Connection
from aiospamc.connections import ConnectionManager
from aiospamc.exceptions import AIOSpamcConnectionFailed


class UnixConnectionManager(ConnectionManager):
    '''Creates new connections based on Unix domain socket path provided.

    Attributes
    ----------
    path : str
        Path of the socket.
    '''

    def __init__(self, path, loop=None):
        '''Constructor for UnixConnectionManager.

        Parameters
        ----------
        path : str
            Path of the socket.
        loop : asyncio.AbstractEventLoop
            The asyncio event loop.
        '''

        self.path = path
        super().__init__(loop)

    def __repr__(self):
        return 'UnixConnectionManager(path={})'.format(repr(self.path))

    def new_connection(self):
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
    path : str
        Path of the socket.
    loop : asyncio.AbstractEventLoop
        The asyncio event loop.
    '''

    def __init__(self, path, loop=None):
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

    def __repr__(self):
        return 'UnixConnection(path={})'.format(repr(self.path))

    async def open(self):
        '''Opens a connection.

        Returns
        -------
        asyncio.StreamReader
        asyncio.StreamWriter

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
    def connection_string(self):
        '''String representation of the connection.

        Returns
        -------
        str
            Path to the Unix domain socket.
        '''

        return self.path
