#!/usr/bin/env python3

'''TCP socket connection and manager.'''

import asyncio

from aiospamc.connections import Connection
from aiospamc.connections import ConnectionManager
from aiospamc.exceptions import AIOSpamcConnectionFailed


class TcpConnectionManager(ConnectionManager):
    '''Creates new connections based on host and port provided.

    Attributes
    ----------
    host : str
        Hostname or IP address of server.
    port : str
        Port number.
    ssl : bool
        Whether to use SSL/TLS.
    '''

    def __init__(self, host, port, ssl=False, loop=None):
        '''Constructor for TcpConnectionManager.

        Parameters
        ----------
        host : str
            Hostname or IP address of server.
        port : str
            Port number
        ssl : :obj:`bool` or optional
            SSL/TLS enabled.
        loop : asyncio.AbstractEventLoop
            The asyncio event loop.
        '''

        self.host = host
        self.port = port
        self.ssl = ssl
        super().__init__(loop)

    def __repr__(self):
        return '{}(host={}, port={}, ssl={})'.format(self.__class__.__name__,
                                                     repr(self.host),
                                                     repr(self.port),
                                                     self.ssl)

    def new_connection(self):
        '''Creates a new TCP connection.

        Raises
        ------
        aiospamc.exceptions.AIOSpamcConnectionFailed
        '''

        return TcpConnection(self.host, self.port, self.ssl, self.loop)


class TcpConnection(Connection):
    '''Manages a TCP connection.

    Attributes
    ----------
    host : str
        Hostname or IP address of server.
    port : str
        Port number
    ssl : bool
        Whether to use SSL/TLS.
    loop : asyncio.AbstratEventLoop
        The asyncio event loop.
    '''

    def __init__(self, host, port, ssl, loop=None):
        '''Constructor for TcpConnection.

        Attributes
        ----------
        host : str
            Hostname or IP address of server.
        port : str
            Port number
        ssl :  :obj:`bool` or optional
            SSL/TLS enabled.
        '''

        self.host = host
        self.port = port
        self.ssl = ssl
        super().__init__(loop)

    def __repr__(self):
        return '{}(host={}, port={}, ssl={})'.format(self.__class__.__name__,
                                                     repr(self.host),
                                                     repr(self.port),
                                                     self.ssl)

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
            reader, writer = await asyncio.open_connection(self.host,
                                                           self.port,
                                                           ssl=self.ssl,
                                                           loop=self.loop)
        except (ConnectionRefusedError, OSError) as error:
            raised = AIOSpamcConnectionFailed(error)
            self.logger.exception('Exception occurred when connecting to %s:%s: %s',
                                  self.host,
                                  self.port,
                                  raised)
            raise raised

        return reader, writer

    @property
    def connection_string(self):
        '''String representation of the connection.

        Returns
        -------
        str
            Hostname and port.
        '''

        return ':'.join([self.host, str(self.port)])
