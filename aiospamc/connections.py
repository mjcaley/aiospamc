#!/usr/bin/env python

"""ConnectionManager classes for TCP and Unix sockets."""

from __future__ import annotations
import asyncio
from contextlib import asynccontextmanager
from functools import wraps
from pathlib import Path
import ssl
from ssl import SSLContext
from typing import Any, Optional, Tuple

import certifi
import loguru
from loguru import logger
import sniffio

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

    def __init__(self, connection_string: str, timeout: Timeout = None) -> None:
        """ConnectionManager constructor.

        :param timeout: Timeout configuration
        """

        self._connection_string = connection_string
        self.timeout = timeout or Timeout()
        self._logger = logger.bind(
            connection_string=self.connection_string,
            timeout=self.timeout,
        )

    @property
    def logger(self) -> loguru.Logger:
        """Return the logger object."""

        return self._logger

    async def request(self, data: bytes) -> bytes:
        """Send bytes data and receive a response.

        :raises: AIOSpamcConnectionFailed
        :raises: ClientTimeoutException

        :param data: Data to send.
        """

        try:
            response = await asyncio.wait_for(self._send(data), self.timeout.total)
        except asyncio.TimeoutError as error:
            self.logger.exception("Total timeout reached")
            raise ClientTimeoutException from error

        return response

    async def _send(self, data: bytes) -> bytes:
        """Opens a connection, sends data to the writer, waits for the reader, then returns the response.

        :param data: Data to send.

        :return: Byte data from the response.
        """

        reader, writer = await self._connect()

        writer.write(data)
        if writer.can_write_eof():
            writer.write_eof()
        await writer.drain()

        response = await self._receive(reader)

        writer.close()
        await writer.wait_closed()

        return response

    async def _receive(self, reader: asyncio.StreamReader) -> bytes:
        """Takes a reader and returns the response.

        :param reader: asyncio reader.

        :return: Byte data from the response.
        """

        try:
            response = await asyncio.wait_for(reader.read(), self.timeout.response)
        except asyncio.TimeoutError as error:
            self.logger.exception("Timed out receiving data")
            raise ClientTimeoutException from error

        self.logger.success("Successfully received data")

        return response

    async def _connect(self) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """Opens a connection from the connection manager.

        :return: Tuple or asyncio reader and writer.
        """

        try:
            reader, writer = await asyncio.wait_for(
                self.open(), self.timeout.connection
            )
        except asyncio.TimeoutError as error:
            self.logger.exception("Timeout when connecting")
            raise ClientTimeoutException from error

        self.logger.success("Successfully connected")

        return reader, writer

    async def open(self) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """Opens a connection, returning the reader and writer objects."""

        raise NotImplementedError

    @property
    def connection_string(self) -> str:
        """String representation of the connection."""

        return self._connection_string


class TcpConnectionManager(ConnectionManager):
    """Connection manager for TCP connections."""

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
        :param timeout: Timeout configuration.
        """

        super().__init__(f"{host}:{port}", timeout)
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
            self.logger.exception("Exception occurred when connecting")
            raise AIOSpamcConnectionFailed from error

        return reader, writer


class UnixConnectionManager(ConnectionManager):
    """Connection manager for Unix pipes."""

    def __init__(self, path: str, timeout: Timeout = None):
        """UnixConnectionManager constructor.

        :param path: Unix socket path.
        :param timeout: Timeout configuration
        """

        super().__init__(path, timeout)
        self.path = path

    async def open(self) -> Tuple[asyncio.StreamReader, asyncio.StreamWriter]:
        """Opens a unix socket path connection.

        :raises: AIOSpamcConnectionFailed

        :return: Reader and writer for the connection.
        """

        try:
            reader, writer = await asyncio.open_unix_connection(self.path)
        except (ConnectionRefusedError, OSError) as error:
            self.logger.exception("Exception occurred when connecting")
            raise AIOSpamcConnectionFailed from error

        return reader, writer


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


def new_connection_manager(
    host: Optional[str] = None,
    port: Optional[int] = None,
    socket_path: Optional[str] = None,
    timeout: Optional[Timeout] = None,
    context: Optional[ssl.SSLContext] = None,
) -> ConnectionManager:
    """Create a new connection manager.

    :param host: TCP hostname.
    :param port: TCP port number.
    :param socket_path: Unix socket path.
    :param timeout: Timeout configuration.
    :param context: SSL context configuration.
    """

    if socket_path:
        return UnixConnectionManager(socket_path, timeout=timeout)
    elif host and port:
        return TcpConnectionManager(host, port, context, timeout)
    else:
        raise ValueError('Either "host" and "port" or "socket_path" must be specified.')


async def _asyncio_send(connect_future: asyncio.Coroutine, data: bytes, context_logger: Any) -> bytes:
    context_logger(f"Connecting to host")
    reader, writer = await connect_future
    context_logger.success(f"Successfully connected to host")

    writer.write(data)
    if writer.can_write_eof():
        writer.write_eof()
    await writer.drain()

    received = await reader.read()

    writer.close()
    await writer.wait_closed()

    return received


async def asyncio_send_tcp(host: str, port: int, data: bytes, ssl_context: SSLContext = None, timeout: float = None) -> bytes:
    import asyncio

    context_logger = logger.bind(host=host, port=port, data=data)
    connect_future = asyncio.open_connection(host, port, ssl=ssl_context)
    received = await asyncio.wait_for(_asyncio_send(connect_future, data, context_logger))

    return received


async def asyncio_send_socket(socket_path: str, data: bytes, timeout: float = None) -> bytes:
    import asyncio

    context_logger = logger.bind(socket_path=socket_path, data=data)
    connect_future = asyncio.open_unix_connection(socket_path)
    received = await asyncio.wait_for(_asyncio_send(connect_future, data, context_logger), timeout)

    return received


async def _trio_send(stream, data: bytes):
    await stream.send_all(data)


async def _trio_receive(stream) -> bytes:
    received = b""
    async for data in stream:
        received += data

    return received


async def trio_send_tcp(host: str, port: int, data: bytes, ssl_context: SSLContext = None, timeout: float = None) -> bytes:
    import trio

    if ssl_context:
        connection = await trio.open_tcp_stream(host, port) # raises OSError
    else:
        connection = await trio.open_ssl_over_tcp_stream(host, port, ssl_context=ssl_context)
    await connection.send_all(data)
    received = await _trio_receive(connection)



async def trio_send_socket(socket_path: str, data: bytes, timeout: float) -> bytes:
    import trio

    await trio.open_unix_socket(socket_path)


async def _curio_send(connect_future, data: bytes, context_logger) -> bytes:
    context_logger.info("Connecting to host")
    socket = await connect_future
    context_logger.success("Successfully connected to host")
    # TODO: More logging
    async with socket:
        await socket.sendall(data)
        chunks = []
        while True:
            chunk = await socket.recv() # TODO: does it take a parameter?
            if not chunk:
                break
            chunks.append(chunk)

    return b"".join(chunks)


async def curio_send_tcp(host: str, port: int, data: bytes, ssl_context: SSLContext = None, timeout: float = None) -> bytes:
    import curio

    context_logger = logger.bind(host=host, port=port, data=data)
    connect_future = curio.open_connection(host, port, ssl=ssl_context)
    async with curio.timeout_after(timeout):
        received = await _curio_send(connect_future, data, context_logger)

    return received


async def curio_send_socket(socket_path: str, data: bytes, timeout: float) -> bytes:
    import curio

    context_logger = logger.bind(socket_path=socket_path, data=data)
    connect_future = curio.open_unix_connection(socket_path)
    async with curio.timeout_after(timeout):
        received = await _curio_send(connect_future, data, context_logger)

    return received


async def send_tcp(host: str, port: int, data: bytes, ssl_context: SSLContext = None, timeout: float = None) -> bytes:
    library = sniffio.current_async_library()
    if library == "asyncio":
        return await asyncio_send_tcp(host, port, data, ssl_context, timeout)
    elif library == "trio":
        return await trio_send_tcp(host, port, data, ssl_context, timeout)
    elif library == "curio":
        return await curio_send_tcp(host, port, data, ssl_context, timeout)
    else:
        raise ValueError("Asynchronous library not supported")


async def send_socket(socket_path: str, data: bytes, timeout: float = None) -> bytes:
    library = sniffio.current_async_library()
    if library == "asyncio":
        return await asyncio_send_socket(socket_path, data, timeout)
    elif library == "trio":
        return await trio_send_socket(socket_path, data, timeout)
    elif library == "curio":
        return await curio_send_socket(socket_path, data, timeout)
    else:
        raise ValueError("Asynchronous library not supported")
