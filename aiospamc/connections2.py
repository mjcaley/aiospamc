#!/usr/bin/env python

'''Connection and ConnectionManager base classes.'''

from aiospamc.exceptions import AIOSpamcConnectionFailed
import asyncio
import logging
from ssl import SSLContext
from typing import Tuple


class ConnectionManager:
    '''Stores connection parameters and creates connections.'''

    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)

    @property
    def logger(self) -> logging.Logger:
        '''Return the logger object.'''

        return self._logger

    async def request(self, data: bytes) -> bytes:
        '''Send bytes data and receive a response.'''

        reader, writer = await self.open()

        writer.write(data)
        await writer.drain()

        response = await reader.read()

        writer.close()

        return response

    async def open(self) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        '''Opens a connection, returning the reader and writer objects.'''

        raise NotImplementedError

    @property
    def connection_string(self) -> str:
        '''String representation of the connection.'''

        raise NotImplementedError


class TcpConnectionManager(ConnectionManager):
    def __init__(self, host: str, port: int, ssl: SSLContext = None) -> None:
        super().__init__()
        self.host = host
        self.port = port
        self.ssl = ssl

    async def open(self) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        try:
            reader, writer = await asyncio.open_connection(self.host,
                                                           self.port,
                                                           ssl=self.ssl)
        except (ConnectionRefusedError, OSError) as error:
            raised = AIOSpamcConnectionFailed(error)
            self.logger.exception('Exception occurred when connecting to %s:%s: %s',
                                  self.host,
                                  self.port,
                                  raised)
            raise raised

        return reader, writer

    @property
    def connection_string(self) -> str:
        '''String representation of the connection.'''

        return ':'.join([self.host, str(self.port)])


class UnixConnectionManager(ConnectionManager):
    def __init__(self, path: str, ssl: SSLContext = None):
        super().__init__()
        self.path = path
        self.ssl = ssl

    async def open(self) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        try:
            reader, writer = await asyncio.open_unix_connection(self.path, ssl=self.ssl)
        except (ConnectionRefusedError, OSError) as error:
            raised = AIOSpamcConnectionFailed(error)
            self.logger.exception('Exception occurred when connecting: %s', raised)
            raise raised

        return reader, writer

    @property
    def connection_string(self) -> str:
        '''Unix connection path.

        :return: str # TODO: Right format?
        '''

        return self.path
