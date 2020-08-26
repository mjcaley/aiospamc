#!/usr/bin/env python

"""ConnectionManager classes for TCP and Unix sockets."""

from .exceptions import AIOSpamcConnectionFailed
import asyncio
import logging
from ssl import SSLContext
from time import monotonic
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
        self._logger = logging.getLogger("aiospamc.connections")

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

        start = monotonic()
        try:
            response = await asyncio.wait_for(self._send(data), self.timeout.total)
        except asyncio.TimeoutError as e:
            self.logger.exception(
                "Timed out (total) to %s after %0.2f seconds",
                self.connection_string,
                monotonic() - start,
                exc_info=e,
                stack_info=True,
                extra={"connection_id": id(self)},
            )
            raise

        end = monotonic()
        self.logger.info(
            "Total response time to %s in %0.2f seconds",
            self.connection_string,
            end - start,
            extra={"connection_id": id(self)},
        )

        return response

    async def _send(self, data: bytes) -> bytes:
        reader, writer = await self._connect()

        writer.write(data)
        if writer.can_write_eof():
            writer.write_eof()
        await writer.drain()

        response = await self._receive(reader)

        writer.close()

        return response

    async def _receive(self, reader: asyncio.StreamReader) -> bytes:
        start = monotonic()
        try:
            response = await asyncio.wait_for(reader.read(), self.timeout.response)
        except asyncio.TimeoutError as e:
            self.logger.exception(
                "Timed out receiving data from %s after %0.2f seconds",
                self.connection_string,
                monotonic() - start,
                exc_info=e,
                stack_info=True,
                extra={"connection_id": id(self)},
            )
            raise

        end = monotonic()
        self.logger.info(
            "Successfully received data from %s in %0.2f seconds",
            self.connection_string,
            end - start,
            extra={"connection_id": id(self)},
        )

        return response

    async def _connect(self) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        start = monotonic()
        try:
            reader, writer = await asyncio.wait_for(
                self.open(), self.timeout.connection
            )
        except asyncio.TimeoutError as e:
            self.logger.exception(
                "Timed out connecting to %s after %0.2f seconds",
                self.connection_string,
                monotonic() - start,
                exc_info=e,
                extra={"connection_id": id(self)},
            )
            raise

        end = monotonic()
        self.logger.info(
            "Successfully connected to %s in %0.2f seconds",
            self.connection_string,
            end - start,
            extra={"connection_id": id(self)},
        )

        return reader, writer

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
                "Exception occurred when connecting to %s",
                self.connection_string,
                exc_info=raised,
                stack_info=True,
                extra={"connection_id": id(self)},
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
            self.logger.exception(
                "Exception occurred when connecting to %s",
                self.connection_string,
                exc_info=raised,
                stack_info=True,
                extra={"connection_id": id(self)},
            )
            raise raised

        return reader, writer

    @property
    def connection_string(self) -> str:
        """:return: Unix connection path."""

        return self.path
