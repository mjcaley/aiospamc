#!/usr/bin/env python

'''Connection and ConnectionManager base classes.'''

import asyncio
import logging
from typing import Tuple, Union, SupportsBytes


class Connection:
    '''Base class for connection objects.

    Attributes
    ----------
    connected
        Status on if the connection is established.
    loop
        The asyncio event loop.
    logger
        Logging instance.  Logs to 'aiospamc.connections'.
    '''

    def __init__(self, loop: asyncio.AbstractEventLoop = None):
        '''Connection constructor.

        Parameters
        ----------
        loop
            The asyncio event loop.
        '''

        self.connected = False
        self.loop = loop or asyncio.get_event_loop()
        self.logger = logging.getLogger(__name__)

    async def __aenter__(self):
        self.logger.debug('Connecting to %s', self.connection_string)
        self.reader, self.writer = await self.open()
        self.connected = True
        self.logger.debug('Connected to %s', self.connection_string)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.logger.debug('Closing connection to %s', self.connection_string)
        self.close()
        self.logger.debug('Closed connection to %s', self.connection_string)

    async def open(self) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        '''Connect to a service.

        Raises
        ------
        aiospamc.exceptions.AIOSpamcConnectionFailed
            If connection failed for some reason.
        '''

        raise NotImplementedError

    @property
    def connection_string(self) -> str:
        '''String representation of the connection.'''

        raise NotImplementedError

    def close(self) -> None:
        '''Closes the connection.'''

        self.writer.close()
        self.connected = False
        del self.reader, self.writer

    async def send(self, data: Union[bytes, SupportsBytes]) -> None:
        '''Sends data through the connection.'''

        self.writer.write(data)
        await self.writer.drain()
        self.writer.write_eof()

    async def receive(self) -> bytes:
        '''Receives data from the connection.'''

        return await self.reader.read()


class ConnectionManager:
    '''Stores connection parameters and creates connections.'''

    def __init__(self, loop: asyncio.AbstractEventLoop = None):
        self.loop = loop or asyncio.get_event_loop()

    def new_connection(self) -> Connection:
        '''Creates a connection object.'''

        raise NotImplementedError
