#!/usr/bin/env python

"""ConnectionManager classes for TCP and Unix sockets."""

from .exceptions import AIOSpamcConnectionFailed
import asyncio
import logging
from ssl import SSLContext
from typing import Tuple


class Timeout:
    """Container object for defining timeouts."""

    def __init__(
        self, total: float = 600, connection: float = None, response: float = None
    ) -> None:
        """Timeout constructor.

        :param total: The total length of time in seconds to set the timeout.
        :param connection: The length of time in seconds to allow for a connection to live before timing out.
        :param response: The length of time in seconds to allow for a response from the server before timing out.
        """

        self.total = total
        self.connection = connection
        self.response = response

    def __repr__(self):
        return (
            f"{self.__class__.__qualname__}("
            f"total={self.total}, "
            f"connection={self.connection}, "
            f"response={self.response}"
            ")"
        )


class ConnectionManager:
    """Stores connection parameters and creates connections."""

    def __init__(self, timeout: Timeout = None) -> None:
        self.timeout = timeout or Timeout()
        self._logger = logging.getLogger(__name__)

    @property
    def logger(self) -> logging.Logger:
        """Return the logger object."""

        return self._logger

    async def request(self, data: bytes) -> bytes:
        """Send bytes data and receive a response.

        :raises: AIOSpamcConnectionFailed
        :raises: asyncio.TimeoutError

        :param data: Data to send.
        """

        response = await asyncio.wait_for(self._send(data), self.timeout.total)

        return response

    async def _send(self, data: bytes) -> bytes:
        reader, writer = await self._connect()

        writer.write(data)
        await writer.drain()

        response = await self._receive(reader)

        writer.close()

        return response

    async def _receive(self, reader: asyncio.StreamReader) -> bytes:
        response = await asyncio.wait_for(reader.read(), self.timeout.response)

        return response

    async def _connect(self) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        return await asyncio.wait_for(self.open(), self.timeout.connection)

    async def open(self) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """Opens a connection, returning the reader and writer objects."""

        raise NotImplementedError

    @property
    def connection_string(self) -> str:
        """String representation of the connection."""

        raise NotImplementedError


class TcpConnectionManager(ConnectionManager):
    def __init__(
        self, host: str, port: int, ssl: SSLContext = None, *args, **kwargs
    ) -> None:
        """TcpConnectionManager constructor.

        :param host: Hostname or IP address.
        :param port: TCP port.
        :param ssl: SSL context.
        """

        super().__init__(*args, **kwargs)
        self.host = host
        self.port = port
        self.ssl = ssl

    async def open(self) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """Opens a TCP connection.

        :raises: AIOSpamcConnectionFailed

        :return: Reader and writer for the connection.
        """

        try:
            reader, writer = await asyncio.open_connection(
                self.host, self.port, ssl=self.ssl
            )
        except (ConnectionRefusedError, OSError) as error:
            raised = AIOSpamcConnectionFailed(error)
            self.logger.exception(
                "Exception occurred when connecting to %s:%s: %s",
                self.host,
                self.port,
                raised,
            )
            raise raised

        return reader, writer

    @property
    def connection_string(self) -> str:
        """:return: TCP hostname/IP and port."""

        return ":".join([self.host, str(self.port)])


class UnixConnectionManager(ConnectionManager):
    def __init__(self, path: str, *args, **kwargs):
        """UnixConnectionManager constructor.

        :param path: Unix socket path.
        """

        super().__init__(*args, **kwargs)
        self.path = path

    async def open(self) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """Opens a unix socket path connection.

        :raises: AIOSpamcConnectionFailed

        :return: Reader and writer for the connection.
        """

        try:
            reader, writer = await asyncio.open_unix_connection(self.path)
        except (ConnectionRefusedError, OSError) as error:
            raised = AIOSpamcConnectionFailed(error)
            self.logger.exception("Exception occurred when connecting: %s", raised)
            raise raised

        return reader, writer

    @property
    def connection_string(self) -> str:
        """:return: Unix connection path."""

        return self.path
