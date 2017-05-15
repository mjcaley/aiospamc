#!/usr/bin/env python

'''Connection and ConnectionManager base classes.'''

import asyncio
import logging


class Connection:
    '''Base class for connection objects.

    Attributes
    ----------
    connected : bool
        Status on if the connection is established.
    loop : asyncio.AbstratEventLoop
        The asyncio event loop.
    logger : logging.Logger
        Logging instance.  Logs to 'aiospamc.connections'
    '''

    def __init__(self, loop=None):
        '''Connection constructor.

        Parameters
        ----------
        loop : asyncio.AbstractEventLoop
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

    async def open(self):
        '''Connect to a service.

        Returns
        -------
        asyncio.StreamReader
            Instance of stream reader.
        asyncio.StreamWriter
            Instance of stream writer.

        Raises
        ------
        aiospamc.exceptions.AIOSpamcConnectionFailed
            If connection failed for some reason.
        '''

        raise NotImplementedError

    @property
    def connection_string(self):
        '''String representation of the connection.

        Returns
        -------
        str
            String of the connection address.
        '''

        raise NotImplementedError

    def close(self):
        '''Closes the connection.'''

        self.writer.close()
        self.connected = False
        del self.reader, self.writer

    async def send(self, data):
        '''Sends data through the connection.

        Parameters
        ----------
        data : bytes
            Data to send.
        '''

        self.writer.write(data)
        await self.writer.drain()

    async def receive(self):
        '''Receives data from the connection.

        Returns
        -------
        bytes
            Data received.
        '''

        return await self.reader.read()


class ConnectionManager:
    '''Stores connection parameters and creates connections.
    
    Attributes
    ----------
    loop : asyncio.AbstratEventLoop
        The asyncio event loop.
    '''

    def __init__(self, loop=None):
        self.loop = loop or asyncio.get_event_loop()

    def new_connection(self):
        '''Creates a connection object.

        Returns
        -------
        Connection
            Instance of a Connection object.
        '''

        raise NotImplementedError
