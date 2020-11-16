#!/usr/bin/env python

"""ConnectionManager classes for TCP and Unix sockets."""

import asyncio
from pathlib import Path
import logging
import ssl
from time import monotonic
from typing import Any, Optional, Tuple

import certifi

from .exceptions import AIOSpamcConnectionFailed, ClientTimeoutException


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
        :raises: ClientTimeoutException

        :param data: Data to send.
        """

        start = monotonic()
        try:
            response = await asyncio.wait_for(self._send(data), self.timeout.total)
        except asyncio.TimeoutError as error:
            self.logger.exception(
                "Timed out (total) to %s after %0.2f seconds",
                self.connection_string,
                monotonic() - start,
                exc_info=error,
                stack_info=True,
                extra={"connection_id": id(self)},
            )
            raise ClientTimeoutException from error

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
        except asyncio.TimeoutError as error:
            self.logger.exception(
                "Timed out receiving data from %s after %0.2f seconds",
                self.connection_string,
                monotonic() - start,
                exc_info=error,
                stack_info=True,
                extra={"connection_id": id(self)},
            )
            raise ClientTimeoutException from error

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
        except asyncio.TimeoutError as error:
            self.logger.exception(
                "Timed out connecting to %s after %0.2f seconds",
                self.connection_string,
                monotonic() - start,
                exc_info=error,
                extra={"connection_id": id(self)},
            )
            raise ClientTimeoutException from error

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
        self,
        host: str,
        port: int,
        ssl_context: ssl.SSLContext = None,
        timeout: Timeout = None,
    ) -> None:
        """TcpConnectionManager constructor.

        :param host: Hostname or IP address.
        :param port: TCP port.
        :param ssl_context: SSL context.
        """

        super().__init__(timeout)
        self.host = host
        self.port = port
        self.ssl_context = ssl_context

    async def open(self) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """Opens a TCP connection.

        :raises: AIOSpamcConnectionFailed

        :return: Reader and writer for the connection.
        """

        try:
            reader, writer = await asyncio.open_connection(
                self.host, self.port, ssl=self.ssl_context
            )
        except (ConnectionRefusedError, OSError) as error:
            self.logger.exception(
                "Exception occurred when connecting to %s",
                self.connection_string,
                exc_info=error,
                stack_info=True,
                extra={"connection_id": id(self)},
            )
            raise AIOSpamcConnectionFailed from error

        return reader, writer

    @property
    def connection_string(self) -> str:
        """:return: TCP hostname/IP and port."""

        return ":".join([self.host, str(self.port)])


class UnixConnectionManager(ConnectionManager):
    def __init__(self, path: str, timeout: Timeout = None):
        """UnixConnectionManager constructor.

        :param path: Unix socket path.
        """

        super().__init__(timeout)
        self.path = path

    async def open(self) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """Opens a unix socket path connection.

        :raises: AIOSpamcConnectionFailed

        :return: Reader and writer for the connection.
        """

        try:
            reader, writer = await asyncio.open_unix_connection(self.path)
        except (ConnectionRefusedError, OSError) as error:
            self.logger.exception(
                "Exception occurred when connecting to %s",
                self.connection_string,
                exc_info=error,
                stack_info=True,
                extra={"connection_id": id(self)},
            )
            raise AIOSpamcConnectionFailed from error

        return reader, writer

    @property
    def connection_string(self) -> str:
        """:return: Unix connection path."""

        return self.path


def new_ssl_context(verify: Optional[Any]) -> Optional[ssl.SSLContext]:
    """Creates an SSL context based on the supplied parameter.

    :param verify: Use SSL for the connection.  If True, will use root certificates.
        If False, will not verify the certificate.  If a string to a path or a Path
        object, the connection will use the certificates found there.
    """

    if verify is None:
        return None
    elif verify is True:
        return ssl.create_default_context(cafile=certifi.where())
    elif verify is False:
        context = ssl.create_default_context(cafile=certifi.where())
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context
    else:
        cert_path = Path(verify).absolute()
        if cert_path.is_dir():
            return ssl.create_default_context(capath=str(cert_path))
        elif cert_path.is_file():
            return ssl.create_default_context(cafile=str(cert_path))
        else:
            raise FileNotFoundError(f"Certificate path does not exist at {verify}")


def new_connection(
    host: Optional[str] = None,
    port: Optional[int] = None,
    socket_path: Optional[str] = None,
    timeout: Optional[Timeout] = None,
    context: Optional[ssl.SSLContext] = None,
) -> ConnectionManager:
    if socket_path:
        return UnixConnectionManager(socket_path, timeout=timeout)
    elif host and port:
        return TcpConnectionManager(host, port, context, timeout)
    else:
        raise ValueError('Either "host" and "port" or "socket_path" must be specified.')
