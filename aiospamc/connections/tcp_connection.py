#!/usr/bin/env python3

'''TCP socket connection and manager.'''

import asyncio
from ssl import SSLContext
from typing import Tuple

from . import Connection
from . import ConnectionManager
from ..exceptions import AIOSpamcConnectionFailed


class TcpConnectionManager(ConnectionManager):
    '''Creates new connections based on host and port provided.'''

    def __init__(self, host: str, port: int, ssl: SSLContext = None) -> None:
        '''Constructor for TcpConnectionManager.

        :param host: Hostname or IP address of server.
        :param port: Port number
        :param ssl: SSL/TLS context.
        '''

        self.host = host
        self.port = port
        self.ssl = ssl
        super().__init__()

    def __repr__(self) -> str:
        return '{}(host={}, port={}, ssl={})'.format(self.__class__.__name__,
                                                     repr(self.host),
                                                     repr(self.port),
                                                     self.ssl)

    def new_connection(self) -> 'TcpConnection':
        '''Creates a new TCP connection.

        :raises AIOSpamcConnectionFailed:
        '''

        return TcpConnection(self.host, self.port, self.ssl)


class TcpConnection(Connection):
    '''Manages a TCP connection.'''

    def __init__(self, host: str, port: int, ssl: SSLContext = None):
        '''Constructor for TcpConnection.

        :param host: Hostname or IP address of server.
        :param port: Port number
        :param ssl: SSL/TLS context.
        '''

        self.host = host
        self.port = port
        self.ssl = ssl
        super().__init__()

    def __repr__(self) -> str:
        return '{}(host={}, port={}, ssl={})'.format(self.__class__.__name__,
                                                     repr(self.host),
                                                     repr(self.port),
                                                     self.ssl)

    async def open(self) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        '''Opens a connection.

        :raises AIOSpamcConnectionFailed:
        '''

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
